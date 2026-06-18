"""
Service IA pour analyser les documents et extraire les métadonnées
"""
import base64
import io
import json
import os
import re
import urllib.request
import urllib.parse
from datetime import date
from PIL import Image
import pytesseract

try:
    import pypdfium2 as pdfium
except ImportError:
    pdfium = None

# Configuration pytesseract pour Windows
# Décommenter si Tesseract n'est pas dans le PATH système
# pytesseract.pytesseract.pytesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

AI_BACKENDS = [b.strip().lower() for b in os.getenv('AI_BACKENDS', 'tesseract,ocr_space,azure_vision').split(',') if b.strip()]
OCR_SPACE_API_KEY = os.getenv('OCR_SPACE_API_KEY')
AZURE_COMPUTER_VISION_ENDPOINT = os.getenv('AZURE_COMPUTER_VISION_ENDPOINT')
AZURE_COMPUTER_VISION_KEY = os.getenv('AZURE_COMPUTER_VISION_KEY')


class DocumentAnalyzer:
    """Analyse les documents scannés pour extraire informations"""

    @staticmethod
    def extract_text_from_image(image_bytes, lang='fra'):
        """Extrait le texte d'une image via OCR local"""
        errors = []
        try:
            img = Image.open(io.BytesIO(image_bytes))
            for ocr_lang in [lang, 'eng', None]:
                try:
                    if ocr_lang:
                        return pytesseract.image_to_string(img, lang=ocr_lang)
                    return pytesseract.image_to_string(img)
                except Exception as exc:
                    errors.append(f"{ocr_lang or 'default'}: {exc}")
        except Exception as e:
            raise ValueError(f"Erreur OCR local: {e}")
        raise ValueError("Erreur OCR local: " + " | ".join(errors))

    @staticmethod
    def analyze_with_tesseract(image_bytes):
        text = DocumentAnalyzer.extract_text_from_image(image_bytes)
        if not text or not text.strip():
            raise ValueError("OCR local n'a renvoyé aucun texte.")
        metadata = DocumentAnalyzer.extract_metadata(text)
        metadata['texte_complet'] = text
        metadata['source'] = 'tesseract'
        return metadata

    @staticmethod
    def pdf_to_images(pdf_bytes, max_pages=5, scale=2.5):
        """Rend les premières pages d'un PDF en images PNG pour l'OCR."""
        if pdfium is None:
            raise ValueError("Support PDF indisponible: installez pypdfium2.")

        try:
            pdf = pdfium.PdfDocument(pdf_bytes)
        except Exception as exc:
            raise ValueError(f"PDF illisible: {exc}") from exc

        images = []
        try:
            page_count = min(len(pdf), max_pages)
            if page_count == 0:
                raise ValueError("PDF vide.")

            for page_index in range(page_count):
                page = pdf[page_index]
                bitmap = None
                try:
                    bitmap = page.render(scale=scale)
                    image = bitmap.to_pil()
                    buffer = io.BytesIO()
                    image.save(buffer, format='PNG')
                    images.append(buffer.getvalue())
                finally:
                    if bitmap is not None:
                        try:
                            bitmap.close()
                        except Exception:
                            pass
                    try:
                        page.close()
                    except Exception:
                        pass
        finally:
            try:
                pdf.close()
            except Exception:
                pass

        return images

    @staticmethod
    def extract_text_from_pdf(pdf_bytes, max_pages=10):
        """Extrait le texte embarque d'un PDF avant de tenter l'OCR."""
        if pdfium is None:
            raise ValueError("Support PDF indisponible: installez pypdfium2.")

        try:
            pdf = pdfium.PdfDocument(pdf_bytes)
        except Exception as exc:
            raise ValueError(f"PDF illisible: {exc}") from exc

        texts = []
        try:
            page_count = min(len(pdf), max_pages)
            for page_index in range(page_count):
                page = pdf[page_index]
                text_page = None
                try:
                    text_page = page.get_textpage()
                    page_text = text_page.get_text_range()
                    if page_text and page_text.strip():
                        texts.append(f"--- Page {page_index + 1} ---\n{page_text.strip()}")
                finally:
                    if text_page is not None:
                        try:
                            text_page.close()
                        except Exception:
                            pass
                    try:
                        page.close()
                    except Exception:
                        pass
        finally:
            try:
                pdf.close()
            except Exception:
                pass

        return "\n\n".join(texts).strip()

    @staticmethod
    def analyze_pdf_with_tesseract(pdf_bytes):
        embedded_text = DocumentAnalyzer.extract_text_from_pdf(pdf_bytes)
        if embedded_text:
            metadata = DocumentAnalyzer.extract_metadata(embedded_text)
            metadata['texte_complet'] = embedded_text
            metadata['source'] = 'pdf_text'
            return metadata

        images = DocumentAnalyzer.pdf_to_images(pdf_bytes)
        texts = []
        page_errors = []

        for index, image_bytes in enumerate(images, start=1):
            try:
                page_text = DocumentAnalyzer.extract_text_from_image(image_bytes)
                if page_text and page_text.strip():
                    texts.append(f"--- Page {index} ---\n{page_text.strip()}")
            except Exception as exc:
                page_errors.append(f"page {index}: {exc}")

        text = "\n\n".join(texts).strip()
        if not text:
            details = " | ".join(page_errors) if page_errors else "aucun texte détecté"
            raise ValueError(f"OCR PDF local n'a renvoyé aucun texte ({details}).")

        metadata = DocumentAnalyzer.extract_metadata(text)
        metadata['texte_complet'] = text
        metadata['source'] = 'tesseract_pdf'
        metadata['pages_analysees'] = len(images)
        return metadata

    @staticmethod
    def analyze_with_ocr_space(image_bytes):
        if not OCR_SPACE_API_KEY:
            raise ValueError("Clé OCR.space non configurée.")

        url = 'https://api.ocr.space/parse/image'
        data = {
            'base64Image': f"data:image/jpeg;base64,{base64.b64encode(image_bytes).decode('utf-8')}",
            'language': 'fre',
            'isOverlayRequired': 'false',
            'detectOrientation': 'true',
        }
        encoded = urllib.parse.urlencode(data).encode('utf-8')
        req = urllib.request.Request(
            url,
            data=encoded,
            headers={'apikey': OCR_SPACE_API_KEY, 'User-Agent': 'GEDCourrier/1.0'}
        )

        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode('utf-8'))
        except Exception as e:
            raise ValueError(f"Erreur OCR.space: {e}")

        if result.get('IsErroredOnProcessing'):
            errors = result.get('ErrorMessage') or result.get('ErrorDetails') or 'Erreur inconnue'
            raise ValueError(f"OCR.space a échoué: {errors}")

        parsed_results = result.get('ParsedResults')
        if not parsed_results or not parsed_results[0].get('ParsedText'):
            raise ValueError("OCR.space n'a renvoyé aucun texte.")

        text = parsed_results[0]['ParsedText']
        metadata = DocumentAnalyzer.extract_metadata(text)
        metadata['texte_complet'] = text
        metadata['source'] = 'ocr_space'
        return metadata

    @staticmethod
    def analyze_with_azure_vision(image_bytes):
        if not AZURE_COMPUTER_VISION_ENDPOINT or not AZURE_COMPUTER_VISION_KEY:
            raise ValueError("Azure Computer Vision non configuré.")

        url = AZURE_COMPUTER_VISION_ENDPOINT.rstrip('/') + '/vision/v3.2/ocr?language=fr&detectOrientation=true'
        req = urllib.request.Request(
            url,
            data=image_bytes,
            headers={
                'Ocp-Apim-Subscription-Key': AZURE_COMPUTER_VISION_KEY,
                'Content-Type': 'application/octet-stream',
                'User-Agent': 'GEDCourrier/1.0'
            },
            method='POST'
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode('utf-8'))
        except Exception as e:
            raise ValueError(f"Erreur Azure Computer Vision: {e}")

        if not result.get('regions'):
            raise ValueError("Azure Computer Vision n'a renvoyé aucune région de texte.")

        lines = []
        for region in result.get('regions', []):
            for line in region.get('lines', []):
                words = [w.get('text', '') for w in line.get('words', [])]
                if words:
                    lines.append(' '.join(words))

        text = '\n'.join(lines).strip()
        if not text:
            raise ValueError("Azure Computer Vision n'a renvoyé aucun texte.")

        metadata = DocumentAnalyzer.extract_metadata(text)
        metadata['texte_complet'] = text
        metadata['source'] = 'azure_vision'
        return metadata

    @staticmethod
    def extract_metadata(text):
        """Extrait les métadonnées du texte"""
        metadata = {
            'objet': None,
            'expediteur': None,
            'date': None,
            'reference': None,
            'contenu_resume': None,
        }

        lines = [
            l.strip()
            for l in text.split('\n')
            if l.strip() and not l.strip().startswith('--- Page ')
        ]
        searchable_text = '\n'.join(lines) if lines else text

        # Recherche date (JJ/MM/YYYY, DD-MM-YYYY, etc.)
        date_patterns = [
            r'\d{1,2}[/-]\d{1,2}[/-]\d{4}',
            r'(?:janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\s+\d{1,2},?\s+\d{4}',
        ]
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                metadata['date'] = match.group(0)
                break

        # Recherche "Objet :" ou "RE :" ou "SUBJECT :"
        objet_patterns = [
            r'(?:OBJET|RE|SUBJECT|Sujet)\s*[\.:=-]+\s*(.+)',
            r'^(?!.*@)(.{10,200})$',  # Première ligne non-email de 10-200 chars
        ]
        for pattern in objet_patterns:
            match = re.search(pattern, searchable_text, re.IGNORECASE | re.MULTILINE)
            if match:
                metadata['objet'] = match.group(1).strip()
                break

        # Recherche "De :" ou "From :"
        expediteur_patterns = [
            r'(?:DE|FROM|Expéditeur)\s*[:=]\s*(.+)',
            r'(?:Monsieur|Mme|M\.|Mademoiselle)\s+(.+?)(?:\s+(?:et|ou|,|\n))',
        ]
        for pattern in expediteur_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                metadata['expediteur'] = match.group(1).strip()
                break

        # Recherche numéro de référence/dossier
        ref_patterns = [
            r'(?:DOSSIER|RÉFÉRENCE|REFERENCE|RÉF|REF\.?|N°)\s*[\.:=-]?\s*([A-Z0-9][A-Z0-9_./-]+)',
        ]
        for pattern in ref_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                metadata['reference'] = match.group(1).strip()
                break

        # Résumé : premiers 300 caractères
        metadata['contenu_resume'] = text[:300].strip()

        return metadata

    @staticmethod
    def analyze_document(image_file):
        """Analyse complète en utilisant une cascade de backends IA"""
        content_type = (getattr(image_file, 'content_type', '') or '').lower()
        filename = (getattr(image_file, 'name', '') or '').lower()
        file_bytes = image_file.read()
        try:
            image_file.seek(0)
        except Exception:
            pass

        if not file_bytes:
            raise ValueError("Aucun contenu de document à analyser.")

        is_pdf = content_type == 'application/pdf' or filename.endswith('.pdf') or file_bytes.startswith(b'%PDF')
        if is_pdf:
            try:
                return DocumentAnalyzer.analyze_pdf_with_tesseract(file_bytes)
            except Exception as exc:
                raise ValueError(f"Analyse PDF impossible. {exc}") from exc

        errors = []
        for backend in AI_BACKENDS:
            if backend == 'tesseract':
                try:
                    return DocumentAnalyzer.analyze_with_tesseract(file_bytes)
                except Exception as exc:
                    errors.append(f"tesseract: {exc}")
                    continue
            if backend == 'ocr_space':
                try:
                    return DocumentAnalyzer.analyze_with_ocr_space(file_bytes)
                except Exception as exc:
                    errors.append(f"ocr_space: {exc}")
                    continue
            if backend == 'azure_vision':
                try:
                    return DocumentAnalyzer.analyze_with_azure_vision(file_bytes)
                except Exception as exc:
                    errors.append(f"azure_vision: {exc}")
                    continue

        raise ValueError("Aucun service IA disponible. " + " | ".join(errors))
