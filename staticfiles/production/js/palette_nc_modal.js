// Variables globales pour le traitement des palettes NC
let currentRecordId = null;
let totalPalettesNC = 0;

// Fonction pour ouvrir le modal de traitement des palettes NC
function openPaletteNCModal(recordId) {
    if (!recordId || isNaN(recordId)) {
        alert('Erreur: ID d\'enregistrement invalide');
        console.error('ID invalide:', recordId);
        return;
    }
    
    currentRecordId = recordId;
    console.log('Ouverture modal pour record ID:', recordId);
    
    // Réinitialiser le modal
    resetModalState();
    
    // Afficher le modal et l'overlay
    const modal = document.getElementById('paletteNCModal');
    const overlay = document.getElementById('modalOverlay');
    
    modal.classList.add('show');
    overlay.classList.add('show');
    document.body.classList.add('modal-open');
    document.body.style.overflow = 'hidden';
    
    // Charger les détails
    loadPaletteNCDetails(recordId);
}

// Fonction pour fermer le modal
function closePaletteNCModal() {
    const modal = document.getElementById('paletteNCModal');
    const overlay = document.getElementById('modalOverlay');
    
    modal.classList.remove('show');
    overlay.classList.remove('show');
    document.body.classList.remove('modal-open');
    document.body.style.overflow = '';
    
    // Réinitialiser les données
    currentRecordId = null;
    totalPalettesNC = 0;
    resetModalState();
}

// Fonction pour réinitialiser l'état du modal
function resetModalState() {
    document.getElementById('palette-details-loading').classList.remove('d-none');
    document.getElementById('palette-details-error').classList.add('d-none');
    document.getElementById('palette-details-content').classList.add('d-none');
    
    // Réinitialiser les formulaires
    const forms = ['form-toute-conforme', 'form-partiel', 'form-non-conforme', 'form-traitement-detaille'];
    forms.forEach(formId => {
        const form = document.getElementById(formId);
        if (form) form.reset();
    });
    
    // Réinitialiser les champs
    const fields = ['fardeaux_rapide', 'commentaire_controle_detaille', 'palettes_conformes', 'fardeaux_partiels'];
    fields.forEach(fieldId => {
        const field = document.getElementById(fieldId);
        if (field) field.value = '';
    });
}

