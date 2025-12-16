# =======================
# IMPORTS
# =======================
from django.shortcuts import (
    render, get_object_or_404, redirect
)
from django.contrib.auth.decorators import login_required
from django.contrib.auth import (
    authenticate, login, logout, update_session_auth_hash, get_user_model
)
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import (
    JsonResponse, HttpResponseBadRequest, HttpResponse
)
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.utils import timezone
from django.contrib import messages
from django.db import transaction
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse

from django.utils import timezone
from datetime import timedelta
from django.shortcuts import render
from django.db import transaction
from pyfcm import FCMNotification
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from .models import Chaine, Video, Abonnement

# 🔥 FIX IMPORT — remplacer ChannelForm par ChaineForm
from .forms import ChaineForm   # ✔ pas ChannelForm

import random
import base64
import os

# Tes modèles
from .models import (
    Appel, Amitie, Discussion, Message, Publication,
    Chaine, Abonnement, Video, Profile, Notification, Media, Commentaire
)

# Tes formulaires
from .forms import (
    InscriptionForm, ProfileForm, PublicationForm,
    MediaForm, VideoUploadForm
)

# Notifications push
from .notifications import envoyer_notification_push

# =======================
# FIX : une seule ligne pour User
# =======================
User = get_user_model()

# =========================== 
# Accueil
# ===========================
@login_required(login_url='eglise:inscription')
def accueil(request):
    if not request.user.is_authenticated:
        return redirect('eglise:inscription')

    notifications = Notification.objects.filter(utilisateur=request.user).order_by('-date')[:5]
    content_type = request.GET.get('type', 'accueil')

    # --- Filtrage des chaînes ---
    if content_type == 'chaines':
        chaines = Chaine.objects.all()
        abonnements = Abonnement.objects.filter(utilisateur=request.user).values_list('chaine_id', flat=True)
        return render(request, 'eglise/accueil.html', {
            'content_type': content_type,
            'chaines': chaines,
            'abonnements': abonnements,
            'notifications': notifications,
        })

    # --- Publications visibles (publiques + personnelles + amis) ---
    publications = Publication.objects.filter(
        Q(visibilite='public') |
        Q(auteur=request.user) |
        Q(visibilite='amis', auteur__in=getattr(request.user, 'amis', lambda: []).all() if hasattr(request.user, 'amis') else [])
    ).distinct().order_by('-created_at')

    # --- Filtrage par type de contenu ---
    if content_type == 'image':
        publications = publications.filter(medias__type='image').distinct()
    elif content_type == 'video':
        publications = publications.filter(medias__type='video').distinct()
    elif content_type == 'programme':
        publications = publications.filter(type='programme').distinct()

    # --- Marquer les publications aimées ---
    for pub in publications:
        pub.liked_by_user = pub.likes.filter(id=request.user.id).exists()
        pub.media_list = pub.medias.all()[:4]  # limite à 4 médias
        pub.extra_media_count = max(0, pub.medias.count() - 4)

    # ✅ Suppression complète de la pagination : affichage de toutes les publications
    return render(request, 'eglise/accueil.html', {
        'content_type': content_type,
        'notifications': notifications,
        'publications': publications,  # plus de page_obj
    })

from django.contrib.auth import get_user_model

User = get_user_model()  # Utiliser le CustomUser

from django.contrib import messages
from .models import Profile
import random

User = get_user_model()  # Utiliser le CustomUser


# =========================== 
# Inscription
# ===========================

def inscription(request):
    if request.user.is_authenticated:
        return redirect('eglise:accueil')

    if request.method == 'POST':
        form = InscriptionForm(request.POST, request.FILES)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            conf_password = form.cleaned_data['conf_password']
            phone = form.cleaned_data.get('phone')

            # Vérification des mots de passe
            if password != conf_password:
                form.add_error('conf_password', "Les mots de passe ne correspondent pas")

            # Vérification du nom d'utilisateur
            elif User.objects.filter(username=username).exists():
                form.add_error('username', "Ce nom d'utilisateur est déjà utilisé")


            # Vérification du numéro de téléphone
            elif User.objects.filter(phone=phone).exists():
                # Récupérer l'utilisateur existant
                existing_user = User.objects.get(phone=phone)
                # Message avec lien vers la page de connexion

            # Vérification du numéro de téléphone (dans Profile, pas User)
            elif Profile.objects.filter(phone=phone).exists():

                messages.error(
                    request,
                    f"Ce numéro est déjà utilisé pour un autre compte. "
                    f"<a href='{request.build_absolute_uri('/connexion/')}'>Se connecter</a>"
                )

            else:

                # Création de l'utilisateur Django (CustomUser)
                user = User.objects.create_user(username=username, password=password, phone=phone)

                # Création de l'utilisateur Django (User n'a PAS phone)
                user = User.objects.create_user(username=username, password=password)


                # Création du profil
                profile = form.save(commit=False)
                profile.user = user


                profile.phone = phone   # <- on place le numéro ici
                profile.continent = request.POST.get('continent', '')
                profile.pays = request.POST.get('pays', '')
                profile.identite_complete = True

                # Génération du code à 6 chiffres
                verification_code = f"{random.randint(100000, 999999)}"
                profile.verification_code = verification_code
                profile.is_verified = False  # marque le profil comme non vérifié
                profile.save()

                # Ici, envoyer le code par SMS ou email (simulé ici)
                print(f"Code de vérification envoyé à {profile.phone}: {verification_code}")
                # Pour un vrai envoi SMS, utiliser Twilio ou autre API

                # Simulation d'envoi
                print(f"Code de vérification envoyé à {profile.phone}: {verification_code}")


                # Redirection vers la page de confirmation du code
                return redirect('eglise:confirme_code', user_id=profile.id)

    else:
        form = InscriptionForm()

    return render(request, 'eglise/inscription.html', {'form': form})


from django.contrib.auth import get_user_model, login

User = get_user_model()  # Utiliser le CustomUser partout

# ===========================
# Confirmation du code
# ===========================
def confirme_code(request, user_id):
    profile = get_object_or_404(Profile, id=user_id)

    if request.method == 'POST':
        code = request.POST.get('code')
        if code == profile.verification_code:
            profile.is_verified = True
            profile.verification_code = ''
            profile.save()

            # Connexion automatique après vérification
            login(request, profile.user)  # ✅ profile.user est un CustomUser
            request.session['device_active'] = True
            request.session['last_login_time'] = timezone.now().isoformat()

            return redirect('eglise:accueil')
        else:
            from django.contrib import messages
            messages.error(request, "Code incorrect. Veuillez réessayer.")

    return render(request, 'eglise/confirme_code.html', {'profile': profile})


# ===========================
# Connexion / Déconnexion
# ===========================
def connexion(request):
    if request.user.is_authenticated:
        return redirect('eglise:accueil')

    error = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        next_url = request.POST.get('next') or 'eglise:accueil'

        user = authenticate(request, username=username, password=password)  # CustomUser
        if user is not None:
            login(request, user)
            request.session['device_active'] = True
            request.session['last_login_time'] = timezone.now().isoformat()
            return redirect(next_url)
        else:
            error = "Nom d'utilisateur ou mot de passe incorrect"

    next_url = request.GET.get('next', '')
    return render(request, 'eglise/connexion.html', {'error': error, 'next': next_url})

