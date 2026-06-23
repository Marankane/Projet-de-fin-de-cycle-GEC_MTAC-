/**
 * Document Scanner & AI Analyzer
 * Handles document selection, preview and OCR metadata extraction.
 */

let selectedScannerFile = null;

document.addEventListener('DOMContentLoaded', function() {
    const scanArea = document.getElementById('scan-area');
    const fileInput = document.getElementById('document-scanner-input');
    const analyzeBtn = document.getElementById('analyze-btn');

    if (!scanArea || !fileInput || !analyzeBtn) return;

    scanArea.addEventListener('dragover', handleDragOver);
    scanArea.addEventListener('dragleave', handleDragLeave);
    scanArea.addEventListener('drop', handleDrop);
    scanArea.addEventListener('click', () => fileInput.click());
    scanArea.addEventListener('keydown', (event) => {
        if (event.key === 'Enter' || event.key === ' ') {
            event.preventDefault();
            fileInput.click();
        }
    });

    fileInput.addEventListener('change', handleFileSelect);
    analyzeBtn.addEventListener('click', analyzeDocument);
});

function handleDragOver(event) {
    event.preventDefault();
    event.stopPropagation();
    this.classList.add('drag-over');
}

function handleDragLeave(event) {
    event.preventDefault();
    event.stopPropagation();
    this.classList.remove('drag-over');
}

function handleDrop(event) {
    event.preventDefault();
    event.stopPropagation();
    this.classList.remove('drag-over');

    const files = event.dataTransfer.files;
    if (!files.length) return;

    const file = files[0];
    const fileInput = document.getElementById('document-scanner-input');
    if (fileInput && window.DataTransfer) {
        const transfer = new DataTransfer();
        transfer.items.add(file);
        fileInput.files = transfer.files;
    }
    displayFile(file);
}

function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) displayFile(file);
}

function displayFile(file) {
    const previewArea = document.getElementById('scan-preview');
    const fileInfo = document.getElementById('file-info');
    const analyzeBtn = document.getElementById('analyze-btn');
    const aiResults = document.getElementById('ai-results');

    const allowedTypes = [
        'image/jpeg',
        'image/png',
        'image/gif',
        'image/webp',
        'image/tiff',
        'application/pdf',
        'application/octet-stream',
        ''
    ];
    const fileName = (file.name || '').toLowerCase();
    const allowedExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.tif', '.tiff', '.pdf'];
    const hasAllowedExtension = allowedExtensions.some(ext => fileName.endsWith(ext));

    if (!(allowedTypes.includes(file.type) && hasAllowedExtension) && !(file.type.startsWith('image/') && hasAllowedExtension)) {
        resetScannerSelection();
        showAlert('Type de fichier non autorise. Formats acceptes : JPEG, PNG, GIF, WEBP, TIFF ou PDF.', 'danger');
        return;
    }

    if (file.size > 20 * 1024 * 1024) {
        resetScannerSelection();
        showAlert('Fichier trop volumineux. Maximum : 20 Mo.', 'danger');
        return;
    }

    selectedScannerFile = file;
    if (aiResults) aiResults.innerHTML = '';

    analyzeBtn.disabled = false;
    analyzeBtn.classList.remove('disabled');
    analyzeBtn.title = '';

    if (fileInfo) {
        fileInfo.innerHTML = `<small class="text-muted">${escapeHtml(file.name)} (${formatFileSize(file.size)})</small>`;
    }

    const isPdf = file.type === 'application/pdf' || fileName.endsWith('.pdf');
    if (isPdf) {
        previewArea.innerHTML = `
            <div class="text-center p-5 bg-light rounded">
                <i class="bi bi-file-pdf" style="font-size: 3rem; color: #dc3545;"></i>
                <p class="mt-2 mb-1">PDF: ${escapeHtml(file.name)}</p>
                <p class="small text-muted mb-0">Le PDF sera converti en images puis analysé par OCR.</p>
            </div>
        `;
        showInlineResult("PDF pret pour l'analyse IA.", 'info');
        return;
    }

    const reader = new FileReader();
    reader.onload = function(event) {
        previewArea.innerHTML = `<img src="${event.target.result}" class="img-fluid rounded" style="max-height: 300px;" alt="Apercu du document">`;
    };
    reader.onerror = function() {
        resetScannerSelection();
        showAlert("Impossible de lire le fichier selectionne.", 'danger');
    };
    reader.readAsDataURL(file);
}

function resetScannerSelection() {
    selectedScannerFile = null;
    const fileInput = document.getElementById('document-scanner-input');
    const analyzeBtn = document.getElementById('analyze-btn');
    const fileInfo = document.getElementById('file-info');
    if (fileInput) fileInput.value = '';
    if (analyzeBtn) {
        analyzeBtn.disabled = true;
        analyzeBtn.classList.add('disabled');
    }
    if (fileInfo) fileInfo.innerHTML = '';
}

