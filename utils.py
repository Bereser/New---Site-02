import os
import re
import json
import time
import requests
import xml.etree.ElementTree as ET
import urllib.parse
from flask import current_app
from youtube_transcript_api import YouTubeTranscriptApi
from ai_service import summarize_text as summarize_with_genai, is_genai_available

import sys
import shutil
import tempfile
import subprocess

_youtube_rate_limited = False
_last_transcript_error = None


def _set_transcript_error(message):
    global _last_transcript_error
    _last_transcript_error = message


def get_transcript_error():
    return _last_transcript_error


def _mark_rate_limited():
    global _youtube_rate_limited
    _youtube_rate_limited = True


def _reset_rate_limit_flag():
    global _youtube_rate_limited, _last_transcript_error
    _youtube_rate_limited = False
    _last_transcript_error = None
def is_valid_youtube_url(url):
    """Validar se é uma URL válida do YouTube"""
    patterns = [
        r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=[\w-]+',
        r'(?:https?://)?(?:www\.)?youtu\.be/[\w-]+',
        r'(?:https?://)?(?:www\.)?youtube\.com/playlist\?list=[\w-]+'
    ]
    return any(re.match(pattern, url) for pattern in patterns)

def extract_video_id(url):
    """Extrair ID do vídeo da URL do YouTube"""
    patterns = [
        r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([\w-]+)',
        r'(?:https?://)?(?:www\.)?youtu\.be/([\w-]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None

def get_video_info(url):
    """Obter informações do vídeo usando yt-dlp com fallback"""
    try:
        import yt_dlp
        
        ydl_opts = {
            'quiet': False,
            'no_warnings': False,
            'socket_timeout': 30,
            'format': 'best',
            'no_color': True,
            'youtube_include_dash_manifest': False  # Evitar erros com DASH
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            return {
                'title': info.get('title'),
                'duration': info.get('duration'),  # em segundos
                'thumbnail': info.get('thumbnail'),
                'video_id': info.get('id'),
                'channel': info.get('uploader')
            }
    
    except Exception as e:
        error_msg = f"{type(e).__name__}: {str(e)}"
        print(f"❌ Erro ao obter info do vídeo: {error_msg}")
        
        # Fallback: tentar extrair informações básicas da URL
        try:
            video_id = extract_video_id(url)
            if video_id:
                # Usar valores padrão para fallback
                return {
                    'title': f'Vídeo {video_id}',
                    'duration': 600,  # 10 minutos padrão
                    'thumbnail': f'https://img.youtube.com/vi/{video_id}/maxresdefault.jpg',
                    'video_id': video_id,
                    'channel': 'Desconhecido'
                }
        except:
            pass
        
        return None

def normalize_transcript_text(text, preserve_line_breaks=True):
    """Limpar e normalizar texto de transcrição."""
    if not text:
        return None

    text = text.replace('\r', '')
    text = text.replace('\t', ' ')

    if preserve_line_breaks:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        normalized = '\n'.join(lines)
    else:
        normalized = re.sub(r'\s+', ' ', text).strip()

    normalized = re.sub(r'\s*([.,;:?!)])', r'\1', normalized)
    normalized = re.sub(r'([.,;:?()])\s*', r'\1 ', normalized)
    normalized = re.sub(r'\s+', ' ', normalized) if not preserve_line_breaks else normalized
    return normalized.strip()


def _fetch_url_text(url, headers=None, timeout=15, retries=3, session=None):
    if not url:
        return None
    default_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
    }
    if headers:
        default_headers.update(headers)

    http = session or requests
    get = http.get if session else requests.get

    for attempt in range(1, retries + 1):
        try:
            proxies = None
            try:
                proxy = current_app.config.get('YT_PROXY')
                if proxy:
                    proxies = {'http': proxy, 'https': proxy}
            except RuntimeError:
                proxies = None

            response = get(url, headers=default_headers, timeout=timeout, proxies=proxies)
            if response.status_code == 200:
                return response.text
            if response.status_code == 429 and attempt < retries:
                _mark_rate_limited()
                wait = attempt * 2
                print(f"_fetch_url_text: 429 Too Many Requests, retry {attempt}/{retries} in {wait}s")
                time.sleep(wait)
                continue
            print(f"_fetch_url_text: HTTP {response.status_code} for {url}")
            return None
        except requests.RequestException as e:
            print(f"_fetch_url_text: request error {type(e).__name__}: {e}")
            if attempt < retries:
                time.sleep(attempt * 2)
                continue
            return None
    return None


def _parse_transcript_json3(raw_text):
    if not raw_text:
        return None
    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError:
        return None

    transcript = []
    for event in data.get('events', []):
        if not event:
            continue
        parts = []
        for segment in event.get('segs') or []:
            text = (segment.get('utf8') or '').strip()
            if text and text != '\n':
                parts.append(text)
        if parts:
            start = event.get('tStartMs', 0) / 1000.0
            transcript.append({'text': ' '.join(parts), 'start': start, 'duration': 3.0})
    return transcript if transcript else None


def _parse_caption_response(raw_text):
    if not raw_text:
        return None
    parsed = _parse_transcript_json3(raw_text)
    if parsed:
        return parsed
    parsed = _parse_transcript_xml(raw_text)
    if parsed:
        return parsed

    lines = []
    for line in raw_text.splitlines():
        line = line.strip()
        if not line or '-->' in line or line.isdigit() or line.upper().startswith('WEBVTT'):
            continue
        lines.append({'text': line})
    return lines if lines else None


def _parse_transcript_xml(raw_text):
    if not raw_text:
        return None
    try:
        root = ET.fromstring(raw_text)
        transcript = []
        for elem in root.findall('.//text'):
            text = ''.join(elem.itertext()).strip()
            if text:
                start = float(elem.get('start', 0) or 0)
                duration = float(elem.get('dur', elem.get('duration', 3)) or 3)
                transcript.append({'text': text, 'start': start, 'duration': duration})
        return transcript if transcript else None
    except ET.ParseError as e:
        print(f"_parse_transcript_xml: ParseError: {e}")
        return None


def _find_ffmpeg_executable():
    """Retorna o caminho do ffmpeg se disponível no PATH ou via imageio_ffmpeg."""
    ffmpeg_path = shutil.which('ffmpeg')
    if ffmpeg_path and os.path.isfile(ffmpeg_path):
        return ffmpeg_path

    try:
        import imageio_ffmpeg
        ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
        if ffmpeg_path and os.path.isfile(ffmpeg_path):
            return ffmpeg_path
    except Exception:
        pass

    return None


def _ensure_ffmpeg_in_path():
    ffmpeg_path = _find_ffmpeg_executable()
    if not ffmpeg_path:
        return False

    ffmpeg_dir = os.path.dirname(ffmpeg_path)
    current_path = os.environ.get('PATH', '')
    if ffmpeg_dir not in current_path.split(os.pathsep):
        os.environ['PATH'] = ffmpeg_dir + os.pathsep + current_path
    return True


def _get_yt_cookies_file():
    """Retorna o caminho do arquivo de cookies do YouTube, se configurado."""
    try:
        cookie_file = current_app.config.get('YT_COOKIES_FILE')
    except RuntimeError:
        cookie_file = None

    if cookie_file and os.path.isfile(cookie_file):
        return cookie_file
    return None


def _download_subtitle_text(url, session=None):
    raw = _fetch_url_text(url, session=session)
    if not raw:
        return None
    return _parse_caption_response(raw)


def _yt_dlp_cli_subtitles(video_url, langs=('pt', 'pt-BR', 'pt-PT', 'en')):
    """Use yt-dlp via CLI to download automatic subtitles (VTT) into a temp dir and return parsed text list.

    Returns a list of {'text': ...} or None.
    """
    tmpdir = None
    try:
        tmpdir = tempfile.mkdtemp(prefix='yt_subs_')
        lang_arg = ','.join(langs)
        out_template = os.path.join(tmpdir, '%(id)s.%(ext)s')
        cmd = [sys.executable, '-m', 'yt_dlp', video_url, '--skip-download', '--write-auto-sub', '--sub-lang', lang_arg, '--sub-format', 'vtt', '-o', out_template]

        cookie_file = _get_yt_cookies_file()
        if cookie_file:
            cmd[1:1] = ['--cookies', cookie_file]

        env = os.environ.copy()
        try:
            proxy = current_app.config.get('YT_PROXY')
            if proxy:
                env['HTTP_PROXY'] = proxy
                env['HTTPS_PROXY'] = proxy
        except RuntimeError:
            pass

        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=120, env=env)
        if proc.returncode != 0:
            cmd2 = [sys.executable, '-m', 'yt_dlp', video_url, '--skip-download', '--write-auto-sub', '--sub-lang', lang_arg, '--sub-format', 'vtt', '--http-headers', 'User-Agent:Mozilla/5.0', '-o', out_template]
            try:
                proc2 = subprocess.run(cmd2, capture_output=True, text=True, timeout=120, env=env)
                if proc2.returncode != 0:
                    return None
            except Exception:
                return None

        files = [os.path.join(tmpdir, fn) for fn in os.listdir(tmpdir) if fn.lower().endswith('.vtt')]
        if not files:
            return None

        files.sort(key=lambda p: os.path.getsize(p), reverse=True)
        path = files[0]
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            raw = f.read()

        lines = []
        block = []
        for ln in raw.splitlines():
            ln = ln.strip()
            if not ln:
                if block:
                    text = ' '.join([l for l in block if '-->' not in l and not l.isdigit() and l != 'WEBVTT'])
                    text = text.strip()
                    if text:
                        lines.append({'text': text})
                    block = []
                continue
            if '-->' in ln or ln.isdigit() or ln.upper().startswith('WEBVTT'):
                block.append(ln)
                continue
            block.append(ln)

        if block:
            text = ' '.join([l for l in block if '-->' not in l and not l.isdigit() and l != 'WEBVTT'])
            text = text.strip()
            if text:
                lines.append({'text': text})

        return lines if lines else None

    except Exception as e:
        print(f"_yt_dlp_cli_subtitles: exception: {repr(e)}")
        return None
    finally:
        if tmpdir and os.path.isdir(tmpdir):
            try:
                for fn in os.listdir(tmpdir):
                    try:
                        os.remove(os.path.join(tmpdir, fn))
                    except Exception:
                        pass
                os.rmdir(tmpdir)
            except Exception:
                pass