// Fonction pour charger les détails d'une palette NC
function loadPaletteNCDetails(recordId) {
     const detailsUrl = '/production/api/production-data/';
    console.log('Chargement depuis:', detailsUrl);
    
    fetch(detailsUrl, {
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => {
        console.log('Réponse HTTP:', response.status);
        if (!response.ok) {
            throw new Error(`Erreur ${response.status}: ${response.statusText}`);
        }
        return response.json();
    })
    .then(data => {
        console.log('Données reçues:', data);
        displayPaletteNCDetails(data);
    })
    .catch(error => {
        console.error('Erreur lors du chargement:', error);
        showError(error.message);
    });
}

// Fonction pour afficher les détails dans le modal
function displayPaletteNCDetails(data) {
    // Masquer le loading
    document.getElementById('palette-details-loading').classList.add('d-none');
    
    // Remplir les informations
    document.getElementById('modal-produit').textContent = data.produit || 'N/A';
    document.getElementById('modal-operateur').textContent = data.operateur || 'N/A';
    document.getElementById('modal-ligne').textContent = data.ligne || 'N/A';
    document.getElementById('modal-date').textContent = data.date_heure || 'N/A';
    document.getElementById('modal-palettes-nc').textContent = data.palettes_nc || 0;
    document.getElementById('modal-cause-nc').textContent = data.cause_non_conformite || 'Non renseignée';
    
    // Stocker le nombre de palettes NC
    totalPalettesNC = data.palettes_nc || 0;
    
    // Configurer les formulaires
    setupForms(currentRecordId);
    
    // Configurer les validations
    setupFormValidation();
    
    // Afficher le contenu
    document.getElementById('palette-details-content').classList.remove('d-none');
}

// Fonction pour afficher une erreur
function showError(message) {
    document.getElementById('palette-details-loading').classList.add('d-none');
    document.getElementById('error-message').textContent = message;
    document.getElementById('palette-details-error').classList.remove('d-none');
}

// Fonction pour configurer les actions des formulaires
function setupForms(recordId) {
    const baseUrl = `/production/traiter-palette-nc/${recordId}/`;
    
    // Mettre à jour les actions
    document.getElementById('form-toute-conforme').action = baseUrl;
    document.getElementById('form-partiel').action = baseUrl;
    document.getElementById('form-non-conforme').action = baseUrl;
    document.getElementById('form-traitement-detaille').action = baseUrl;
    
    // Mettre à jour les champs cachés
    document.getElementById('record-id-toute-conforme').value = recordId;
    document.getElementById('record-id-partiel').value = recordId;
    document.getElementById('record-id-non-conforme').value = recordId;
    document.getElementById('record-id-detaille').value = recordId;
}

// Fonction pour configurer la validation des formulaires
function setupFormValidation() {
    const palettesInput = document.getElementById('palettes_conformes');
    const fardeauxInput = document.getElementById('fardeaux_partiels');
    
    if (palettesInput) {
        palettesInput.max = totalPalettesNC;
        palettesInput.addEventListener('input', validateTraitementDetaille);
    }
    
    if (fardeauxInput) {
        fardeauxInput.max = totalPalettesNC * 72; // 1 palette = 72 fardeaux
        fardeauxInput.addEventListener('input', validateTraitementDetaille);
    }
}

// Fonction de validation du traitement détaillé avec conversion correcte
function validateTraitementDetaille() {
    const palettes = parseInt(document.getElementById('palettes_conformes').value) || 0;
    const fardeaux = parseInt(document.getElementById('fardeaux_partiels').value) || 0;
    
    // Validation des limites
    if (palettes > totalPalettesNC) {
        document.getElementById('palettes_conformes').value = totalPalettesNC;
        showValidationWarning('Nombre de palettes ajusté au maximum possible');
        return false;
    }
    
    // Conversion : 1 palette = 72 fardeaux, donc max fardeaux = totalPalettesNC * 72
    const maxFardeaux = totalPalettesNC * 72;
    if (fardeaux > maxFardeaux) {
        document.getElementById('fardeaux_partiels').value = maxFardeaux;
        showValidationWarning('Nombre de fardeaux ajusté au maximum possible');
        return false;
    }
    
    // Validation de cohérence : palettes entières + fardeaux ne doivent pas dépasser le total
    const fardeauxDespalettesEntieres = palettes * 72;
    const totalFardeauxUtilises = fardeauxDespalettesEntieres + fardeaux;
    
    if (totalFardeauxUtilises > maxFardeaux) {
        // Ajuster automatiquement les fardeaux
        const fardeauxRestants = Math.max(0, maxFardeaux - fardeauxDespalettesEntieres);
        document.getElementById('fardeaux_partiels').value = fardeauxRestants;
        showValidationWarning(`Fardeaux ajustés à ${fardeauxRestants} (maximum après ${palettes} palette(s) entière(s))`);
    }
    
    return true;
}

// Fonction pour afficher un avertissement de validation
function showValidationWarning(message) {
    // Créer ou mettre à jour un message d'avertissement temporaire
    let warning = document.getElementById('validation-warning');
    if (!warning) {
        warning = document.createElement('div');
        warning.id = 'validation-warning';
        warning.className = 'alert alert-warning alert-dismissible fade show';
        warning.innerHTML = `
            <i class="fas fa-exclamation-triangle"></i> <span class="message"></span>
            <button type="button" class="btn-close" onclick="this.parentElement.remove()"></button>
        `;
        document.getElementById('palette-details-content').insertBefore(warning, document.getElementById('palette-details-content').firstChild);
    }
    
    warning.querySelector('.message').textContent = message;
    
    // Auto-suppression après 3 secondes
    setTimeout(() => {
        if (warning && warning.parentNode) {
            warning.remove();
        }
    }, 3000);
}

// Fonctions de soumission des différents traitements

function submitTraitementDetaille() {
    if (!currentRecordId) {
        alert('Erreur: Aucun enregistrement sélectionné');
        return;
    }
    
    if (!validateTraitementDetaille()) {
        return;
    }
    
    const commentaire = document.getElementById('commentaire_controle_detaille').value.trim();
    if (!commentaire) {
        alert('Veuillez saisir un commentaire décrivant le contrôle effectué');
        document.getElementById('commentaire_controle_detaille').focus();
        return;
    }
    
    const conformes = parseInt(document.getElementById('palettes_conformes').value) || 0;
    const fardeaux = parseInt(document.getElementById('fardeaux_partiels').value) || 0;
    
    const message = `Confirmer le traitement détaillé :\n` +
                   `• ${conformes} palette(s) récupérées comme conformes\n` +
                   `• ${fardeaux} fardeau(x) récupérés partiellement\n` +
                   `• Le reste sera considéré comme déchets`;
    
    if (confirm(message)) {
        document.getElementById('form-traitement-detaille').submit();
    }
}

function submitRapidePartiel() {
    const fardeaux = parseInt(document.getElementById('fardeaux_rapide').value);
    
    if (!fardeaux || fardeaux <= 0) {
        alert('Veuillez saisir un nombre de fardeaux valide');
        document.getElementById('fardeaux_rapide').focus();
        return;
    }
    
    if (fardeaux > totalPalettesNC * 72) {
        alert(`Le nombre de fardeaux ne peut pas dépasser ${totalPalettesNC * 72} (${totalPalettesNC} palettes × 72)`);
        return;
    }
    
    if (!currentRecordId) {
        alert('Erreur: Aucun enregistrement sélectionné');
        return;
    }
    
    // Calculer les boîtes de déchets : fardeaux non récupérés × 24 boîtes/fardeau
    const totalFardeauxDansNC = totalPalettesNC * 72;
    const fardeauxNonRecuperes = totalFardeauxDansNC - fardeaux;
    const boitesDeDechetsPrevues = fardeauxNonRecuperes * 24;
    
    // Remplir le formulaire partiel caché
    document.getElementById('fardeaux_conformes').value = fardeaux;
    document.getElementById('commentaire_controle').value = `Récupération rapide: ${fardeaux} fardeau(x) récupéré(s), ${fardeauxNonRecuperes} fardeaux → ${boitesDeDechetsPrevues} boîtes de déchets`;
    
    const message = `Confirmer la récupération rapide :\n` +
                   `• ${fardeaux} fardeau(x) récupéré(s)\n` +
                   `• ${fardeauxNonRecuperes} fardeau(x) non récupéré(s) = ${boitesDeDechetsPrevues} boîtes de déchets`;
    
    if (confirm(message)) {
        document.getElementById('form-partiel').submit();
    }
}

function submitTouteConforme() {
    if (!currentRecordId) {
        alert('Erreur: Aucun enregistrement sélectionné');
        return;
    }
    
    const message = `Êtes-vous sûr de vouloir marquer les ${totalPalettesNC} palette(s) non conformes comme CONFORMES ?\n\nCela signifie qu'elles ont été entièrement récupérées.`;
    
    if (confirm(message)) {
        document.getElementById('form-toute-conforme').submit();
    }
}

function submitNonConforme() {
    if (!currentRecordId) {
        alert('Erreur: Aucun enregistrement sélectionné');
        return;
    }
    
    const message = `Êtes-vous sûr de vouloir confirmer que les ${totalPalettesNC} palette(s) restent NON CONFORMES ?\n\nElles seront comptabilisées comme déchets définitifs.`;
    
    if (confirm(message)) {
        document.getElementById('form-non-conforme').submit();
    }
}

// Fonction utilitaire pour récupérer le token CSRF
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Event listeners principaux
document.addEventListener('DOMContentLoaded', function() {
    console.log('Initialisation du système de traitement des palettes NC');
    
    // Gestion de la fermeture du modal avec Échap
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape') {
            const modal = document.getElementById('paletteNCModal');
            if (modal && modal.classList.contains('show')) {
                closePaletteNCModal();
            }
        }
    });
    
    // Gestion du clic sur l'overlay
    const overlay = document.getElementById('modalOverlay');
    if (overlay) {
        overlay.addEventListener('click', closePaletteNCModal);
    }
    
    // Empêcher la fermeture du modal en cliquant sur le contenu
    const modalContent = document.querySelector('#paletteNCModal .modal-content');
    if (modalContent) {
        modalContent.addEventListener('click', function(event) {
            event.stopPropagation();
        });
    }
    
    console.log('Système de traitement des palettes NC initialisé avec succès');
});