# ===========================
# Déconnexion
# ===========================
def deconnexion(request):
    if 'device_active' in request.session:
        del request.session['device_active']
    if 'last_login_time' in request.session:
        del request.session['last_login_time']

    logout(request)
    return redirect("eglise:inscription")


# ===========================
# Paramètres
# ===========================
@login_required
def parametres(request):
    user = request.user
    profile = user.profile

    if request.method == "POST":
        profile.theme = request.POST.get("theme", "clair")
        profile.notif_messages = bool(request.POST.get("notif_messages"))
        profile.notif_activites = bool(request.POST.get("notif_activites"))
        profile.notif_emails = bool(request.POST.get("notif_emails"))
        profile.notif_push = bool(request.POST.get("notif_push"))
        profile.langue = request.POST.get("langue", "fr")
        profile.flux = request.POST.get("flux", "recent")

        pseudo = request.POST.get("pseudo", user.username)
        bio = request.POST.get("bio", profile.bio)
        user.username = pseudo
        profile.bio = bio

        password = request.POST.get("password")
        if password:
            user.set_password(password)
            update_session_auth_hash(request, user)

        user.save()
        profile.save()
        messages.success(request, "Paramètres enregistrés avec succès !")
        return redirect('eglise:parametres')

    return render(request, "eglise/parametres.html", {"user": user})


# ===========================
# Profil public
# ===========================
def profil_public(request, username):
    User = get_user_model()  # Assure que l'on utilise CustomUser
    try:
        user_profile = User.objects.get(username=username)
    except User.DoesNotExist:
        return redirect('eglise:accueil')

    return render(request, 'eglise/profil_public.html', {'user_profile': user_profile})


User = get_user_model()  # Utiliser CustomUser partout

@login_required
def profil_modification(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('eglise:profil_modification')
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'eglise/profil_modification.html', {'form': form, 'profile': profile})


@login_required
def profil_utilisateur(request, user_id):
    utilisateur = get_object_or_404(User, id=user_id)
    publications = Publication.objects.filter(auteur=utilisateur).order_by('-created_at')

    est_ami = Amitie.objects.filter(
        Q(demandeur=request.user, receveur=utilisateur, statut="accepte") |
        Q(demandeur=utilisateur, receveur=request.user, statut="accepte")
    ).exists()

    chaine = Chaine.objects.filter(auteur=utilisateur).first()
    est_abonne = False
    if chaine:
        est_abonne = Abonnement.objects.filter(utilisateur=request.user, chaine=chaine).exists()

    return render(request, 'eglise/profil_utilisateur.html', {
        'utilisateur': utilisateur,
        'publications': publications,
        'est_ami': est_ami,
        'chaine': chaine,
        'est_abonne': est_abonne,
    })

# -----------------------------------------------------------
# 1️⃣ ENVOYER UNE INVITATION D'AMI
# -----------------------------------------------------------
@login_required
def ajouter_ami(request, user_id):
    utilisateur = get_object_or_404(User, id=user_id)

    if utilisateur == request.user:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': "Tu ne peux pas t'envoyer une invitation à toi-même 😅."})
        messages.warning(request, "Tu ne peux pas t'envoyer une invitation à toi-même 😅.")
        return redirect("eglise:profil_utilisateur", user_id=user_id)

    amitie, created = Amitie.objects.get_or_create(
        demandeur=request.user,
        receveur=utilisateur,
        defaults={"statut": "en_attente"}
    )

    if not created and amitie.statut == "refuse":
        amitie.statut = "en_attente"
        amitie.date_creation = timezone.now()
        amitie.date_reponse = None
        amitie.save()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True})

    messages.success(request, "Invitation envoyée ✔")
    return redirect("eglise:profil_utilisateur", user_id=utilisateur.id)


# -----------------------------------------------------------
# 2️⃣ ACCEPTER UNE INVITATION
# -----------------------------------------------------------
@login_required
def accepter_invitation(request, invitation_id):
    invitation = get_object_or_404(
        Amitie,
        id=invitation_id,
        receveur=request.user,
        statut="en_attente"
    )

    invitation.statut = "accepte"
    invitation.date_reponse = timezone.now()
    invitation.save()

    # Création discussion dans les 2 sens
    Discussion.objects.get_or_create(utilisateur=request.user, correspondant=invitation.demandeur)
    Discussion.objects.get_or_create(utilisateur=invitation.demandeur, correspondant=request.user)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True})

    messages.success(request, "Vous avez accepté l'invitation ✔")
    return redirect("eglise:dialogues")


# -----------------------------------------------------------
# 3️⃣ REFUSER UNE INVITATION
# -----------------------------------------------------------
@login_required
def refuser_invitation(request, invitation_id):
    invitation = get_object_or_404(
        Amitie,
        id=invitation_id,
        receveur=request.user,
        statut="en_attente"
    )

    invitation.statut = "refuse"
    invitation.date_reponse = timezone.now()
    invitation.save()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True})

    messages.info(request, "Invitation refusée.")
    return redirect("eglise:dialogues")


# -----------------------------------------------------------
# 4️⃣ AFFICHAGE DES DIALOGUES + INVITATIONS
# -----------------------------------------------------------
@login_required
def dialogues(request):
    invitations_recues = Amitie.objects.filter(receveur=request.user, statut="en_attente")
    invitations_envoyees = Amitie.objects.filter(demandeur=request.user).exclude(statut="en_attente")
    mes_discussions = Discussion.objects.filter(utilisateur=request.user).select_related("correspondant")

    return render(request, "eglise/dialogues.html", {
        "invitations_recues": invitations_recues,
        "invitations_envoyees": invitations_envoyees,
        "mes_discussions": mes_discussions,
    })


# -----------------------------------------------------------
# 5️⃣ AJOUTER MANUELLEMENT UNE DISCUSSION (optionnel)
# -----------------------------------------------------------
@login_required
def ajouter_discussion(request, user_id):
    correspondant = get_object_or_404(User, id=user_id)
    utilisateur = request.user

    if correspondant == utilisateur:
        messages.warning(request, "Tu ne peux pas discuter avec toi-même 😅.")
        return redirect('eglise:accueil')

    discussion, created = Discussion.objects.get_or_create(utilisateur=utilisateur, correspondant=correspondant)

    if created:
        Discussion.objects.get_or_create(utilisateur=correspondant, correspondant=utilisateur)
        messages.success(request, f"{correspondant.username} a été ajouté à vos discussions ✔.")
    else:
        messages.info(request, "Cette discussion existe déjà.")

    return redirect('eglise:dialogues')