def _transcript_data_to_text(transcript_data):
    payload = _build_transcript_payload(transcript_data)
    return payload['text'] if payload else None


def _normalize_segments(transcript_data):
    if not transcript_data:
        return []

    segments = []
    cursor = 0.0
    for item in transcript_data:
        if isinstance(item, dict):
            text = (item.get('text') or '').strip()
            if not text:
                continue
            start = item.get('start')
            if start is None:
                start = cursor
            duration = item.get('duration')
            if duration is None and item.get('end') is not None:
                duration = max(float(item['end']) - float(start), 0.5)
            duration = float(duration or 3.0)
            segments.append({'start': float(start), 'duration': duration, 'text': text})
            cursor = float(start) + duration
        elif isinstance(item, str):
            text = item.strip()
            if text:
                segments.append({'start': cursor, 'duration': 3.0, 'text': text})
                cursor += 3.0
    return segments


def format_timestamp(seconds):
    if seconds is None:
        return '00:00'
    total = max(int(seconds), 0)
    hours = total // 3600
    minutes = (total % 3600) // 60
    secs = total % 60
    if hours:
        return f'{hours:02d}:{minutes:02d}:{secs:02d}'
    return f'{minutes:02d}:{secs:02d}'


def _segments_to_paragraphs(segments, pause_gap=2.5, max_span=45):
    if not segments:
        return []

    paragraphs = []
    current_start = segments[0]['start']
    current_texts = []
    last_end = segments[0]['start']

    for segment in segments:
        start = segment['start']
        text = segment['text'].strip()
        if not text:
            continue
        end = start + segment.get('duration', 3.0)
        if current_texts and (start - last_end > pause_gap or start - current_start > max_span):
            paragraphs.append({
                'start': current_start,
                'time': format_timestamp(current_start),
                'text': ' '.join(current_texts),
            })
            current_start = start
            current_texts = [text]
        else:
            if not current_texts:
                current_start = start
            current_texts.append(text)
        last_end = end

    if current_texts:
        paragraphs.append({
            'start': current_start,
            'time': format_timestamp(current_start),
            'text': ' '.join(current_texts),
        })
    return paragraphs


