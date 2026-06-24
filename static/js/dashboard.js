// ==================== FUNÇÕES GLOBAIS ====================

document.querySelectorAll('.close-alert').forEach(btn => {
    btn.addEventListener('click', function() {
        this.closest('.alert').remove();
    });
});

let currentResultData = null;

function formatDuration(seconds) {
    if (!seconds) return 'N/A';

    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;

    if (hours > 0) {
        return `${hours}h ${minutes}m ${secs}s`;
    }
    if (minutes > 0) {
        return `${minutes}m ${secs}s`;
    }
    return `${secs}s`;
}

function renderMarkdownSummary(text) {
    if (!text) return '<p>Não disponível</p>';

    const escaped = text
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');

    return escaped
        .replace(/^## (.+)$/gm, '<h2>$1</h2>')
        .replace(/^- (.+)$/gm, '<li>$1</li>')
        .replace(/(<li>[\s\S]*?<\/li>)/g, (match) => {
            if (match.includes('<ul>')) return match;
            return `<ul>${match}</ul>`;
        })
        .replace(/(<h2>[\s\S]*?<\/h2>)/g, '\n$1\n')
        .replace(/\n{3,}/g, '\n\n')
        .split('\n\n')
        .map(block => {
            block = block.trim();
            if (!block) return '';
            if (block.startsWith('<h2>') || block.startsWith('<ul>')) return block;
            return `<p>${block.replace(/\n/g, '<br>')}</p>`;
        })
        .join('');
}

function renderTranscriptParagraphs(container, paragraphs) {
    container.innerHTML = '';

    if (!paragraphs || paragraphs.length === 0) {
        container.innerHTML = '<p class="empty-copy">Transcrição não disponível.</p>';
        return;
    }

    paragraphs.forEach(item => {
        const block = document.createElement('article');
        block.className = 'transcript-paragraph';

        const time = document.createElement('span');
        time.className = 'transcript-time';
        time.textContent = item.time || '--:--';

        const text = document.createElement('p');
        text.textContent = item.text || '';

        block.appendChild(time);
        block.appendChild(text);
        container.appendChild(block);
    });
}

function transcriptParagraphsToText(paragraphs) {
    if (!paragraphs || !paragraphs.length) return '';
    return paragraphs
        .map(item => `[${item.time || '00:00'}] ${item.text || ''}`.trim())
        .join('\n\n');
}

function setupContentTabs(scope) {
    const tabs = scope.querySelectorAll('.content-tab');
    const panels = scope.querySelectorAll('.content-panel');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const target = tab.dataset.tab;
            tabs.forEach(t => t.classList.remove('active'));
            panels.forEach(p => p.classList.remove('active'));
            tab.classList.add('active');
            scope.querySelector(`#${target === 'summary' ? 'resultSummaryPanel' : 'resultTranscriptPanel'}`)?.classList.add('active');
        });
    });
}

function displayResult(data) {
    currentResultData = data;

    document.getElementById('resultTitle').textContent = data.title;
    document.getElementById('resultDuration').textContent = formatDuration(data.duration);

    const summaryEl = document.getElementById('resultSummary');
    summaryEl.innerHTML = renderMarkdownSummary(data.summary || '');

    renderTranscriptParagraphs(
        document.getElementById('resultTranscript'),
        data.transcript_paragraphs || []
    );

    document.querySelectorAll('#resultBox .content-tab').forEach(tab => tab.classList.remove('active'));
    document.querySelectorAll('#resultBox .content-panel').forEach(panel => panel.classList.remove('active'));
    document.querySelector('#resultBox .content-tab[data-tab="summary"]')?.classList.add('active');
    document.getElementById('resultSummaryPanel')?.classList.add('active');
}