# -----------------------------------------------------------
# 6️⃣ DÉTAIL D'UNE DISCUSSION
# -----------------------------------------------------------
@login_required
def discussion_detail(request, discussion_id=None, user_id=None):
    """
    Affiche le détail d'une discussion.
    - discussion_id : accéder directement à une discussion existante
    - user_id : créer ou récupérer une discussion avec cet utilisateur
    """
    utilisateur = request.user

    # Si user_id est fourni
    if user_id and not discussion_id:
        correspondant = get_object_or_404(User, id=user_id)
        if correspondant == utilisateur:
            messages.warning(request, "Vous ne pouvez pas discuter avec vous-même 😅.")
            return redirect('eglise:dialogues')
        discussion, created = Discussion.objects.get_or_create(utilisateur=utilisateur, correspondant=correspondant)
        Discussion.objects.get_or_create(utilisateur=correspondant, correspondant=utilisateur)
    else:
        # Récupération via discussion_id
        discussion = get_object_or_404(Discussion, id=discussion_id)
        correspondant = discussion.correspondant

    # Récupération des messages
    messages_discussion = Message.objects.filter(
        Q(expediteur=utilisateur, destinataire=correspondant) |
        Q(expediteur=correspondant, destinataire=utilisateur)
    ).order_by('date')

    # Gestion de l'envoi de message
    if request.method == 'POST':
        texte = request.POST.get('message')
        fichier = request.FILES.get('file')
        audio = request.FILES.get('audio')

        if texte:
            Message.objects.create(
                expediteur=utilisateur,
                destinataire=correspondant,
                type='texte',
                contenu=texte
            )
        elif fichier:
            Message.objects.create(
                expediteur=utilisateur,
                destinataire=correspondant,
                type='fichier',
                fichier=fichier
            )
        elif audio:
            Message.objects.create(
                expediteur=utilisateur,
                destinataire=correspondant,
                type='audio',
                fichier=audio
            )
        return redirect(request.path)

    return render(request, "eglise/discussion_detail.html", {
        "discussion": discussion,
        "correspondant": correspondant,
        "messages": messages_discussion,
        "user": utilisateur,
    })
####################################################

@login_required
def notifications(request):
    user = request.user
    profil = user.profile
    notifications = Notification.objects.filter(utilisateur=user)
    
    # Filtrer selon les préférences de l'utilisateur
    if not profil.notif_messages:
        notifications = notifications.exclude(type="message")
    if not profil.notif_activites:
        notifications = notifications.exclude(type="activite")
    if not profil.notif_emails:
        notifications = notifications.exclude(type="email")
    if not profil.notif_push:
        notifications = notifications.exclude(type="push")
    
    notifications = notifications.order_by("-date")

    # Notifications non lues pour le badge (avant de les marquer lues)
    non_lues = notifications.filter(lu=False)

    # MARQUER TOUTES LES NOTIFICATIONS COMME LUES
    notifications.filter(lu=False).update(lu=True)

    return render(request, "eglise/notifications.html", {
        "notifications": notifications,
        "non_lues": non_lues
    })


User = get_user_model()  # Utiliser CustomUser partout

# ===========================
# Recherche
# ===========================
def recherche_eglise(request):
    query = request.GET.get("q", "")
    results_chain = Chaine.objects.filter(nom__icontains=query) if query else []
    results_users = User.objects.filter(username__icontains=query) if query else []

    # Récupérer les publications de chaque utilisateur trouvé
    publications_par_utilisateur = {}
    for user_found in results_users:
        pubs = Publication.objects.filter(auteur=user_found).order_by('-created_at')
        publications_par_utilisateur[user_found.username] = pubs

    return render(request, "eglise/recherche.html", {
        "query": query,
        "results_chain": results_chain,
        "results_users": results_users,
        "publications_par_utilisateur": publications_par_utilisateur,
    })


def search_view(request):
    query = request.GET.get('q', '').strip()
    results_users = []
    results_chain = []

    if query:
        # Utilisateurs
        results_users = User.objects.filter(
            Q(username__icontains=query) |
            Q(profile__nom__icontains=query) |
            Q(profile__prenom__icontains=query) |
            Q(profile__pseudo_publique__icontains=query)
        ).distinct()

        # Chaînes
        results_chain = Chaine.objects.filter(
            Q(nom__icontains=query) |
            Q(description__icontains=query)
        ).distinct()

    context = {
        'query': query,
        'results_users': results_users,
        'results_chain': results_chain
    }
    return render(request, 'eglise/search_results.html', context)


# ===========================
# Pages secondaires
# ===========================
def actus(request):
    return render(request, 'eglise/actus.html')


# ===========================
# Publications
# ===========================
@login_required
def creer_publication(request):
    if request.method == 'POST':
        pub_form = PublicationForm(request.POST, request.FILES)
        media_form = MediaForm(request.POST, request.FILES)

        if pub_form.is_valid() and media_form.is_valid():
            publication = pub_form.save(commit=False)
            publication.auteur = request.user
            publication.save()

            fichiers = request.FILES.getlist('fichiers')
            for f in fichiers:
                if f.content_type.startswith('image/'):
                    type_media = 'image'
                elif f.content_type.startswith('video/'):
                    type_media = 'video'
                else:
                    type_media = 'document'
                Media.objects.create(
                    publication=publication,
                    fichier=f,
                    type=type_media
                )

            return redirect('eglise:accueil')
    else:
        pub_form = PublicationForm()
        media_form = MediaForm()

    return render(request, 'eglise/creer_publication.html', {
        'pub_form': pub_form,
        'media_form': media_form
    })


User = get_user_model()  # Utiliser CustomUser partout

# ===========================
# Liste des publications
# ===========================
@login_required
def liste_publications(request):
    publications = Publication.objects.all().order_by('-created_at')
    return render(request, "eglise/liste_publications.html", {
        "publications": publications
    })


# ===========================
# Détails d’une publication
# ===========================
@login_required
def details_publication(request, pk):
    publication = get_object_or_404(Publication, pk=pk)
    commentaires = Commentaire.objects.filter(publication=publication).order_by('created_at')
    liked_by_user = publication.likes.filter(id=request.user.id).exists()

    if request.method == "POST":
        contenu = request.POST.get("contenu")
        if contenu and contenu.strip():
            Commentaire.objects.create(
                publication=publication,
                auteur=request.user,
                contenu=contenu
            )
            if publication.auteur != request.user:
                Notification.objects.create(
                    utilisateur=publication.auteur,
                    message=f"{request.user.username} a commenté votre publication."
                )
            return redirect("eglise:details_publication", pk=pk)

    return render(request, "eglise/details_publication.html", {
        "publication": publication,
        "commentaires": commentaires,
        "liked_by_user": liked_by_user
    })


# ===========================
# Filtrage par type de média
# ===========================
def filtre_publications(request, filtre):
    if filtre == "all":
        publications = Publication.objects.all().order_by("-created_at")
    elif filtre == "image":
        publications = Publication.objects.filter(medias__type="image").distinct().order_by("-created_at")
    elif filtre == "video":
        publications = Publication.objects.filter(medias__type="video").distinct().order_by("-created_at")
    elif filtre == "programme":
        publications = Publication.objects.filter(categorie="programme").order_by("-created_at")
    else:
        publications = Publication.objects.none()

    for pub in publications:
        pub.media_list = pub.medias.all()[:4]
        pub.extra_media_count = max(0, pub.medias.count() - 4)

    return render(request, "eglise/espace_milieu.html", {
        "publications": publications
    })


from django.shortcuts import render, redirect, get_object_or_404 
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from django.utils.text import slugify
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages

from .models import (
    Chaine,
    Video,
    PublicationTexte,
    Abonnement,
    Channel,
    Publication,
    PublicationChaine,
)

from .forms import (
    ChaineForm,
    VideoForm,
    PublicationTexteForm,
    ChannelForm,
)


# ======================
# LISTE DES CHAINES
# ======================

def liste_chaines(request):
    chaines = Chaine.objects.all().order_by("nom")
    return render(request, "eglise/chaines/liste.html", {"chaines": chaines})