def _build_transcript_payload(transcript_data):
    segments = _normalize_segments(transcript_data)
    if not segments:
        return None

    paragraphs = _segments_to_paragraphs(segments)
    plain = ' '.join(segment['text'] for segment in segments)
    plain = normalize_transcript_text(plain, preserve_line_breaks=False)
    return {
        'text': plain,
        'segments': segments,
        'paragraphs': paragraphs,
    }


def parse_transcript_segments(stored_segments_json, fallback_text=None):
    if stored_segments_json:
        try:
            data = json.loads(stored_segments_json)
            if isinstance(data, list) and data:
                return data
        except json.JSONDecodeError:
            pass

    if fallback_text:
        lines = [line.strip() for line in fallback_text.splitlines() if line.strip()]
        paragraphs = []
        for line in lines:
            match = re.match(r'^\[([0-9:\.]+)\]\s*(.*)$', line)
            if match:
                paragraphs.append({'time': match.group(1), 'text': match.group(2).strip()})
            else:
                paragraphs.append({'time': None, 'text': line})
        if paragraphs:
            return paragraphs
        return [{'time': None, 'text': fallback_text}]
    return []


def _fetch_transcript_obj(transcript_obj, session=None):
    try:
        return transcript_obj.fetch()
    except Exception as e_fetch:
        safe = repr(e_fetch).encode('ascii', 'backslashreplace').decode('ascii')
        print(f"youtube_transcript_api: fetch falhou ({transcript_obj.language_code}): {type(e_fetch).__name__}: {safe}")
        if '429' in safe or 'Too Many Requests' in safe:
            _mark_rate_limited()

    if hasattr(transcript_obj, '_url'):
        raw = _fetch_url_text(transcript_obj._url, session=session)
        if raw:
            parsed = _parse_caption_response(raw)
            if parsed:
                print("youtube_transcript_api: manual fetch via _url ok")
                return parsed
    return None