function analyzeDocument() {
    const fileInput = document.getElementById('document-scanner-input');
    const file = (fileInput && fileInput.files[0]) || selectedScannerFile;

    if (!file) {
        showAlert('Veuillez selectionner un document.', 'warning');
        return;
    }

    const fileName = (file.name || '').toLowerCase();
    const isPdf = file.type === 'application/pdf' || fileName.endsWith('.pdf');
    if (!file.type.startsWith('image/') && !isPdf) {
        showAlert("L'analyse IA accepte les images et les PDF uniquement.", 'warning');
        return;
    }

    const loadingSpinner = document.getElementById('loading-spinner');
    const analyzeBtn = document.getElementById('analyze-btn');
    const aiResults = document.getElementById('ai-results');

    if (loadingSpinner) loadingSpinner.classList.remove('d-none');
    analyzeBtn.disabled = true;
    analyzeBtn.classList.add('disabled');
    if (aiResults) aiResults.innerHTML = '';

    const formData = new FormData();
    formData.append('document', file);

    fetch('/courriers/api/process-document/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken') || ''
        },
        body: formData
    })
    .then(async response => {
        let data;
        try {
            data = await response.json();
        } catch (error) {
            throw new Error('Reponse serveur invalide.');
        }
        if (!response.ok) {
            throw new Error(data.error || data.detail || `Erreur HTTP ${response.status}`);
        }
        return data;
    })
    .then(data => {
        if (loadingSpinner) loadingSpinner.classList.add('d-none');
        analyzeBtn.disabled = false;
        analyzeBtn.classList.remove('disabled');

        if (data.success) {
            displayAIResults(data.metadata || {}, data.backend);
            fillFormFields(data.metadata || {});
            showAlert('Document analyse avec succes.', 'success');
        } else {
            showInlineResult(data.error || "Erreur lors de l'analyse.", 'danger');
        }
    })
    .catch(error => {
        if (loadingSpinner) loadingSpinner.classList.add('d-none');
        analyzeBtn.disabled = false;
        analyzeBtn.classList.remove('disabled');
        showInlineResult(error.message, 'danger');
    });
}

function displayAIResults(metadata, backend) {
    const aiResults = document.getElementById('ai-results');
    const rows = [];

    if (metadata.objet) rows.push(`<li><strong>Objet detecte :</strong> ${escapeHtml(metadata.objet)}</li>`);
    if (metadata.expediteur) rows.push(`<li><strong>Expediteur :</strong> ${escapeHtml(metadata.expediteur)}</li>`);
    if (metadata.date) rows.push(`<li><strong>Date :</strong> ${escapeHtml(metadata.date)}</li>`);
    if (metadata.reference) rows.push(`<li><strong>Reference :</strong> ${escapeHtml(metadata.reference)}</li>`);
    if (metadata.resume) rows.push(`<li><strong>Resume :</strong> ${escapeHtml(metadata.resume.substring(0, 200))}</li>`);

    const details = rows.length ? `<ul class="mb-0 mt-2">${rows.join('')}</ul>` : '<p class="mb-0 mt-2">Aucune metadonnee fiable detectee.</p>';
    aiResults.innerHTML = `<div class="alert alert-info"><strong>Resultats IA${backend ? ` (${escapeHtml(backend)})` : ''} :</strong>${details}</div>`;
}

function fillFormFields(metadata) {
    const objetField = document.querySelector('textarea[name="objet"]');
    if (objetField && metadata.objet && !objetField.value.trim()) {
        objetField.value = metadata.objet;
    }

    const dateField = document.querySelector('input[name="date_reception"]');
    if (dateField && metadata.date && !dateField.value) {
        const parsedDate = parseDate(metadata.date);
        if (parsedDate) dateField.value = parsedDate;
    }

    const numeroLettreField = document.querySelector('input[name="numero_lettre"]');
    if (numeroLettreField && metadata.reference && !numeroLettreField.value.trim()) {
        numeroLettreField.value = metadata.reference;
    }

    [objetField, dateField, numeroLettreField].forEach(field => {
        if (!field) return;
        field.dispatchEvent(new Event('input', { bubbles: true }));
        field.dispatchEvent(new Event('change', { bubbles: true }));
    });
}

function parseDate(dateStr) {
    const numeric = dateStr.match(/(\d{1,2})[/-](\d{1,2})[/-](\d{4})/);
    if (numeric) {
        return `${numeric[3]}-${String(numeric[2]).padStart(2, '0')}-${String(numeric[1]).padStart(2, '0')}`;
    }
    return null;
}

function showInlineResult(message, type) {
    const aiResults = document.getElementById('ai-results');
    if (aiResults) {
        aiResults.innerHTML = `<div class="alert alert-${type} mb-0">${escapeHtml(message)}</div>`;
    } else {
        showAlert(message, type);
    }
}

function showAlert(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${escapeHtml(message)}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Fermer"></button>
    `;

    const form = document.querySelector('form');
    if (form && form.parentElement) {
        form.parentElement.insertBefore(alertDiv, form);
        setTimeout(() => {
            try {
                bootstrap.Alert.getOrCreateInstance(alertDiv).close();
            } catch (error) {
                alertDiv.remove();
            }
        }, 5000);
    }
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.substring(0, name.length + 1) === `${name}=`) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text == null ? '' : String(text);
    return div.innerHTML;
}

function formatFileSize(size) {
    if (size >= 1024 * 1024) {
        return `${(size / (1024 * 1024)).toFixed(2)} MB`;
    }
    return `${(size / 1024).toFixed(2)} KB`;
}