# ======================
# VUE GENERALE (ESPACE PUBLIC)
# - Affiche les vidéos publiées publiées depuis moins de 3 jours
# ======================

def vue_generale(request):
    trois_jours = timezone.now() - timedelta(days=3)
    videos = (
        Video.objects.filter(created_at__gte=trois_jours, published=True)
        .select_related("chaine", "chaine__auteur")
        .order_by("-created_at")
    )

    user_chaine = None
    if request.user.is_authenticated:
        user_chaine = Chaine.objects.filter(auteur=request.user).first()

    return render(request, "eglise/vue_generale.html", {
        "videos": videos,
        "user_chaine": user_chaine,
    })
    
    
# ======================
# DETAIL CHAINE
# ======================

def detail_chaine(request, username):
    chaine = get_object_or_404(Chaine, username=username)
    videos = Video.objects.filter(chaine=chaine).order_by("-created_at")

    user_chaine = None
    if request.user.is_authenticated:
        user_chaine = Chaine.objects.filter(auteur=request.user).first()

    return render(request, "eglise/chaines/detail.html", {
        "chaine": chaine,
        "videos": videos,
        "user_chaine": user_chaine,
    })


# ======================
# MODIFIER CHAINE
# ======================

@login_required
def modifier_chaine(request, username):
    chaine = get_object_or_404(Chaine, username=username, auteur=request.user)

    if request.method == "POST":
        form = ChaineForm(request.POST, request.FILES, instance=chaine)
        if form.is_valid():
            form.save()
            messages.success(request, "Votre chaîne a été modifiée.")
            return redirect("eglise:detail_chaine", username=chaine.username)

    form = ChaineForm(instance=chaine)
    return render(request, "eglise/chaines/modifier.html", {"form": form, "chaine": chaine})


# ======================
# PUBLIER TEXTE
# ======================

@login_required
def publier_texte(request, username):
    chaine = get_object_or_404(Chaine, username=username)

    if request.method == "POST":
        contenu = request.POST.get("contenu")
        if contenu:
            PublicationTexte.objects.create(chaine=chaine, auteur=request.user, contenu=contenu)
        return redirect("eglise:detail_chaine", username=username)

    return render(request, "eglise/chaine/publier_texte.html", {"chaine": chaine})


@login_required
def upload_video(request, username):
    # L'utilisateur ne peut publier que sur SA chaîne
    chaine = get_object_or_404(Chaine, username=username, auteur=request.user)

    if request.method == "POST":
        fichier = request.FILES.get("video")  # champ correct du formulaire
        titre = request.POST.get("titre", "")
        description = request.POST.get("description", "")

        if not fichier:
            messages.error(request, "Veuillez sélectionner une vidéo.")
            return redirect("eglise:upload_video", username=username)

        EXT = ["mp4", "mov", "avi", "mkv", "webm"]
        ext = fichier.name.split(".")[-1].lower()

        if ext not in EXT:
            messages.error(request, "Format non autorisé ! Seules les vidéos sont acceptées.")
            return redirect("eglise:upload_video", username=username)

        # ENREGISTRE BIEN DANS video_file (champ correct)
        Video.objects.create(
            chaine=chaine,
            titre=titre,
            description=description,
            video_file=fichier,
            published=True,
        )

        messages.success(request, "Vidéo publiée avec succès ! Elle sera visible 3 jours.")
        return redirect("eglise:detail_chaine", username=username)

    return render(request, "eglise/videos/upload.html", {"chaine": chaine})

@property
def is_expired(self):
    return self.created_at < timezone.now() - timedelta(days=3)


# ======================
# REDIRECTION AUTOMATIQUE POUR PUBLIER
# ======================

@login_required
def choix_chaine_pour_publier(request):
    chaine = Chaine.objects.filter(auteur=request.user).first()

    if not chaine:
        messages.error(request, "Vous devez d'abord créer une chaîne.")
        return redirect("eglise:chaine_creer")

    return redirect("eglise:upload_video", username=chaine.username)


# ======================
# LIKE PUBLICATION
# ======================

@login_required
def toggle_like(request, pub_id):
    publication = get_object_or_404(Publication, id=pub_id)

    if request.user in publication.likes.all():
        publication.likes.remove(request.user)
    else:
        publication.likes.add(request.user)

    return redirect("eglise:details_publication", pk=publication.id)


# ======================
# SUPPRIMER CHAINE
# ======================

@login_required
def supprimer_chaine(request, chaine_id):
    chaine = get_object_or_404(Chaine, id=chaine_id, auteur=request.user)

    if request.method == "POST":
        chaine.delete()
        messages.success(request, "Votre chaîne a été supprimée.")
        return redirect("eglise:liste_chaines")

    return redirect("eglise:detail_chaine", username=chaine.username)


# ======================
# SUPPRIMER VIDEO
# ======================

@login_required
def supprimer_video(request, video_id):
    video = get_object_or_404(Video, id=video_id, chaine__auteur=request.user)

    if request.method == "POST":
        video.delete()
        messages.success(request, "Vidéo supprimée.")
        return redirect("eglise:liste_chaines")

    return redirect("eglise:detail_chaine", username=video.chaine.username)


# ======================
# LIKE VIDEO (AJAX)
# ======================

@login_required
def like_video(request, video_id):
    video = get_object_or_404(Video, id=video_id)

    if request.user in video.likes.all():
        video.likes.remove(request.user)
        liked = False
    else:
        video.likes.add(request.user)
        liked = True

    return JsonResponse({
        "liked": liked,
        "total_likes": video.likes.count()
    })

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.text import slugify
from django import forms

from .models import Chaine, Video

# Try to import your real publication form; if it doesn't exist, provide a minimal fallback.
try:
    from .forms import PublicationForm as PubForm
except Exception:
    class PubForm(forms.Form):
        # minimal fields so {{ pub_form.as_p }} renders safely
        titre = forms.CharField(required=False)
        description = forms.CharField(widget=forms.Textarea, required=False)


@login_required
def chaine_creer(request):
    """
    Page pour créer / afficher la chaîne de l'utilisateur.
    - Affiche la chaîne et ses vidéos si la chaîne existe.
    - Permet de créer la chaîne via POST.
    Note: la popup de publication dans le template attend un 'pub_form' dans le contexte.
    """

    user_chaine = Chaine.objects.filter(auteur=request.user).first()
    pub_form = PubForm()

    # Si l'utilisateur a déjà une chaîne, afficher la page avec ses vidéos
    if user_chaine:
        videos = Video.objects.filter(chaine=user_chaine).order_by('-created_at')
        return render(request, "eglise/chaine_creer.html", {
            "user_chaine": user_chaine,
            "videos": videos,
            "pub_form": pub_form,
        })

    # Création de la chaîne (POST)
    if request.method == "POST":
        # Le template actuel envoie name="name" (et non "nom")
        nom = request.POST.get("name") or request.POST.get("nom") or ""
        username = request.POST.get("username") or request.user.username
        bio = request.POST.get("bio", "")
        avatar = request.FILES.get("avatar")
        banner = request.FILES.get("banner")

        # Générer un slug/username unique
        base_slug = slugify(username or nom) or slugify(request.user.username)
        final_slug = base_slug
        counter = 1
        while Chaine.objects.filter(username=final_slug).exists():
            final_slug = f"{base_slug}-{counter}"
            counter += 1

        chaine = Chaine.objects.create(
            auteur=request.user,
            nom=nom or request.user.get_full_name() or request.user.username,
            username=final_slug,
            bio=bio,
            avatar=avatar,
            banner=banner,
        )

        messages.success(request, "Votre chaîne a été créée.")
        # Rediriger en GET vers la même page pour éviter repost et garantir que la liste videos est rechargée
        return redirect("eglise:chaine_creer")

    # Méthode GET et pas de chaîne
    return render(request, "eglise/chaine_creer.html", {
        "user_chaine": None,
        "videos": [],
        "pub_form": pub_form,
    })