def _fetch_via_youtube_transcript_api(video_id, session=None):
    preferred_methods = [
        ('find_generated_transcript', ['pt', 'pt-BR', 'pt-PT']),
        ('find_transcript', ['pt', 'pt-BR', 'pt-PT']),
        ('find_generated_transcript', ['en']),
        ('find_transcript', ['en']),
    ]

    try:
        cookie_file = None
        try:
            cookie_file = current_app.config.get('YT_COOKIES_FILE')
        except RuntimeError:
            pass

        transcripts = YouTubeTranscriptApi.list_transcripts(video_id, cookies=cookie_file)
        print("youtube_transcript_api: list_transcripts ok")
    except Exception as e:
        safe = repr(e).encode('ascii', 'backslashreplace').decode('ascii')
        print(f"youtube_transcript_api: list_transcripts falhou: {type(e).__name__}: {safe}")
        if 'TranscriptsDisabled' in safe or 'Subtitles are disabled' in safe:
            _set_transcript_error('Este video nao possui legendas habilitadas no YouTube.')
        elif 'VideoUnavailable' in safe:
            _set_transcript_error('Video indisponivel ou privado.')
        return None

    candidates = []
    seen = set()
    for method_name, languages in preferred_methods:
        try:
            transcript_obj = getattr(transcripts, method_name)(languages)
            key = (transcript_obj.language_code, transcript_obj.is_generated)
            if key not in seen:
                seen.add(key)
                candidates.append(transcript_obj)
        except Exception:
            pass

    for transcript_obj in transcripts:
        if transcript_obj.is_translatable:
            try:
                translated = transcript_obj.translate('pt')
                key = (translated.language_code, transcript_obj.is_generated, 'translated')
                if key not in seen:
                    seen.add(key)
                    candidates.append(translated)
            except Exception:
                pass

    for transcript_obj in transcripts:
        key = (transcript_obj.language_code, transcript_obj.is_generated)
        if key not in seen:
            seen.add(key)
            candidates.append(transcript_obj)

    for transcript_obj in candidates:
        if _youtube_rate_limited:
            break
        transcript_data = _fetch_transcript_obj(transcript_obj, session=session)
        if transcript_data:
            print(f"youtube_transcript_api: sucesso ({transcript_obj.language_code})")
            return transcript_data

    return None


