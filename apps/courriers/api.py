"""
API endpoints pour traiter les documents scannés
"""
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
import json
import logging
from .ai_service import DocumentAnalyzer

logger = logging.getLogger(__name__)

def _is_allowed_document(file):
    content_type = (getattr(file, 'content_type', '') or '').lower()
    name = (getattr(file, 'name', '') or '').lower()
    allowed_types = {
        'image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/tiff',
        'application/pdf', 'application/octet-stream', 'binary/octet-stream',
    }
    allowed_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.webp', '.tif', '.tiff', '.pdf')

    if content_type == 'application/pdf':
        return True
    if content_type.startswith('image/'):
        return True
    if content_type in allowed_types and name.endswith(allowed_extensions):
        return True
    if name.endswith('.pdf'):
        return True
    return False


@login_required
@require_POST
def process_document(request):
    """
    Endpoint pour analyser un document scanné/importé
    Retourne les métadonnées extraites
    """
    if 'document' not in request.FILES:
        return JsonResponse({'error': 'Aucun fichier fourni'}, status=400)

    file = request.FILES['document']

    # Vérifier le type de fichier
    if not _is_allowed_document(file):
        return JsonResponse(
            {'error': 'Type de fichier non autorisé. Acceptés: JPEG, PNG, GIF, WEBP, TIFF ou PDF.'},
            status=400
        )

    # Vérifier la taille
    if file.size > 20 * 1024 * 1024:  # 20 Mo
        return JsonResponse({'error': 'Fichier trop volumineux (max 20 Mo)'}, status=400)

    try:
        metadata = DocumentAnalyzer.analyze_document(file)

        return JsonResponse({
            'success': True,
            'backend': metadata.get('source', 'unknown'),
            'metadata': {
                'objet': metadata.get('objet'),
                'expediteur': metadata.get('expediteur'),
                'date': metadata.get('date'),
                'reference': metadata.get('reference'),
                'resume': (metadata.get('contenu_resume') or "")[:200],
            },
            'raw_text': (metadata.get('texte_complet') or "")[:500],  # Premiers 500 chars
        })

    except ValueError as e:
        logger.warning(
            "Analyse document echouee: name=%s content_type=%s size=%s error=%s",
            getattr(file, 'name', ''),
            getattr(file, 'content_type', ''),
            getattr(file, 'size', ''),
            e,
        )
        return JsonResponse({
            'success': False,
            'error': str(e),
            'metadata': {},
            'raw_text': '',
        })
    except Exception as e:
        return JsonResponse({'error': f'Erreur lors du traitement: {str(e)}'}, status=500)