@login_required
def videos_publier(request):
    """
    Traitement du formulaire de publication des vidéos.
    - Attendu: le formulaire POST contient des fichiers dans 'fichiers'
      et éventuellement des champs 'titre'/'titre' et 'description' (ou 'title'/'desc').
    - On détecte dynamiquement le nom du champ fichier dans le modèle Video
      (video_file / fichier / file), ainsi que le nom des champs titre/description.
    - Après création, on redirige vers la page chaine_creer (où la liste 'videos' est affichée).
    """
    if request.method == "POST":
        user_chaine = Chaine.objects.filter(auteur=request.user).first()
        if not user_chaine:
            messages.error(request, "Vous devez créer une chaîne avant de publier.")
            return redirect("eglise:chaine_creer")

        # Récupère les fichiers envoyés
        fichiers = request.FILES.getlist("fichiers")

        # Détecter les noms de champs du modèle Video
        video_field_name = None
        titre_field_name = None
        desc_field_name = None

        model_field_names = [f.name for f in Video._meta.get_fields() if hasattr(f, "name")]

        for candidate in ("video_file", "fichier", "file"):
            if candidate in model_field_names:
                video_field_name = candidate
                break

        for candidate in ("titre", "title",):
            if candidate in model_field_names:
                titre_field_name = candidate
                break

        for candidate in ("description", "desc", "body"):
            if candidate in model_field_names:
                desc_field_name = candidate
                break

        # Récupérer valeurs titre/description depuis POST (support plusieurs noms)
        title_value = request.POST.get("titre") or request.POST.get("title") or request.POST.get("titre_pub") or ""
        desc_value = request.POST.get("description") or request.POST.get("desc") or request.POST.get("body") or ""

        created_any = False
        for f in fichiers:
            if not video_field_name:
                # Aucun champ de fichier reconnu : abort
                messages.error(request, "Le modèle Video n'a pas de champ de fichier attendu (video_file/fichier/file).")
                return redirect("eglise:chaine_creer")

            kwargs = {
                "chaine": user_chaine,
                video_field_name: f,
            }
            if titre_field_name:
                kwargs[titre_field_name] = title_value
            if desc_field_name:
                kwargs[desc_field_name] = desc_value

            # Create the Video
            Video.objects.create(**kwargs)
            created_any = True

        if created_any:
            messages.success(request, "🎉 Vidéo(s) publiée(s) avec succès !")
        else:
            messages.warning(request, "Aucun fichier vidéo reçu.")

        # Rediriger vers la page chaîne pour rafraîchir la liste
        return redirect("eglise:chaine_creer")

    # Si GET, afficher page de gestion (facultatif) : on montre les vidéos de la chaîne
    user_chaine = Chaine.objects.filter(auteur=request.user).first()
    videos = Video.objects.filter(chaine=user_chaine).order_by("-created_at") if user_chaine else []

    return render(request, "eglise/videos/videos_publier.html", {
        "videos": videos,
        "user_chaine": user_chaine,
    })

from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Chaine

@login_required
def toggle_abonnement(request, username):
    chaine = get_object_or_404(Chaine, username=username)

    if request.user in chaine.abonnes.all():
        chaine.abonnes.remove(request.user)
    else:
        chaine.abonnes.add(request.user)

    return redirect("detail_chaine", username=username)


from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def mon_espace(request):
    """
    Page espace utilisateur :
    - Ses informations
    - Ses chaînes
    - Ses publications
    """
    utilisateur = request.user

    # Si tu veux afficher les chaînes créées par l'utilisateur
    chaines = getattr(utilisateur, "chaine_set", None)
    if chaines:
        chaines = chaines.all()

    # Si tu veux afficher les publications créées par l'utilisateur
    publications = getattr(utilisateur, "publication_set", None)
    if publications:
        publications = publications.all()

    context = {
        "utilisateur": utilisateur,
        "chaines": chaines,
        "publications": publications,
    }

    return render(request, "eglise/mon_espace.html", context)


########################################################
########################################################
########################################################
########################################################
# ===========================
# Détails publication
# ===========================
def publication_detail(request, pub_id):
    publication = get_object_or_404(Publication, id=pub_id)
    auteur = publication.auteur
    publications_auteur = Publication.objects.filter(auteur=auteur).order_by("-date_creation")
    return render(
        request,
        "eglise/publication_detail.html",
        {
            "publication": publication,
            "auteur": auteur,
            "publications_auteur": publications_auteur,
        },
    )


# ===========================
# Discussions & Messages
# ===========================
@login_required
def ajouter_commentaire(request, pk):
    publication = get_object_or_404(Publication, pk=pk)

    if request.method == "POST":
        contenu = request.POST.get("contenu")
        if contenu and contenu.strip():
            Commentaire.objects.create(
                publication=publication,
                auteur=request.user,
                contenu=contenu
            )

            if publication.auteur != request.user:
                Notification.objects.create(
                    utilisateur=publication.auteur,
                    message=f"{request.user.username} a commenté votre publication."
                )

                envoyer_notification_push(
                    utilisateur=publication.auteur,
                    titre="Nouveau commentaire",
                    corps=f"{request.user.username} a commenté votre publication."
                )

    return redirect("eglise:details_publication", pk=pk)



def envoyer_notification_push(utilisateur, titre, corps):
    token = getattr(utilisateur, "device_token", None)
    if not token:
        profile = getattr(utilisateur, "profile", None)
        if profile:
            token = getattr(profile, "device_token", None)

    if not token:
        return False

    api_key = getattr(settings, "FCM_API_KEY", None)
    if not api_key:
        return False

    push_service = FCMNotification(api_key=api_key)
    try:
        push_service.notify_single_device(
            registration_id=token,
            message_title=titre,
            message_body=corps
        )
        return True
    except Exception:
        return False
    
    

User = get_user_model()