def _transcribe_with_whisper(url, max_duration=900):
    """Fallback: baixa audio e transcreve com Whisper quando legendas falham."""
    tmpdir = None
    try:
        import whisper
    except ImportError:
        _set_transcript_error('Whisper nao esta instalado. Execute: pip install openai-whisper imageio-ffmpeg')
        print("whisper fallback: pacote nao instalado")
        return None

    try:
        video_info = get_video_info(url)
        duration = (video_info or {}).get('duration') or 0
        if duration > max_duration:
            _set_transcript_error(
                f'Video muito longo para transcricao local ({duration // 60} min). '
                f'Use um video com legendas ou com ate {max_duration // 60} minutos.'
            )
            print(f"whisper fallback: video muito longo ({duration}s)")
            return None

        tmpdir = tempfile.mkdtemp(prefix='yt_whisper_')
        out_path = os.path.join(tmpdir, 'audio.%(ext)s')
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'format': 'bestaudio/best',
            'outtmpl': out_path,
            'noplaylist': True,
        }

        cookie_file = _get_yt_cookies_file()
        if cookie_file:
            ydl_opts['cookiefile'] = cookie_file

        try:
            proxy = current_app.config.get('YT_PROXY')
            if proxy:
                ydl_opts['proxy'] = proxy
        except RuntimeError:
            pass

        import yt_dlp
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        audio_files = [
            os.path.join(tmpdir, fn)
            for fn in os.listdir(tmpdir)
            if os.path.isfile(os.path.join(tmpdir, fn))
        ]
        if not audio_files:
            return None

        audio_path = audio_files[0]
        if not _ensure_ffmpeg_in_path():
            _set_transcript_error(
                'Whisper nao encontrou FFmpeg. Instale ffmpeg no PATH ou garanta que imageio-ffmpeg esteja instalado.'
            )
            print("whisper fallback: ffmpeg nao encontrado")
            return None

        print("whisper fallback: iniciando transcricao local")
        model = whisper.load_model('tiny')
        result = None
        for language in ('pt', None, 'en'):
            attempt = model.transcribe(
                audio_path,
                language=language,
                fp16=False,
                no_speech_threshold=0.35,
                condition_on_previous_text=False,
            )
            text = (attempt or {}).get('text', '').strip()
            if text:
                result = attempt
                break

        text = (result or {}).get('text', '').strip()
        if not text:
            _set_transcript_error(
                'Nao foi possivel detectar fala no audio deste video. '
                'Videos apenas com musica, risadas ou efeitos sonoros nao podem ser transcritos.'
            )
            print("whisper fallback: nenhuma fala detectada no audio")
            return None

        whisper_segments = []
        for seg in (result or {}).get('segments') or []:
            seg_text = (seg.get('text') or '').strip()
            if seg_text:
                whisper_segments.append({
                    'text': seg_text,
                    'start': float(seg.get('start', 0)),
                    'duration': max(float(seg.get('end', 0)) - float(seg.get('start', 0)), 0.5),
                })

        payload = _build_transcript_payload(whisper_segments) if whisper_segments else None
        if payload:
            return payload

        normalized = normalize_transcript_text(text, preserve_line_breaks=False)
        return {
            'text': normalized,
            'segments': whisper_segments,
            'paragraphs': [{'time': '00:00', 'start': 0, 'text': normalized}],
        }
    except Exception as e:
        _set_transcript_error(f'Erro na transcricao local: {e}')
        print(f"whisper fallback: {type(e).__name__}: {e}")
        return None
    finally:
        if tmpdir and os.path.isdir(tmpdir):
            try:
                for fn in os.listdir(tmpdir):
                    try:
                        os.remove(os.path.join(tmpdir, fn))
                    except Exception:
                        pass
                os.rmdir(tmpdir)
            except Exception:
                pass


