from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

app_name = "eglise"

urlpatterns = [
    # --- Authentification ---
    path("inscription/", views.inscription, name="inscription"),
    path("connexion/", views.connexion, name="connexion"),
    path("deconnexion/", LogoutView.as_view(next_page="eglise:inscription"), name="deconnexion"),

    # --- Accueil et paramètres ---
    path("", views.accueil, name="accueil"),
    path("parametres/", views.parametres, name="parametres"),

    # --- Profil utilisateur ---
    path("profil/<str:username>/", views.profil_public, name="profil"),
    path("profil/modifier/", views.profil_modification, name="profil_modification"),
    path("profil/<int:user_id>/", views.profil_utilisateur, name="profil_utilisateur"),
    path("ajouter-ami/<int:user_id>/", views.ajouter_ami, name="ajouter_ami"),
    path("publication/<int:pk>/commentaire/", views.ajouter_commentaire, name="ajouter_commentaire"),

    # --- Publications ---
    path("publication/<int:pub_id>/like/", views.toggle_like, name="toggle_like"),
    path("publication/<int:pk>/", views.details_publication, name="details_publication"),
    path("publications/", views.liste_publications, name="liste_publications"),
    path("publications/<str:filtre>/", views.filtre_publications, name="filtre_publications"),

    
    path("notifications/", views.notifications, name="notifications"),

    # --- Dialogues ---
    path("dialogues/", views.mes_discussions_view, name="dialogues"),
    path("annuler-invitation/<int:user_id>/", views.annuler_invitation, name="annuler_invitation"),
    path("renvoyer-invitation/<int:user_id>/", views.renvoyer_invitation, name="renvoyer_invitation"),
    path("discussion/<int:discussion_id>/upload/", views.upload_message_file, name="upload_message_file"),
    path("ajouter_discussion/<int:user_id>/", views.ajouter_discussion, name="ajouter_discussion"),
    path("discussions/", views.mes_discussions_view, name="mes_discussions_view"),

    # --- Discussions directes ---
    path("discussion/user/<int:user_id>/", views.discussion_detail, name="discussion_detail_user"),

    # --- Recherche ---
    path("recherche/", views.recherche_eglise, name="recherche_eglise"),

    # --- Appels ---
    path('audio-appel/<int:user_id>/', views.audio_appel, name='audio_appel'),
    path('video-appel/<int:user_id>/', views.video_appel, name='video_appel'),

    # --- Autres pages ---
    path("actus/", views.actus, name="actus"),
    path("creer-publication/", views.creer_publication, name="creer_publication"),

    # --- Vérification code ---
    path('confirme/<int:user_id>/', views.confirme_code, name='confirme_code'),

    # --- Invitations ---
    path('invitation/send/<int:user_id>/', views.ajouter_ami, name='envoyer_invitation'),
    path('invitation/accept/<int:invitation_id>/', views.accepter_invitation, name='accepter_invitation'),
    path('invitation/reject/<int:invitation_id>/', views.refuser_invitation, name='refuser_invitation'),

    # ======================================================
    # CHAÎNES
    # ======================================================
    path("chaines/", views.liste_chaines, name="liste_chaines"),

    # Création chaîne (POPUP)
    path("chaine/creer/", views.chaine_creer, name="chaine_creer"),
   
    # MAIS juste après :
    

    path('videos/publier/', views.videos_publier, name='videos_publier'),


    # Profil chaîne
    path("chaine/<slug:username>/", views.detail_chaine, name="detail_chaine"),

    # Modifier chaîne
    path("chaine/<slug:username>/modifier/", views.modifier_chaine, name="modifier_chaine"),

    # Supprimer chaîne
    path("chaine/<int:chaine_id>/supprimer/", views.supprimer_chaine, name="supprimer_chaine"),

    # Abonnement
    path("chaine/<slug:username>/toggle-abonnement/", views.toggle_abonnement, name="toggle_abonnement"),

    # ======================================================
    # PUBLICATIONS & VIDEOS
    # ======================================================
    path("publier/", views.choix_chaine_pour_publier, name="choix_chaine_pour_publier"),

    # Upload vidéo avec USERNAME (correct)
    path("upload-video/<slug:username>/", views.upload_video, name="upload_video"),

    # Vidéo actions
    path("video/<int:video_id>/supprimer/", views.supprimer_video, name="supprimer_video"),
    path("video/<int:video_id>/like/", views.like_video, name="like_video"),

    # Publier un texte
    path("chaine/<slug:username>/publier-texte/", views.publier_texte, name="publier_texte"),
    path("chaine/<slug:username>/toggle-abonnement/", views.toggle_abonnement, name="toggle_abonnement"),


    # ======================================================
    # AUTRES
    # ======================================================
    path("videos/", views.vue_generale, name="vue_generale"),
    path("mon-espace/", views.mon_espace, name="mon_espace"),
    
   # -------------------------------
    # Orange Money
    # -------------------------------
    path('payer_orange/', views.payer_orange_money, name='payer_orange'),

    # -------------------------------
    # VIP
    # -------------------------------
    path('acheter_vip/', views.acheter_vip, name='acheter_vip'),

    # -------------------------------
    # Consommation de data
    # -------------------------------
    path('ajouter_conso/', views.ajouter_conso, name='ajouter_conso'),

    # -------------------------------
    # Publicités sponsorisées
    # -------------------------------
    path('afficher_pubs/', views.afficher_pubs, name='afficher_pubs'),
    path('pubs_actives/', views.pubs_a_afficher, name='pubs_actives'),

    # -------------------------------
    # Interactions utilisateur
    # -------------------------------
    path('interaction/<str:action_type>/', views.enregistrer_interaction, name='enregistrer_interaction'),
    path('interaction/<str:action_type>/<int:cible_id>/', views.enregistrer_interaction, name='enregistrer_interaction_cible'),

    # -------------------------------
    # Action premium
    # -------------------------------
    path('action_premium/<str:action_type>/', views.action_premium, name='action_premium'),
    path('action_premium/<str:action_type>/<int:cible_id>/', views.action_premium, name='action_premium_cible'),

    # -------------------------------
    # Daily bonus
    # -------------------------------
    path('daily_bonus/', views.daily_bonus, name='daily_bonus'),
    path('vip/acheter/<int:duree>/', views.acheter_vip, name='acheter_vip'),
    path('vip/statut/', views.vip_statut, name='vip_statut'),
    
]