@login_required
def discussion_detail(request, user_id):
    utilisateur = request.user

    # Récupérer l'utilisateur ciblé
    cible = get_object_or_404(User, id=user_id)

    # Vérifier si discussion existe
    discussion = Discussion.objects.filter(
        Q(utilisateur=utilisateur, correspondant=cible) |
        Q(utilisateur=cible, correspondant=utilisateur)
    ).first()

    # Sinon créer
    if not discussion:
        discussion = Discussion.objects.create(utilisateur=utilisateur, correspondant=cible)

    # Correspondant réel
    correspondant = discussion.correspondant if discussion.utilisateur == utilisateur else discussion.utilisateur

    # Marquer messages du correspondant comme lus
    discussion.messages.filter(expediteur=correspondant, lu=False).update(lu=True)

    # ------------------------------
    #  ENVOI DE MESSAGE
    # ------------------------------
    if request.method == "POST":
        message_text = request.POST.get('message', '').strip()
        # on récupère maintenant potentiellement plusieurs fichiers
        fichiers = request.FILES.getlist('file')
        audio = request.FILES.get('audio')

        # Message texte
        if message_text:
            Message.objects.create(
                discussion=discussion,
                expediteur=utilisateur,
                contenu=message_text,
                type='texte'
            )

        # Messages fichiers (plusieurs possibles)
        for fichier in fichiers:
            if not fichier:
                continue
            ext = fichier.name.split('.')[-1].lower()

            if ext in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
                type_msg = 'image'
            elif ext in ['mp4', 'mov', 'webm', 'avi', 'mkv']:
                type_msg = 'video'
            elif ext in ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt']:
                type_msg = 'document'
            elif ext in ['mp3', 'wav', 'ogg', 'm4a']:
                type_msg = 'audio'
            else:
                type_msg = 'fichier'

            Message.objects.create(
                discussion=discussion,
                expediteur=utilisateur,
                fichier=fichier,
                type=type_msg
            )

        # Audio direct (si envoyé séparément)
        if audio:
            Message.objects.create(
                discussion=discussion,
                expediteur=utilisateur,
                fichier=audio,
                type='audio'
            )

        # Notification push (on notifie le correspondant)
        envoyer_notification_push(
            correspondant,
            f"Nouveau message de {utilisateur.username}",
            message_text or "Fichier/Audio reçu"
        )

        return redirect('eglise:discussion_detail_user', user_id=correspondant.id)

    # ------------------------------
    #  RÉCUPÉRATION DES MESSAGES
    # ------------------------------
    messages_list = list(Message.objects.filter(discussion=discussion).order_by('date_envoye'))

    # Déterminer front_type
    for msg in messages_list:
        if getattr(msg, 'fichier', None):
            ext = msg.fichier.name.split('.')[-1].lower()

            if ext in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
                msg.front_type = 'image'
            elif ext in ['mp4', 'mov', 'webm', 'avi', 'mkv']:
                msg.front_type = 'video'
            elif ext in ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt']:
                msg.front_type = 'document'
                msg.full_url = request.build_absolute_uri(msg.fichier.url)
            elif ext in ['mp3', 'wav', 'ogg', 'm4a']:
                msg.front_type = 'audio'
            else:
                msg.front_type = 'fichier'
        else:
            msg.front_type = 'texte'

    # ------------------------------
    #  RÉCUPÉRATION DES APPELS
    # ------------------------------
    appels_list = Appel.objects.filter(
        Q(emetteur=utilisateur, recepteur=correspondant) |
        Q(emetteur=correspondant, recepteur=utilisateur)
    ).order_by('-date_creation')

    for appel in appels_list:
        fake_msg = Message(id=None)
        fake_msg.front_type = 'appel'
        fake_msg.date_envoye = appel.date_creation

        if fake_msg.date_envoye and timezone.is_naive(fake_msg.date_envoye):
            fake_msg.date_envoye = timezone.make_aware(fake_msg.date_envoye, timezone.get_current_timezone())

        fake_msg.statut = appel.statut
        messages_list.append(fake_msg)

    # ------------------------------
    #  TRI FINAL PAR DATE
    # ------------------------------
    def get_message_date(m):
        dt = getattr(m, 'date_envoye', None)
        if dt is None:
            return timezone.make_aware(datetime.min, timezone.get_current_timezone())
        if timezone.is_naive(dt):
            return timezone.make_aware(dt, timezone.get_current_timezone())
        return dt

    messages_list = sorted(messages_list, key=get_message_date)

    # ------------------------------
    #  FORMAT HEURE HH:MM
    # ------------------------------
    for msg in messages_list:
        dt = getattr(msg, 'date_envoye', None)
        if dt:
            if timezone.is_naive(dt):
                dt = timezone.make_aware(dt, timezone.get_current_timezone())
            msg.time_str = dt.strftime('%H:%M')
        else:
            msg.time_str = ''

        # compatibilité template (si tu utilises {{ msg.date_envoi }})
        msg.date_envoi = getattr(msg, 'date_envoye', None)

    return render(request, 'eglise/discussion_detail.html', {
        'discussion': discussion,
        'correspondant': correspondant,
        'messages': messages_list,
    })
    
@login_required
def mes_discussions_view(request):
    utilisateur = request.user

    # --- Invitations reçues en attente (jaune) ---
    invitations_recues_qs = Amitie.objects.filter(
        receveur=utilisateur, statut="en_attente"
    ).select_related('demandeur')
    invitations_recues_count = invitations_recues_qs.count()
    invitations_recues = invitations_recues_qs

    # --- Invitations refusées par les autres (rouge) ---
    invitations_refusees_qs = Amitie.objects.filter(
        demandeur=utilisateur, statut="refuse"
    ).select_related('receveur')
    invitations_refusees_count = invitations_refusees_qs.count()
    invitations_refusees = invitations_refusees_qs

    # --- Discussions existantes ---
    mes_discussions = Discussion.objects.filter(
        Q(utilisateur=utilisateur) | Q(correspondant=utilisateur)
    ).distinct().order_by('-id')

    for d in mes_discussions:
        # Déterminer correctement le correspondant
        d.correspondant = d.utilisateur if d.utilisateur != utilisateur else d.correspondant

        # Dernier message
        dernier_message = d.messages.order_by('-date_envoye').first()
        d.dernier_message = dernier_message if dernier_message else None
        d.dernier_message_date = dernier_message.date_envoye if dernier_message else None

        # --- Badge : messages non lus ---
        # Compte uniquement les messages envoyés par le correspondant à l'utilisateur connecté
        d.non_lus_count = d.messages.filter(
            expediteur=d.correspondant,
            lu=False
        ).count()

        # Invitation jaune
        d.correspondant.has_new_invitation = Amitie.objects.filter(
            demandeur=d.correspondant, receveur=utilisateur, statut="en_attente"
        ).exists()

        # Invitation rouge
        d.correspondant.has_refused = Amitie.objects.filter(
            demandeur=utilisateur, receveur=d.correspondant, statut="refuse"
        ).exists()

    return render(request, 'eglise/dialogues.html', {
        'mes_discussions': mes_discussions,
        'invitations_recues_count': invitations_recues_count,
        'invitations_recues': invitations_recues,
        'invitations_refusees_count': invitations_refusees_count,
        'invitations_refusees': invitations_refusees,
    })


@csrf_exempt
@login_required
def upload_message_file(request, discussion_id):
    fichier = request.FILES.get('fichier')
    if not fichier:
        return JsonResponse({'error': 'Aucun fichier reçu'}, status=400)

    # --- Déterminer le type de fichier ---
    ext = fichier.name.split('.')[-1].lower()
    if ext in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
        type_message = 'image'
    elif ext in ['mp4', 'mov', 'webm', 'avi', 'mkv']:
        type_message = 'video'
    elif ext in ['mp3', 'wav', 'ogg', 'm4a']:
        type_message = 'audio'
    elif ext in ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt']:
        type_message = 'document'
    else:
        type_message = 'fichier'

    # --- Création du message ---
    msg = Message.objects.create(
        discussion_id=discussion_id,
        expediteur=request.user,
        fichier=fichier,
        type=type_message
    )

    # --- Notification pour le destinataire ---
    discussion = msg.discussion
    destinataire = discussion.correspondant if discussion.utilisateur == request.user else discussion.utilisateur
    envoyer_notification_push(
        destinataire,
        f"Nouveau fichier de {request.user.username}",
        f"Type : {type_message}"
    )

    # --- Retour JSON avec URL du fichier et type pour le front-end ---
    return JsonResponse({'fichier_url': msg.fichier.url, 'type': msg.type})