def _fetch_caption_via_page(video_id, preferred_langs=('pt', 'pt-BR', 'pt-PT', 'en')):
    """Busca legendas carregando a pagina do YouTube e reutilizando a mesma sessao/cookies."""
    try:
        page_url = f'https://www.youtube.com/watch?v={video_id}'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        }

        with requests.Session() as sess:
            sess.trust_env = False
            try:
                proxy = current_app.config.get('YT_PROXY')
                if proxy:
                    sess.proxies.update({'http': proxy, 'https': proxy})
            except RuntimeError:
                pass

            resp = sess.get(page_url, headers=headers, timeout=15)
            if resp.status_code != 200:
                return None

            match = re.search(r'ytInitialPlayerResponse\s*=\s*({.+?});', resp.text, re.DOTALL)
            if not match:
                return None

            try:
                player_response = json.loads(match.group(1))
            except json.JSONDecodeError:
                return None

            tracks = player_response.get('captions', {}).get('playerCaptionsTracklistRenderer', {}).get('captionTracks', [])
            if not tracks:
                return None

            chosen = None
            for lang in preferred_langs:
                for track in tracks:
                    code = track.get('languageCode') or ''
                    if code == lang or code.startswith(lang.split('-')[0]):
                        chosen = track
                        break
                if chosen:
                    break
            if not chosen:
                chosen = tracks[0]

            base_url = chosen.get('baseUrl')
            if not base_url:
                return None

            parsed = urllib.parse.urlparse(base_url)
            qs = urllib.parse.parse_qs(parsed.query)
            variants = []

            def add_variant(query):
                variants.append(urllib.parse.urlunparse(parsed._replace(query=urllib.parse.urlencode(query, doseq=True))))

            add_variant(qs)
            qs_no_ip = {k: v for k, v in qs.items() if k not in ('ip', 'ipbits')}
            add_variant(qs_no_ip)
            qs_json = dict(qs_no_ip)
            qs_json['fmt'] = ['json3']
            add_variant(qs_json)

            chosen_lang = chosen.get('languageCode') or ''
            if chosen_lang and not chosen_lang.startswith('pt'):
                qs_pt = dict(qs_no_ip)
                qs_pt['tlang'] = ['pt']
                add_variant(qs_pt)
                qs_pt_json = dict(qs_pt)
                qs_pt_json['fmt'] = ['json3']
                add_variant(qs_pt_json)

            caption_headers = headers.copy()
            caption_headers.update({
                'Referer': page_url,
                'Accept': 'application/json, text/xml, application/xml, text/plain, */*',
            })

            for variant_url in variants:
                for attempt in range(1, 4):
                    try:
                        caption_resp = sess.get(variant_url, headers=caption_headers, timeout=15)
                    except requests.RequestException:
                        break

                    if caption_resp.status_code == 429 and attempt < 3:
                        _mark_rate_limited()
                        time.sleep(attempt * 2)
                        continue
                    if caption_resp.status_code != 200:
                        break

                    parsed_trans = _parse_caption_response(caption_resp.text)
                    if parsed_trans:
                        return parsed_trans
                    break

    except Exception as e:
        print(f"_fetch_caption_via_page: error {type(e).__name__}: {e}")
    return None


