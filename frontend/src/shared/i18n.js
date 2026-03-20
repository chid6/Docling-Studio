import { useSettingsStore } from '../features/settings/store.js'

const messages = {
  fr: {
    // Sidebar
    'nav.studio': 'Studio',
    'nav.history': 'Historique',
    'nav.settings': 'Paramètres',

    // Studio — import
    'studio.title': 'Intelligence des documents',
    'studio.subtitle': 'Importez un document PDF pour commencer l\'analyse avec Docling',
    'studio.recentDocs': 'Documents récents',

    // Studio — workspace
    'studio.configure': 'Configurer',
    'studio.verify': 'Vérifier',
    'studio.addFiles': 'Ajouter des fichiers',
    'studio.analyzing': 'Analyse...',
    'studio.run': 'Exécuter',
    'studio.loaded': 'Chargé',
    'studio.analysisRunning': 'Analyse en cours...',
    'studio.failed': 'Échec',
    'studio.visual': 'Visuel',

    // Config panel
    'config.model': 'Modèle',
    'config.pipeline': 'Pipeline',
    'config.ocr': 'OCR',
    'config.ocrHint': 'Activer l\'OCR pour les documents scannés',
    'config.tableStructure': 'Extraction des tableaux',
    'config.tableStructureHint': 'Détecter et extraire la structure des tableaux',
    'config.tableMode': 'Mode tableaux',
    'config.tableModeAccurate': 'Précis',
    'config.tableModeFast': 'Rapide',
    'config.enrichment': 'Enrichissement',
    'config.codeEnrichment': 'Code',
    'config.codeEnrichmentHint': 'OCR spécialisé pour les blocs de code',
    'config.formulaEnrichment': 'Formules',
    'config.formulaEnrichmentHint': 'OCR des formules, retourne du LaTeX',
    'config.pictures': 'Images',
    'config.pictureClassification': 'Classification',
    'config.pictureClassificationHint': 'Classifier les types d\'images',
    'config.pictureDescription': 'Description',
    'config.pictureDescriptionHint': 'Générer des descriptions d\'images (VLM)',
    'config.generatePictureImages': 'Extraire les images',
    'config.generatePictureImagesHint': 'Extraire les images du document',
    'config.generatePageImages': 'Images de pages',
    'config.generatePageImagesHint': 'Générer une image par page via Docling',
    'config.imagesScale': 'Échelle images',
    'config.documents': 'Documents',

    // Results
    'results.textResult': 'Résultat du texte',
    'results.markdown': 'Markdown',
    'results.images': 'Images',
    'results.pageOf': 'Page {current} sur {total}',
    'results.noImages': 'Aucune image détectée dans ce document',
    'results.noMarkdown': 'Pas de contenu markdown',
    'results.runAnalysis': 'Lancez une analyse pour voir les résultats',
    'results.analysisFailed': 'L\'analyse a échoué',
    'results.page': 'Page',

    // Upload
    'upload.drop': 'Déposez un PDF ici ou cliquez pour importer',
    'upload.uploading': 'Import en cours...',
    'upload.maxSize': 'Max 50Mo',

    // History
    'history.title': 'Historique des analyses',
    'history.empty': 'Aucune analyse. Allez dans Studio pour analyser votre premier document.',

    // Settings
    'settings.title': 'Paramètres',
    'settings.apiUrl': 'API URL',
    'settings.version': 'Version',
    'settings.theme': 'Thème',
    'settings.themeDark': 'Sombre',
    'settings.themeLight': 'Clair',
    'settings.language': 'Langue',
  },
  en: {
    'nav.studio': 'Studio',
    'nav.history': 'History',
    'nav.settings': 'Settings',

    'studio.title': 'Document Intelligence',
    'studio.subtitle': 'Upload a PDF document to start analyzing with Docling',
    'studio.recentDocs': 'Recent documents',

    'studio.configure': 'Configure',
    'studio.verify': 'Verify',
    'studio.addFiles': 'Add files',
    'studio.analyzing': 'Analyzing...',
    'studio.run': 'Run',
    'studio.loaded': 'Loaded',
    'studio.analysisRunning': 'Analysis running...',
    'studio.failed': 'Failed',
    'studio.visual': 'Visual',

    'config.model': 'Model',
    'config.pipeline': 'Pipeline',
    'config.ocr': 'OCR',
    'config.ocrHint': 'Enable OCR for scanned documents',
    'config.tableStructure': 'Table extraction',
    'config.tableStructureHint': 'Detect and extract table structure',
    'config.tableMode': 'Table mode',
    'config.tableModeAccurate': 'Accurate',
    'config.tableModeFast': 'Fast',
    'config.enrichment': 'Enrichment',
    'config.codeEnrichment': 'Code',
    'config.codeEnrichmentHint': 'Specialized OCR for code blocks',
    'config.formulaEnrichment': 'Formulas',
    'config.formulaEnrichmentHint': 'Formula OCR, returns LaTeX',
    'config.pictures': 'Pictures',
    'config.pictureClassification': 'Classification',
    'config.pictureClassificationHint': 'Classify picture types',
    'config.pictureDescription': 'Description',
    'config.pictureDescriptionHint': 'Generate picture descriptions (VLM)',
    'config.generatePictureImages': 'Extract pictures',
    'config.generatePictureImagesHint': 'Extract pictures from document',
    'config.generatePageImages': 'Page images',
    'config.generatePageImagesHint': 'Generate one image per page via Docling',
    'config.imagesScale': 'Images scale',
    'config.documents': 'Documents',

    'results.textResult': 'Text result',
    'results.markdown': 'Markdown',
    'results.images': 'Images',
    'results.pageOf': 'Page {current} of {total}',
    'results.noImages': 'No images detected in this document',
    'results.noMarkdown': 'No markdown content',
    'results.runAnalysis': 'Run an analysis to see results',
    'results.analysisFailed': 'Analysis failed',
    'results.page': 'Page',

    'upload.drop': 'Drop a PDF here or click to upload',
    'upload.uploading': 'Uploading...',
    'upload.maxSize': 'Max 50MB',

    'history.title': 'Analysis History',
    'history.empty': 'No analyses yet. Go to Studio to analyze your first document.',

    'settings.title': 'Settings',
    'settings.apiUrl': 'API URL',
    'settings.version': 'Version',
    'settings.theme': 'Theme',
    'settings.themeDark': 'Dark',
    'settings.themeLight': 'Light',
    'settings.language': 'Language',
  }
}

export function useI18n() {
  const settings = useSettingsStore()

  function t(key, params = {}) {
    let str = messages[settings.locale]?.[key] || messages['fr'][key] || key
    for (const [k, v] of Object.entries(params)) {
      str = str.replace(`{${k}}`, v)
    }
    return str
  }

  return { t }
}