// ==================== DASHBOARD ====================

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('summarizeForm');
    const processingBox = document.getElementById('processingBox');
    const resultBox = document.getElementById('resultBox');
    const submitBtn = document.getElementById('submitBtn');
    const summariesList = document.getElementById('summariesList');
    const modal = document.getElementById('summaryModal');

    if (!form) return;

    setupContentTabs(document.getElementById('resultBox'));

    form.addEventListener('submit', async function(e) {
        e.preventDefault();

        const url = document.getElementById('videoUrl').value.trim();
        if (!url) {
            showAlert('Por favor, insira a URL do vídeo', 'error');
            return;
        }

        form.style.display = 'none';
        processingBox.style.display = 'block';
        resultBox.style.display = 'none';
        submitBtn.disabled = true;

        try {
            const csrfToken = document.querySelector('input[name="csrf_token"]').value;
            const response = await fetch('/api/summarize', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({ url })
            });

            let data = {};
            try {
                data = await response.json();
            } catch (parseError) {
                throw new Error('Resposta inválida do servidor. Tente novamente.');
            }

            if (!response.ok) {
                throw new Error(data.error || 'Erro ao processar vídeo');
            }

            displayResult(data);
            processingBox.style.display = 'none';
            resultBox.style.display = 'block';
            await refreshSummaries();
            document.getElementById('videoUrl').value = 'https://www.youtube.com/watch?v=';
        } catch (error) {
            processingBox.style.display = 'none';
            form.style.display = 'block';
            showAlert(error.message, 'error');
        } finally {
            submitBtn.disabled = false;
        }
    });

    document.getElementById('copyBtn').addEventListener('click', async function() {
        const text = currentResultData?.summary || document.getElementById('resultSummary').textContent;
        await copyToClipboard(text, 'Resumo copiado!');
    });

    document.getElementById('copyTranscriptBtn').addEventListener('click', async function() {
        const text = transcriptParagraphsToText(currentResultData?.transcript_paragraphs || []);
        await copyToClipboard(text || document.getElementById('resultTranscript').textContent, 'Transcrição copiada!');
    });

    document.getElementById('downloadBtn').addEventListener('click', function() {
        const title = document.getElementById('resultTitle').textContent;
        const summary = currentResultData?.summary || '';
        const transcript = transcriptParagraphsToText(currentResultData?.transcript_paragraphs || []);
        const text = `${title}\n\n=== RESUMO ===\n${summary}\n\n=== TRANSCRIÇÃO ===\n${transcript}`;
        const blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `art-resumos_${Date.now()}.txt`;
        a.click();
        window.URL.revokeObjectURL(url);
    });

    document.querySelector('.close-result').addEventListener('click', function() {
        resultBox.style.display = 'none';
        form.style.display = 'block';
    });

    async function refreshSummaries() {
        try {
            const response = await fetch('/api/summaries');
            const summaries = await response.json();

            if (summaries.length === 0) {
                summariesList.innerHTML = `
                    <div class="empty-state">
                        <i class="fas fa-inbox"></i>
                        <p>Nenhum resumo ainda</p>
                        <small>Comece resumindo seu primeiro vídeo</small>
                    </div>
                `;
                return;
            }

            summariesList.innerHTML = summaries.map(summary => `
                <div class="summary-item" data-id="${summary.id}">
                    <div class="summary-header">
                        <h4>${summary.title.substring(0, 50)}</h4>
                        <span class="status status-${summary.status}">${summary.status}</span>
                    </div>
                    <div class="summary-meta">
                        <span><i class="fas fa-calendar"></i> ${summary.created_at}</span>
                        <span><i class="fas fa-clock"></i> ${Math.floor(summary.duration / 60)}m</span>
                    </div>
                    <p class="summary-preview">${summary.summary.substring(0, 100)}...</p>
                    <div class="summary-actions">
                        <a href="#" class="link-view" data-summary-id="${summary.id}">Ver completo</a>
                        <a href="#" class="link-delete" data-summary-id="${summary.id}">Deletar</a>
                    </div>
                </div>
            `).join('');

            addSummaryListeners();
        } catch (error) {
            console.error('Erro ao carregar resumos:', error);
        }
    }

    function addSummaryListeners() {
        document.querySelectorAll('.link-view').forEach(link => {
            link.addEventListener('click', async function(e) {
                e.preventDefault();
                await openSummaryModal(this.dataset.summaryId);
            });
        });

        document.querySelectorAll('.link-delete').forEach(link => {
            link.addEventListener('click', async function(e) {
                e.preventDefault();
                if (!confirm('Tem certeza que deseja deletar este resumo?')) return;

                const summaryId = this.dataset.summaryId;
                try {
                    const csrfToken = document.querySelector('input[name="csrf_token"]').value;
                    const response = await fetch(`/api/delete/${summaryId}`, {
                        method: 'DELETE',
                        headers: { 'X-CSRFToken': csrfToken }
                    });

                    if (response.ok) {
                        await refreshSummaries();
                        showAlert('Resumo deletado com sucesso', 'success');
                    } else {
                        throw new Error('Erro ao deletar resumo');
                    }
                } catch (error) {
                    showAlert(error.message, 'error');
                }
            });
        });
    }

    async function openSummaryModal(summaryId) {
        try {
            const response = await fetch(`/api/summary/${summaryId}`);
            const summary = await response.json();

            document.getElementById('modalTitle').textContent = summary.title;
            const contentEl = document.getElementById('modalContent');
            contentEl.innerHTML = '';

            const meta = document.createElement('div');
            meta.className = 'modal-info-grid';
            meta.innerHTML = `
                <div class="info-row"><span class="label">URL</span><span class="value"><a href="${summary.url}" target="_blank" rel="noopener">${summary.url}</a></span></div>
                <div class="info-row"><span class="label">Duração</span><span class="value">${formatDuration(summary.duration)}</span></div>
                <div class="info-row"><span class="label">Status</span><span class="value status status-${summary.status}">${summary.status}</span></div>
                <div class="info-row"><span class="label">Data</span><span class="value">${summary.created_at || ''}</span></div>
            `;
            contentEl.appendChild(meta);

            const tabs = document.createElement('div');
            tabs.className = 'content-tabs';
            tabs.innerHTML = `
                <button type="button" class="content-tab active" data-tab="summary">Resumo</button>
                <button type="button" class="content-tab" data-tab="transcript">Transcrição</button>
            `;
            contentEl.appendChild(tabs);

            const summaryPanel = document.createElement('div');
            summaryPanel.id = 'modalSummaryPanel';
            summaryPanel.className = 'content-panel active modal-section';
            summaryPanel.innerHTML = `
                <h4>Resumo inteligente</h4>
                <div class="summary-text markdown-body"></div>
            `;
            summaryPanel.querySelector('.summary-text').innerHTML = renderMarkdownSummary(summary.summary);

            const transcriptPanel = document.createElement('div');
            transcriptPanel.id = 'modalTranscriptPanel';
            transcriptPanel.className = 'content-panel modal-section';
            transcriptPanel.innerHTML = '<h4>O que foi dito</h4><div class="transcript-paragraphs"></div>';
            renderTranscriptParagraphs(
                transcriptPanel.querySelector('.transcript-paragraphs'),
                summary.transcript_paragraphs || []
            );

            if (summary.transcript_highlights) {
                const highlightsSection = document.createElement('div');
                highlightsSection.className = 'modal-section';
                highlightsSection.innerHTML = '<h4>Destaques</h4><div class="highlights"></div>';
                summary.transcript_highlights.split('\n\n').forEach(part => {
                    const card = document.createElement('div');
                    card.className = 'highlight-card';
                    card.textContent = part.trim();
                    highlightsSection.querySelector('.highlights').appendChild(card);
                });
                contentEl.appendChild(highlightsSection);
            }

            contentEl.appendChild(summaryPanel);
            contentEl.appendChild(transcriptPanel);

            tabs.querySelectorAll('.content-tab').forEach(tab => {
                tab.addEventListener('click', () => {
                    tabs.querySelectorAll('.content-tab').forEach(t => t.classList.remove('active'));
                    contentEl.querySelectorAll('.content-panel').forEach(p => p.classList.remove('active'));
                    tab.classList.add('active');
                    contentEl.querySelector(`#modal${tab.dataset.tab === 'summary' ? 'Summary' : 'Transcript'}Panel`)?.classList.add('active');
                });
            });

            modal.dataset.transcript = transcriptParagraphsToText(summary.transcript_paragraphs || []);
            modal.dataset.summary = summary.summary || '';
            modal.classList.add('active');
        } catch (error) {
            showAlert('Erro ao carregar resumo', 'error');
        }
    }

    document.getElementById('copyFullBtn').addEventListener('click', async function() {
        await copyToClipboard(modal.dataset.summary || '', 'Resumo copiado!');
    });

    document.getElementById('copyModalTranscriptBtn').addEventListener('click', async function() {
        await copyToClipboard(modal.dataset.transcript || '', 'Transcrição copiada!');
    });

    document.querySelector('.close-modal').addEventListener('click', function() {
        modal.classList.remove('active');
    });

    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            modal.classList.remove('active');
        }
    });

    refreshSummaries();
});

function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.innerHTML = `
        <i class="fas fa-${getIcon(type)}"></i>
        <span>${message}</span>
        <button class="close-alert" type="button">&times;</button>
    `;

    const nav = document.querySelector('.navbar');
    nav.parentNode.insertBefore(alertDiv, nav.nextSibling);

    alertDiv.querySelector('.close-alert').addEventListener('click', function() {
        alertDiv.remove();
    });

    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

function getIcon(type) {
    const icons = {
        success: 'check-circle',
        error: 'exclamation-circle',
        warning: 'exclamation-triangle',
        info: 'info-circle'
    };
    return icons[type] || 'info-circle';
}

async function copyToClipboard(text, message) {
    try {
        await navigator.clipboard.writeText(text);
        showAlert(message, 'success');
    } catch (error) {
        showAlert('Erro ao copiar', 'error');
    }
}
