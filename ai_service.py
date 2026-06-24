"""
Módulo wrapper para Google Generative AI.
Importação lazy para evitar erro de protobuf em Python 3.14+
"""
import os
import re

_genai = None
_import_error = None

def _init_genai():
    """Inicializa google.generativeai apenas quando necessário"""
    global _genai, _import_error

    if _genai is None and _import_error is None:
        try:
            import google.generativeai as genai
            _genai = genai
        except Exception as e:
            _import_error = e
            print(f"Aviso: Google Generative AI não disponível: {e}")

    if _import_error:
        raise _import_error

    return _genai

def summarize_text(text, max_tokens=800):
    """
    Sumariza texto usando Google Generative AI.
    Retorna um resumo local simples se a IA não estiver disponível.
    """
    if not text:
        return None

    try:
        genai = _init_genai()
        api_key = os.getenv('GOOGLE_API_KEY')

        if not api_key:
            raise RuntimeError('GOOGLE_API_KEY não configurada')

        genai.configure(api_key=api_key)

        for model_name in ('gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro'):
            try:
                model = genai.GenerativeModel(model_name)
                break
            except Exception:
                model = genai.GenerativeModel('gemini-pro')

        prompt = f"""Você é um editor especializado em resumos de vídeos. Analise a transcrição abaixo e produza um resumo em português do Brasil, claro e bem organizado.

Use EXATAMENTE esta estrutura:

## Visão geral
(2-3 frases sobre o tema central do vídeo)

## Pontos principais
- (bullet 1)
- (bullet 2)
- (bullet 3)
- (até 6 bullets no total)

## Conclusão
(1-2 frases com a mensagem final ou takeaway)

Regras:
- Seja objetivo e fiel ao conteúdo
- Não invente informações
- Use linguagem natural e profissional
- Ignore repetições e vícios de fala

Transcrição:
{text}"""

        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=max_tokens,
                temperature=0.35,
            )
        )

        summary = (response.text or '').strip()
        return summary if summary else _local_summary(text)
    except Exception as e:
        print(f"Erro ao resumir com IA: {e}")
        return _local_summary(text)


def _local_summary(text, max_sentences=6):
    """Resumo simples local quando a IA não está disponível."""
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text.replace('\n', ' ')) if s.strip()]
    if not sentences:
        return None

    ranked = sorted(sentences, key=lambda s: -len(s))
    chosen = ranked[:max_sentences]
    chosen.sort(key=lambda s: text.find(s))

    body = '\n'.join(f'- {s.rstrip(".")}' for s in chosen[:4])
    overview = chosen[0] if chosen else ''
    conclusion = chosen[-1] if len(chosen) > 1 else overview

    return (
        "## Visão geral\n"
        f"{overview}\n\n"
        "## Pontos principais\n"
        f"{body}\n\n"
        "## Conclusão\n"
        f"{conclusion}"
    )


def is_genai_available():
    """Verifica se Google Generative AI está disponível"""
    try:
        _init_genai()
        return bool(os.getenv('GOOGLE_API_KEY'))
    except Exception:
        return False