# eglise/views.py

# -----------------------------------------------------------
# APPELS AUDIO / VIDEO
# -----------------------------------------------------------

@login_required
def audio_appel(request, user_id):
    """
    Lance un appel audio vers un utilisateur identifié par user_id.
    Crée un objet Appel avec statut 'en_attente' et renvoie la page audio.
    """
    correspondant = get_object_or_404(User, id=user_id)
    appel = Appel.objects.create(
        emetteur=request.user,
        recepteur=correspondant,
        type_appel='audio',
        statut='en_attente',
    )
    return render(request, 'eglise/audio_appel.html', {
        'correspondant': correspondant,
        'appel_id': appel.id
    })


@login_required
def video_appel(request, user_id):
    """
    Lance un appel vidéo vers un utilisateur identifié par user_id.
    Crée un objet Appel avec statut 'en_attente' et renvoie la page vidéo.
    """
    correspondant = get_object_or_404(User, id=user_id)
    appel = Appel.objects.create(
        emetteur=request.user,
        recepteur=correspondant,
        type_appel='video',
        statut='en_attente',
    )
    return render(request, 'eglise/video_appel.html', {
        'correspondant': correspondant,
        'appel_id': appel.id
    })

# --- envoyer invitation depuis un popup "Ajouter à la discussion" ---
@login_required
def envoyer_invitation(request, user_id):
    """A envoie une invitation à B."""
    demandeur = request.user
    receveur = get_object_or_404(User, id=user_id)

    if demandeur == receveur:
        return JsonResponse({'error': "Impossible de s'inviter soi-même."}, status=400)

    # Vérifier s'il existe déjà une invitation ou amitié acceptée
    existing = Amitie.objects.filter(
        Q(demandeur=demandeur, receveur=receveur) | Q(demandeur=receveur, receveur=demandeur)
    ).first()

    if existing:
        # si déjà accepté
        if existing.statut == "accepte":
            return JsonResponse({'status': 'already_friends'}, status=200)
        # si en attente, renvoyer info
        if existing.statut == "en_attente":
            return JsonResponse({'status': 'already_pending'}, status=200)
        # si refusée, on peut recréer/mettre à jour la demande
        if existing.statut == "refuse":
            existing.demandeur = demandeur
            existing.receveur = receveur
            existing.statut = "en_attente"
            existing.created_at = timezone.now()
            existing.save()
            envoyer_notification_push(receveur, f"Nouvelle invitation de {demandeur.username}", "")
            return JsonResponse({'status': 'resent'}, status=200)

    # créer nouvelle invitation
    inv = Amitie.objects.create(demandeur=demandeur, receveur=receveur, statut="en_attente")
    envoyer_notification_push(receveur, f"Nouvelle invitation de {demandeur.username}", "")
    return JsonResponse({'status': 'sent', 'invitation_id': inv.id}, status=201)


# --- Accepter une invitation ---
@login_required
def accepter_invitation(request, invitation_id):
    invitation = get_object_or_404(Amitie, id=invitation_id, receveur=request.user)
    if invitation.statut == "accepte":
        messages.info(request, "Invitation déjà acceptée.")
        return redirect('eglise:mes_discussions_view')

    with transaction.atomic():
        invitation.statut = "accepte"
        invitation.accepted_at = timezone.now() if hasattr(invitation, 'accepted_at') else timezone.now()
        invitation.save()

        # Créer discussions dans les deux sens s'il n'y en a pas encore
        u1 = invitation.demandeur
        u2 = invitation.receveur

        # Fonction utilitaire minimale ici
        def ensure_discussion(a, b):
            d = Discussion.objects.filter(Q(utilisateur=a, correspondant=b) | Q(utilisateur=b, correspondant=a)).first()
            if not d:
                Discussion.objects.create(utilisateur=a, correspondant=b)

        ensure_discussion(u1, u2)
        ensure_discussion(u2, u1)

    # Notifications
    envoyer_notification_push(invitation.demandeur, f"{request.user.username} a accepté votre invitation", "")
    messages.success(request, f"Vous avez accepté l'invitation de {invitation.demandeur.username}.")
    return redirect('eglise:mes_discussions_view')

# --- Refuser une invitation ---
@login_required
def refuser_invitation(request, invitation_id):
    invitation = get_object_or_404(Amitie, id=invitation_id, receveur=request.user)
    if invitation.statut == "refuse":
        messages.info(request, "Invitation déjà refusée.")
        return redirect('eglise:mes_discussions_view')

    invitation.statut = "refuse"
    invitation.refused_at = timezone.now() if hasattr(invitation, 'refused_at') else timezone.now()
    if hasattr(invitation, 'attempts'):
        invitation.attempts = (invitation.attempts or 0) + 1
    invitation.save()

    # Notification push pour le demandeur
    envoyer_notification_push(invitation.demandeur, f"Votre invitation a été refusée par {request.user.username}", "")

    # Message côté utilisateur courant en rouge
    messages.error(request, f"Vous avez refusé l'invitation de {invitation.demandeur.username}.")

    return redirect('eglise:mes_discussions_view')

@login_required
def renvoyer_invitation(request, user_id):
    utilisateur = request.user
    try:
        receveur = User.objects.get(id=user_id)
        # Supprimer l’invitation refusée précédente si elle existe
        Amitie.objects.filter(demandeur=utilisateur, receveur=receveur, statut='refuse').delete()
        # Créer une nouvelle invitation
        Amitie.objects.create(demandeur=utilisateur, receveur=receveur, statut='en_attente')
        messages.success(request, f"Invitation renvoyée à {receveur.username}.")
    except User.DoesNotExist:
        messages.error(request, "Utilisateur introuvable.")
    return redirect('eglise:mes_discussions_view')



User = get_user_model()  # CustomUser

@login_required
def annuler_invitation(request, user_id):
    """
    Annule une invitation envoyée par l'utilisateur connecté vers un autre utilisateur.
    Peut être appelée via GET ou POST (pour compatibilité avec le bouton dans le template).
    """
    receveur = get_object_or_404(User, id=user_id)

    # Chercher invitation en attente
    invitation = Amitie.objects.filter(
        demandeur=request.user,
        receveur=receveur,
        statut='en_attente'
    ).first()

    if invitation:
        invitation.delete()
        messages.success(request, f"Invitation annulée pour {receveur.username}.")
    else:
        messages.info(request, "Aucune invitation en attente à annuler.")

    # Redirection vers la liste des discussions
    return redirect('eglise:mes_discussions_view')

from django.shortcuts import redirect

@login_required
def discussion_detail_user(request, utilisateur_id):
    utilisateur = request.user
    correspondant = get_object_or_404(User, id=utilisateur_id)

    # Récupérer ou créer la discussion
    discussion, created = Discussion.objects.get_or_create(
        utilisateur=min(utilisateur, correspondant),
        correspondant=max(utilisateur, correspondant)
    )

    # --- Marquer tous les messages envoyés par le correspondant comme lus ---
    discussion.messages.filter(
        expediteur=correspondant,
        lu=False
    ).update(lu=True)

    messages = discussion.messages.order_by('date_envoye')

    return render(request, 'eglise/discussion_detail_user.html', {
        'discussion': discussion,
        'messages': messages,
        'correspondant': correspondant
    })
    
