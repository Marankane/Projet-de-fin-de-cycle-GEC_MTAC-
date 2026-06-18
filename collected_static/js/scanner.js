/**
 * Document Scanner & AI Analyzer
 * Gère le scan, l'import et l'analyse des documents
 */

document.addEventListener('DOMContentLoaded', function() {
    const scanArea = document.getElementById('scan-area');
    const fileInput = document.getElementById('document-scanner-input');
    const previewArea = document.getElementById('scan-preview');
    const analyzeBtn = document.getElementById('analyze-btn');
    const loadingSpinner = document.getElementById('loading-spinner');
    const aiResults = document.getElementById('ai-results');

    if (!scanArea) return; // Exit if not on enregistrement page

    // Configure drag & drop
    scanArea.addEventListener('dragover', handleDragOver);
    scanArea.addEventListener('dragleave', handleDragLeave);
    scanArea.addEventListener('drop', handleDrop);
    scanArea.addEventListener('click', () => fileInput.click());

    fileInput.addEventListener('change', handleFileSelect);
    analyzeBtn?.addEventListener('click', analyzeDocument);
});

function handleDragOver(e) {
    e.preventDefault();
    e.stopPropagation();
    this.classList.add('drag-over');
}

function handleDragLeave(e) {
    e.preventDefault();
    e.stopPropagation();
    this.classList.remove('drag-over');
}

function handleDrop(e) {
    e.preventDefault();
    e.stopPropagation();
    this.classList.remove('drag-over');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        displayFile(files[0]);
    }
}

function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) {
        displayFile(file);
    }
}

function displayFile(file) {
    const previewArea = document.getElementById('scan-preview');
    const fileInfo = document.getElementById('file-info');
    const analyzeBtn = document.getElementById('analyze-btn');

    // Vérifier le type
    const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'application/pdf'];
    if (!allowedTypes.includes(file.type)) {
        showAlert('Type de fichier non autorisé', 'danger');
        return;
    }

    // Vérifier la taille
    if (file.size > 20 * 1024 * 1024) {
        showAlert('Fichier trop volumineux (max 20 Mo)', 'danger');
        return;
    }

    // Afficher l'aperçu
    const reader = new FileReader();
    reader.onload = function(e) {
        if (file.type.startsWith('image/')) {
            previewArea.innerHTML = `<img src="${e.target.result}" class="img-fluid rounded" style="max-height: 300px;">`;
        } else if (file.type === 'application/pdf') {
            previewArea.innerHTML = `<div class="text-center p-5 bg-light rounded"><i class="bi bi-file-pdf" style="font-size: 3rem; color: #dc3545;"></i><p class="mt-2">PDF: ${file.name}</p></div>`;
        }
        fileInfo.innerHTML = `<small class="text-muted">${file.name} (${(file.size / 1024).toFixed(2)} KB)</small>`;
        analyzeBtn.disabled = false;
        analyzeBtn.classList.remove('disabled');

        // Stocker le fichier pour analyse
        previewArea.dataset.file = JSON.stringify({
            name: file.name,
            size: file.size,
            type: file.type
        });
    };
    reader.readAsDataURL(file);

    // Stocker le fichier pour l'upload
    document.getElementById('document-scanner-input').dataset.file = file;
}

function analyzeDocument() {
    const fileInput = document.getElementById('document-scanner-input');
    const file = fileInput.files[0];

    if (!file) {
        showAlert('Veuillez sélectionner un document', 'warning');
        return;
    }

    const loadingSpinner = document.getElementById('loading-spinner');
    const analyzeBtn = document.getElementById('analyze-btn');
    const aiResults = document.getElementById('ai-results');

    loadingSpinner.classList.remove('d-none');
    analyzeBtn.disabled = true;
    aiResults.innerHTML = '';

    // Préparer les données
    const formData = new FormData();
    formData.append('document', file);

    // Appel API
    fetch('/courriers/api/process-document/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        loadingSpinner.classList.add('d-none');
        analyzeBtn.disabled = false;

        if (data.success) {
            displayAIResults(data.metadata);
            fillFormFields(data.metadata);
            showAlert('Document analysé avec succès!', 'success');
        } else {
            showAlert(data.error || 'Erreur lors de l\'analyse', 'danger');
        }
    })
    .catch(error => {
        loadingSpinner.classList.add('d-none');
        analyzeBtn.disabled = false;
        showAlert(`Erreur: ${error.message}`, 'danger');
    });
}

function displayAIResults(metadata) {
    const aiResults = document.getElementById('ai-results');
    let html = '<div class="alert alert-info"><strong>Résultats IA :</strong><ul class="mb-0 mt-2">';

    if (metadata.objet) {
        html += `<li><strong>Objet détecté :</strong> ${escapeHtml(metadata.objet)}</li>`;
    }
    if (metadata.expediteur) {
        html += `<li><strong>Expéditeur :</strong> ${escapeHtml(metadata.expediteur)}</li>`;
    }
    if (metadata.date) {
        html += `<li><strong>Date :</strong> ${escapeHtml(metadata.date)}</li>`;
    }
    if (metadata.reference) {
        html += `<li><strong>Référence :</strong> ${escapeHtml(metadata.reference)}</li>`;
    }
    if (metadata.resume) {
        html += `<li><strong>Résumé :</strong> ${escapeHtml(metadata.resume.substring(0, 150))}...</li>`;
    }

    html += '</ul></div>';
    aiResults.innerHTML = html;
}

function fillFormFields(metadata) {
    // Remplir l'objet si détecté
    const objetField = document.querySelector('textarea[name="objet"]');
    if (objetField && metadata.objet && !objetField.value) {
        objetField.value = metadata.objet;
    }

    // Remplir la date si détectée
    const dateField = document.querySelector('input[name="date_reception"]');
    if (dateField && metadata.date && !dateField.value) {
        const parsedDate = parseDate(metadata.date);
        if (parsedDate) {
            dateField.value = parsedDate;
        }
    }

    // Remplir la référence externe
    const refField = document.querySelector('input[name="reference_externe"]');
    if (refField && metadata.reference && !refField.value) {
        refField.value = metadata.reference;
    }
}

function parseDate(dateStr) {
    const patterns = [
        { regex: /(\d{1,2})[/-](\d{1,2})[/-](\d{4})/, format: (m) => `${m[3]}-${String(m[2]).padStart(2, '0')}-${String(m[1]).padStart(2, '0')}` },
    ];

    for (let pattern of patterns) {
        const match = dateStr.match(pattern.regex);
        if (match) {
            return pattern.format(match);
        }
    }
    return null;
}

function showAlert(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    const form = document.querySelector('form');
    if (form) {
        form.parentElement.insertBefore(alertDiv, form);
        setTimeout(() => alertDiv.remove(), 5000);
    }
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