def get_video_transcript(url):
    """Obter transcrição do vídeo do YouTube com múltiplos fallbacks."""
    video_id = extract_video_id(url)
    if not video_id:
        print(f"ERRO: ID do vídeo não extraído de {url}")
        return None

    _reset_rate_limit_flag()
    print(f"Extraindo transcricao para video: {video_id}")
    transcript_data = None

    try:
        page_fallback = _fetch_caption_via_page(video_id)
        if page_fallback:
            transcript_data = page_fallback
            print("_fetch_caption_via_page: sucesso")
        else:
            print("_fetch_caption_via_page: sem legendas")
    except Exception as e:
        print(f"_fetch_caption_via_page: excecao {type(e).__name__}: {e}")

    if not transcript_data and not _youtube_rate_limited:
        transcript_data = _fetch_via_youtube_transcript_api(video_id)

    if not transcript_data and not _youtube_rate_limited:
        print("legendas via pagina/API falharam, tentando fallback yt-dlp")
        try:
            import yt_dlp
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'skip_download': True,
                'writesubtitles': True,
                'writeautomaticsub': True,
                'subtitlesformat': 'vtt',
                'format': 'best',
            }
            cookie_file = _get_yt_cookies_file()
            if cookie_file:
                ydl_opts['cookiefile'] = cookie_file

            try:
                proxy = current_app.config.get('YT_PROXY')
                if proxy:
                    ydl_opts['proxy'] = proxy
            except RuntimeError:
                pass

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)

            if info:
                subtitles = info.get('subtitles') or {}
                auto = info.get('automatic_captions') or {}

                for source in (subtitles, auto):
                    for lang in ['pt', 'pt-BR', 'pt-PT', 'en']:
                        if _youtube_rate_limited or lang not in source:
                            continue
                        sub_info = source[lang]
                        if isinstance(sub_info, list) and sub_info:
                            url_sub = sub_info[0].get('url')
                        elif isinstance(sub_info, dict):
                            url_sub = sub_info.get('url')
                        else:
                            url_sub = None
                        if url_sub:
                            print(f"yt-dlp: found subtitle url for {lang}")
                            transcript_data = _download_subtitle_text(url_sub)
                            if transcript_data:
                                break
                    if transcript_data or _youtube_rate_limited:
                        break
        except Exception as e:
            safe = repr(e).encode('ascii', 'backslashreplace').decode('ascii')
            print(f"fallback yt-dlp falhou: {type(e).__name__}: {safe}")

    if not transcript_data and not _youtube_rate_limited:
        try:
            cli_try = _yt_dlp_cli_subtitles(url)
            if cli_try:
                transcript_data = cli_try
                print("_yt_dlp_cli_subtitles: sucesso")
        except Exception as e:
            print(f"_yt_dlp_cli_subtitles: excecao: {repr(e)}")

    payload = _build_transcript_payload(transcript_data)
    if payload:
        print(f"Transcricao extraida com sucesso. caracteres: {len(payload['text'])}")
        return payload

    if _youtube_rate_limited:
        print("YouTube limitou requisicoes de legendas (429), usando whisper fallback")
    else:
        print("legendas indisponiveis, tentando whisper fallback")
    whisper_result = _transcribe_with_whisper(url)
    if whisper_result:
        print(f"whisper fallback: sucesso. caracteres: {len(whisper_result['text'])}")
        return whisper_result

    if _youtube_rate_limited and not _last_transcript_error:
        _set_transcript_error(
            'YouTube bloqueou temporariamente as legendas (429). '
            'Aguarde alguns minutos e tente novamente.'
        )
    elif not _last_transcript_error:
        _set_transcript_error(
            'Nao foi possivel obter a transcricao deste video. '
            'Verifique se ele possui legendas ou fala clara no audio.'
        )

    print(f"Nenhuma transcricao disponivel para {video_id}")
    return None


def extract_transcript_highlights(text, max_lines=5):
    """Extrai trechos importantes da transcrição usando scoring simples.

    Estratégia: dividir em linhas, computar frequência de palavras (excluindo stopwords),
    pontuar cada linha pela soma das frequências das palavras; selecionar top N
    mantendo a ordem original.
    """
    if not text:
        return None

    # pequenas stopwords em PT/EN
    stopwords = {
        'a','o','e','de','do','da','que','para','por','com','sem','ele','ela','isso',
        'the','and','of','to','in','is','it','that','you','for'
    }

    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if not lines:
        return None

    # tokenizar e contar
    freqs = {}
    for ln in lines:
        for w in re.findall(r"\w+", ln.lower()):
            if w in stopwords or len(w) < 2:
                continue
            freqs[w] = freqs.get(w, 0) + 1

    # score por linha
    scored = []
    for idx, ln in enumerate(lines):
        score = 0
        for w in re.findall(r"\w+", ln.lower()):
            score += freqs.get(w, 0)
        scored.append((idx, score, ln))

    # selecionar top max_lines por score
    scored_sorted = sorted(scored, key=lambda x: (-x[1], x[0]))[:max_lines]
    # ordenar pela posição original
    scored_sorted.sort(key=lambda x: x[0])

    highlights = [item[2] for item in scored_sorted]
    return '\n\n'.join(highlights)

def summarize_text(text, max_length=2000):
    """Gerar resumo usando Google Generative AI"""
    if not text:
        return None
    
    summary = summarize_with_genai(text, max_tokens=max_length)
    return summary if summary else None

def format_duration(seconds):
    """Formatar duração em segundos para formato legível"""
    if not seconds:
        return "N/A"
    
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    if hours > 0:
        return f"{hours}h {minutes}m {secs}s"
    elif minutes > 0:
        return f"{minutes}m {secs}s"
    else:
        return f"{secs}s"

def truncate_text(text, max_length=100):
    """Truncar texto com ellipsis"""
    if len(text) > max_length:
        return text[:max_length] + "..."
    return text