def upload_video(request, username):
    return HttpResponse("Upload vidéo OK")


import uuid
import random
from datetime import timedelta, date
from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.conf import settings
from django.contrib import messages

from .models import (
    PaiementOrangeMoney,
    ModCoins,
    VIPSubscription,
    DataUsage,
    PubliciteSponsorisee,
    Interaction,
    RewardedAd
)

# =========================================================
# ORANGE MONEY - SIMULATEUR
# =========================================================
@login_required
def payer_orange_money(request):
    """
    Simulation de paiement Orange Money
    Chaque Fc payé → 10 ModCoins crédités
    """
    numero_reception = settings.ORANGE_MONEY_RECEIVER
    montant_min = settings.ORANGE_MONEY_MIN_MONTANT

    if request.method == "POST":
        try:
            montant = float(request.POST.get("montant"))
            numero = request.POST.get("numero").strip()

            if montant < montant_min:
                return render(request, "erreur.html", {"message": f"Le montant minimum est {montant_min} Fc."})

            if numero != numero_reception:
                return render(request, "erreur.html", {"message": f"Veuillez utiliser le numéro Orange Money valide."})

            reference = uuid.uuid4().hex[:12]

            paiement = PaiementOrangeMoney.objects.create(
                user=request.user,
                montant=montant,
                numero=numero,
                reference=reference,
                statut="success"  # simulation immédiate
            )

            # Ajouter ModCoins automatiquement
            coins, _ = ModCoins.objects.get_or_create(user=request.user)
            coins.solde += montant * 10  # 1 Fc → 10 ModCoins
            coins.save()

            messages.success(request, f"Paiement de {montant} Fc réussi ! Vos ModCoins ont été crédités.")
            return render(request, "paiement_success.html", {"montant": montant})

        except ValueError:
            return render(request, "erreur.html", {"message": "Montant invalide."})

    # GET : afficher le formulaire
    return render(request, "payer_orange.html", {
        "numero_reception": numero_reception,
        "montant_min": montant_min
    })


# =========================================================
# ACHETER VIP
# =========================================================
@login_required
def acheter_vip(request, duree):
    """
    duree = 7, 30 ou 90 jours
    Achète ou renouvelle un abonnement VIP
    """
    user = request.user
    vip, created = VIPSubscription.objects.get_or_create(user=user)

    vip.duration_days = duree
    vip.activate()

    messages.success(request, f"VIP activé avec succès pour {duree} jours !")
    return JsonResponse({
        "message": "VIP activé avec succès",
        "expire_le": vip.end_date.strftime("%d/%m/%Y %H:%M"),
        "duree": duree,
    })


# =========================================================
# STATUT VIP
# =========================================================
@login_required
def vip_statut(request):
    """
    Affiche le statut VIP actuel de l'utilisateur
    """
    vip = getattr(request.user, "vip_subscription", None)
    if vip:
        vip.check_expiration()
    return render(request, "vip_statut.html", {"vip": vip})


# =========================================================
# DECORATOR VIP
# =========================================================
def vip_required(view_func):
    """
    Décorateur pour restreindre l'accès aux pages VIP
    """
    def _wrapper(request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return redirect('login')

        vip = getattr(user, 'vip_subscription', None)
        if not vip:
            return render(request, "errors/not_vip.html")

        vip.check_expiration()
        if not vip.is_active:
            return render(request, "errors/not_vip.html")

        return view_func(request, *args, **kwargs)
    return _wrapper


@vip_required
def page_premium(request):
    """
    Exemple d'accès réservé aux VIP
    """
    return render(request, "premium/page.html")


# =========================================================
# CONSOMMATION DE DATA
# =========================================================
@login_required
def ajouter_conso(request):
    """
    Ajouter la consommation de données (MO)
    """
    try:
        mo = float(request.GET.get("mo", 1))
    except ValueError:
        mo = 1

    usage, _ = DataUsage.objects.get_or_create(user=request.user)
    usage.mo_utilises += mo
    usage.save()

    return JsonResponse({"mo_total": usage.mo_utilises})


# =========================================================
# PUBS SPONSORISÉES
# =========================================================
@login_required
def afficher_pubs(request):
    """
    Affiche toutes les pubs actives
    """
    pubs = PubliciteSponsorisee.objects.filter(actif=True)
    return render(request, "pubs.html", {"pubs": pubs})


@login_required
def pubs_a_afficher(request):
    """
    Retourne 3 pubs aléatoires pour l'utilisateur
    """
    pubs = PubliciteSponsorisee.objects.filter(actif=True)
    pubs_choisies = random.sample(list(pubs), min(3, len(pubs)))
    return render(request, "pubs_actives.html", {"pubs": pubs_choisies})


# =========================================================
# INTERACTIONS UTILISATEUR
# =========================================================
@login_required
def enregistrer_interaction(request, action_type, cible_id=None):
    """
    Enregistre une interaction utilisateur et attribue ModCoins si reward
    """
    interaction = Interaction.objects.create(
        user=request.user,
        type=action_type,
        cible_id=cible_id
    )

    rewarded = RewardedAd.objects.filter(actif=True).first()
    coins, _ = ModCoins.objects.get_or_create(user=request.user)

    if rewarded:
        coins.solde += rewarded.coins_bonus
        coins.save()
        messages.info(request, f"Vous avez gagné {rewarded.coins_bonus} ModCoins !")

    return JsonResponse({"status": "ok", "coins": coins.solde})


# =========================================================
# ACTION PREMIUM
# =========================================================
@login_required
def action_premium(request, action_type, cible_id=None):
    """
    Utilise ModCoins pour actions premium, VIP gratuit
    """
    vip = getattr(request.user, 'vip_subscription', None)
    if vip and vip.is_active:
        Interaction.objects.create(
            user=request.user,
            type=action_type,
            cible_id=cible_id
        )
        return JsonResponse({"status": "ok", "coins_restants": "illimité (VIP)"})

    coins, _ = ModCoins.objects.get_or_create(user=request.user)
    cout = 1  # 1 ModCoin par action

    if coins.solde < cout:
        return JsonResponse({"status": "error", "message": "Pas assez de ModCoins"})

    coins.solde -= cout
    coins.save()
    Interaction.objects.create(
        user=request.user,
        type=action_type,
        cible_id=cible_id
    )

    return JsonResponse({"status": "ok", "coins_restants": coins.solde})


# =========================================================
# BONUS QUOTIDIEN
# =========================================================
@login_required
def daily_bonus(request):
    """
    Bonus journalier : 5 ModCoins
    """
    today = date.today()
    if not Interaction.objects.filter(user=request.user, type="daily_bonus", date__date=today).exists():
        coins, _ = ModCoins.objects.get_or_create(user=request.user)
        coins.solde += 5
        coins.save()
        Interaction.objects.create(user=request.user, type="daily_bonus")
        messages.success(request, "Vous avez reçu 5 ModCoins pour votre connexion quotidienne !")
    else:
        messages.info(request, "Vous avez déjà reçu votre bonus aujourd'hui.")

    return redirect("eglise:accueil")
