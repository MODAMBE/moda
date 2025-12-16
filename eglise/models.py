from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth import get_user_model
import random

# -----------------------------------------------------
# CUSTOM USER MODEL
# -----------------------------------------------------
class CustomUser(AbstractUser):

    phone = models.CharField(max_length=20, unique=True)

    phone = models.CharField(max_length=20, unique=True, null=True)
    is_verified = models.BooleanField(default=False)
    verification_code = models.CharField(max_length=6, blank=True, null=True)

    avatar = models.ImageField(upload_to="user_avatars/", blank=True, null=True)
    bio = models.TextField(blank=True)

    groups = models.ManyToManyField(
        Group,
        related_name="customuser_set",
        blank=True,
        help_text="The groups this user belongs to.",
        verbose_name="groups",
    )

    user_permissions = models.ManyToManyField(
        Permission,
        related_name="customuser_permissions_set",
        blank=True,
        help_text="Specific permissions for this user.",
        verbose_name="user permissions",
    )

    def generate_verification_code(self):
        self.verification_code = f"{random.randint(100000, 999999)}"
        self.save()
        return self.verification_code

    def __str__(self):
        return self.username

User = get_user_model()

# -----------------------------------------------------
# PROFIL UTILISATEUR
# -----------------------------------------------------
class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    nom = models.CharField(max_length=50, blank=True, null=True)
    postnom = models.CharField(max_length=50, blank=True, null=True)
    prenom = models.CharField(max_length=50, blank=True, null=True)
    sexe = models.CharField(
        max_length=1,
        choices=[("M", "Masculin"), ("F", "Féminin")],
        blank=True,
        null=True,
    )
    date_naissance = models.DateField(blank=True, null=True)
    ville = models.CharField(max_length=100, blank=True, null=True)
    continent = models.CharField(max_length=50, blank=True, null=True)
    pays = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email_secondaire = models.EmailField(blank=True, null=True)
    pseudo_publique = models.CharField(max_length=50, blank=True, null=True)

    image = models.ImageField(upload_to="profiles/", null=True, blank=True)

    theme = models.CharField(
        max_length=20,
        choices=[("clair", "Clair"), ("sombre", "Sombre")],
        default="clair",
    )
    notif_messages = models.BooleanField(default=True)
    notif_activites = models.BooleanField(default=True)
    notif_emails = models.BooleanField(default=True)
    notif_push = models.BooleanField(default=True)

    langue = models.CharField(
        max_length=5,
        choices=[("fr", "Français"), ("en", "English"), ("es", "Español")],
        default="fr",
    )
    flux = models.CharField(
        max_length=20,
        choices=[("recent", "Publications récentes"), ("populaire", "Publications populaires")],
        default="recent",
    )

    bio = models.TextField(blank=True, default="")
    linked_accounts = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True, related_name="linked_profiles"
    )

    public_profile = models.BooleanField(default=True)
    newsletter = models.BooleanField(default=True)
    accept_cookies = models.BooleanField(default=True)

    language_preference = models.CharField(
        max_length=20,
        choices=[("fr", "Français"), ("en", "English"), ("es", "Español")],
        default="fr",
    )

    verification_code = models.CharField(max_length=6, blank=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username
# -----------------------------------------------------
# PUBLICATION PRINCIPALE
# -----------------------------------------------------
class Publication(models.Model):
    TYPE_CHOICES = [
        ("texte", "Texte"),
        ("image", "Image"),
        ("video", "Vidéo"),
        ("document", "Document"),
        ("vente", "Vente"),
        ("programme", "Programme"),
        ("application", "Application"),
    ]

    VISIBILITE_CHOICES = [
        ("public", "Public"),
        ("prive", "Privé"),
        ("amis", "Amis"),
    ]

    auteur = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="publications"
    )
    titre = models.CharField(max_length=255, blank=True, null=True)
    contenu = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to="publications/images/", blank=True, null=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default="texte")
    visibilite = models.CharField(
        max_length=10, choices=VISIBILITE_CHOICES, default="public"
    )
    prix = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    booster = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="likes", blank=True)

    def __str__(self):
        return self.titre or f"Publication {self.id} par {self.auteur.username}"


from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


# CHANNEL (optionnel, lié 1-1 à User)
class Channel(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="channel")
    name = models.CharField(max_length=255)
    username = models.SlugField(unique=True)
    bio = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    banner = models.ImageField(upload_to="banners/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Chaine(models.Model):
    auteur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="chaines")
    nom = models.CharField(max_length=255)
    username = models.SlugField(unique=True)
    bio = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    banner = models.ImageField(upload_to="banners/", blank=True, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nom


# VIDEO
class Video(models.Model):
    # On supporte les deux relations (Channel et Chaine), Channel est optionnel
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name="videos", null=True, blank=True)
    chaine = models.ForeignKey(Chaine, on_delete=models.CASCADE, related_name="videos", null=True, blank=True)

    titre = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    video_file = models.FileField(upload_to="videos/")
    thumbnail = models.ImageField(upload_to="thumbnails/", blank=True, null=True)

    hls_playlist = models.CharField(max_length=1024, blank=True)
    views = models.PositiveIntegerField(default=0)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="video_likes", blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    published = models.BooleanField(default=True)

    def __str__(self):
        return self.titre

    @property
    def is_expired(self):
        """Retourne True si la vidéo a plus de 3 jours."""
        return self.created_at < timezone.now() - timedelta(days=3)


# ABONNEMENT
class Abonnement(models.Model):
    utilisateur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="abonnements")
    chaine = models.ForeignKey(Chaine, on_delete=models.CASCADE, related_name="abonnements")
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ("utilisateur", "chaine")

    def __str__(self):
        return f"{self.utilisateur} -> {self.chaine}"




# -----------------------------------------------------
# ABONNEMENTS
# -----------------------------------------------------
class Abonnement(models.Model):
    utilisateur = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="abonnements"
    )
    chaine = models.ForeignKey(
        Chaine,
        on_delete=models.CASCADE,
        related_name="abonnements"
    )

    date_abonnement = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ("utilisateur", "chaine")

    def __str__(self):
        return f"{self.utilisateur.username} → {self.chaine.nom}"


# -----------------------------------------------------
# SUIVI ENTRE UTILISATEURS
# -----------------------------------------------------
class Suivi(models.Model):
    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="suivis",
    )
    suivi = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="followers",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("follower", "suivi")

    def __str__(self):
        return f"{self.follower.username} suit {self.suivi.username}"


# -----------------------------------------------------
# NOTIFICATIONS
# -----------------------------------------------------
class Notification(models.Model):
    TYPE_CHOICES = [
        ("message", "Message"),
        ("activite", "Activité"),
        ("email", "Email"),
        ("push", "Push"),
    ]

    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications"
    )
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)

    # FIXED!
    message = models.TextField()

    date = models.DateTimeField(auto_now_add=True)
    lu = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.utilisateur.username} - {self.type} - {self.message[:30]}"




class Media(models.Model):
    publication = models.ForeignKey(
        Publication, on_delete=models.CASCADE, related_name="medias"
    )
    fichier = models.FileField(upload_to="uploads/%Y/%m/%d/")
    type = models.CharField(
        max_length=20,
        choices=[("image", "Image"), ("video", "Vidéo"), ("document", "Document")],
        default="image",
    )
    miniature = models.ImageField(upload_to="uploads/thumbnails/", blank=True, null=True)

    def __str__(self):
        return f"Média {self.type} de la publication {self.publication.id}"


class Commentaire(models.Model):
    publication = models.ForeignKey(
        Publication, on_delete=models.CASCADE, related_name="commentaires"
    )
    auteur = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="commentaires"
    )

    # FIXED!
    contenu = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.auteur.username} sur {self.publication}"


# -----------------------------------------------------
# PROMOTIONS
# -----------------------------------------------------
class Promotion(models.Model):
    publication = models.OneToOneField(
        Publication, on_delete=models.CASCADE, related_name="promotion"
    )
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    duree = models.PositiveIntegerField(help_text="Durée en jours")
    actif = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Promotion de la publication {self.publication.id}"


# -----------------------------------------------------
# AMITIÉS
# -----------------------------------------------------
class Amitie(models.Model):
    demandeur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="demandes_envoyees",
        on_delete=models.CASCADE,
    )
    receveur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="demandes_recues",
        on_delete=models.CASCADE,
    )
    statut = models.CharField(
        max_length=10,
        choices=[
            ("en_attente", "En attente"),
            ("accepte", "Accepté"),
            ("refuse", "Refusé"),
        ],
        default="en_attente",
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    date_reponse = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.demandeur.username} → {self.receveur.username} ({self.statut})"

    @property
    def emetteur(self):
        return self.demandeur

    def accepter(self):
        from .models import Discussion
        self.statut = "accepte"
        self.date_reponse = timezone.now()
        self.save()

        Discussion.objects.get_or_create(
            utilisateur=self.demandeur, correspondant=self.receveur
        )
        Discussion.objects.get_or_create(
            utilisateur=self.receveur, correspondant=self.demandeur
        )

    def refuser(self):
        self.statut = "refuse"
        self.date_reponse = timezone.now()
        self.save()

    def heures_depuis_reponse(self):
        if self.date_reponse:
            return int((timezone.now() - self.date_reponse).total_seconds() // 3600)
        return None


# -----------------------------------------------------
# DISCUSSIONS & MESSAGES
# -----------------------------------------------------
class Discussion(models.Model):
    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="mes_discussions",
    )
    correspondant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="discussions_avec",
    )
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("utilisateur", "correspondant")

    def __str__(self):
        return f"{self.utilisateur.username} ↔ {self.correspondant.username}"


class Message(models.Model):
    discussion = models.ForeignKey(
        Discussion, on_delete=models.CASCADE, related_name="messages"
    )
    expediteur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    # FIXED!
    contenu = models.TextField(blank=True, null=True)

    fichier = models.FileField(upload_to="messages/", blank=True, null=True)
    type = models.CharField(
        max_length=20,
        choices=[
            ("texte", "Texte"),
            ("image", "Image"),
            ("video", "Vidéo"),
            ("audio", "Audio"),
            ("fichier", "Fichier"),
        ],
        default="texte",
    )
    date_envoye = models.DateTimeField(auto_now_add=True)
    lu = models.BooleanField(default=False)
    envoyer_local = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.expediteur.username} → {self.contenu or (self.fichier.name if self.fichier else 'Audio')}"


# -----------------------------------------------------
# APPELS
# -----------------------------------------------------
class Appel(models.Model):
    TYPE_CHOICES = (("audio", "Appel audio"), ("video", "Appel vidéo"))
    STATUT_CHOICES = (
        ("en_attente", "En attente"),
        ("accepte", "Accepté"),
        ("refuse", "Refusé"),
        ("manque", "Manqué"),
        ("termine", "Terminé"),
    )

    emetteur = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="appels_emis", on_delete=models.CASCADE
    )
    recepteur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="appels_recus",
        on_delete=models.CASCADE,
    )

    type_appel = models.CharField(max_length=10, choices=TYPE_CHOICES, default="audio")
    statut = models.CharField(
        max_length=20, choices=STATUT_CHOICES, default="en_attente"
    )

    date_creation = models.DateTimeField(default=timezone.now)
    date_fin = models.DateTimeField(null=True, blank=True)
    duree = models.DurationField(null=True, blank=True)

    def terminer(self, statut_final):
        self.statut = statut_final
        self.date_fin = timezone.now()
        if self.date_creation:
            self.duree = self.date_fin - self.date_creation
        self.save()

    def __str__(self):
        return f"{self.emetteur.username} → {self.recepteur.username} ({self.type_appel}) - {self.statut}"

# -----------------------------------------------------
# TABLE INTERMÉDIAIRE POUR LES LIKES
# -----------------------------------------------------
class PublicationLike(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    # Like sur une publication TEXTUELLE
    publicationtexte = models.ForeignKey(
        "PublicationTexte",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="likes_relations_texte"
    )

    # Like sur une publication PAR CHAÎNE
    publicationchaine = models.ForeignKey(
        "PublicationChaine",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="likes_relations_chaine"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "eglise"
        db_table = "eglise_publication_like"

        # CORRECTION 🔥 : unique_together corrigé avec les VRAIS champs
        unique_together = (
            ("user", "publicationtexte"),
            ("user", "publicationchaine"),
        )

    def clean(self):
        """
        Empêche d'avoir :
        - 0 publication (aucune cible)
        - 2 publications (texte + chaîne en même temps)
        """
        from django.core.exceptions import ValidationError

        if not self.publicationtexte and not self.publicationchaine:
            raise ValidationError("Un like doit cibler une publication texte OU chaîne.")

        if self.publicationtexte and self.publicationchaine:
            raise ValidationError("Un like ne peut pas cibler deux publications à la fois.")

    def __str__(self):
        if self.publicationtexte:
            return f"{self.user.username} aime PublicationTexte {self.publicationtexte.id}"
        if self.publicationchaine:
            return f"{self.user.username} aime PublicationChaine {self.publicationchaine.id}"
        return f"Like orphelin par {self.user.username}"

# PublicationTexte (publications spécifiques aux chaines)
class PublicationTexte(models.Model):
    chaine = models.ForeignKey(Chaine, on_delete=models.CASCADE, related_name="textes")
    auteur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="publication_textes")
    contenu = models.TextField(blank=True, null=True)
    bg_color = models.CharField(max_length=20, blank=True, null=True)
    text_color = models.CharField(max_length=20, blank=True, null=True)
    stickers = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="texte_likes", blank=True)

    def __str__(self):
        return f"Texte #{self.id} - {self.chaine.nom}"
    
from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import uuid
import requests

# ---------------------------------------------------------
# CONSOMMATION DE DONNÉES PAYANTE (DATA)
# ---------------------------------------------------------
class DataUsage(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    mo_utilises = models.FloatField(default=0)
    mo_payes = models.FloatField(default=0)  # montant payé pour les Mo

    def __str__(self):
        return f"{self.user.username} - {self.mo_utilises} Mo utilisées, {self.mo_payes} Fc payés"

    def add_usage(self, mo, montant_fc):
        """Ajouter de la consommation payante"""
        self.mo_utilises += mo
        self.mo_payes += montant_fc
        self.save()


# ---------------------------------------------------------
# MODCOINS (Monnaie virtuelle)
# ---------------------------------------------------------
class ModCoins(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    solde = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.user.username} - {self.solde} Coins"

    def ajouter(self, montant):
        self.solde += montant
        self.save()

    def retirer(self, montant):
        if self.solde >= montant:
            self.solde -= montant
            self.save()
            return True
        return False


# ---------------------------------------------------------
# ABONNEMENT VIP
# ---------------------------------------------------------
class VIPSubscription(models.Model):
    DURATION_CHOICES = [
        (7, "7 jours"),
        (30, "30 jours"),
        (90, "90 jours"),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='vip_subscription')
    duration_days = models.IntegerField(choices=DURATION_CHOICES, default=7)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=False)

    def activate(self):
        """Active ou renouvelle l'abonnement VIP."""
        self.start_date = timezone.now()
        self.end_date = self.start_date + timedelta(days=self.duration_days)
        self.is_active = True
        self.save()

    def check_expiration(self):
        """Désactive automatiquement si expiré."""
        if self.end_date and timezone.now() > self.end_date:
            self.is_active = False
            self.save()

    def __str__(self):
        return f"VIP de {self.user.username} — actif: {self.is_active}"


# ---------------------------------------------------------
# INTERACTIONS UTILISATEUR
# ---------------------------------------------------------
class Interaction(models.Model):
    TYPE_CHOICES = [
        ("like","Like"),
        ("commentaire","Commentaire"),
        ("telechargement","Téléchargement"),
        ("video_view","Visionnage vidéo"),
        ("daily_bonus","Bonus journalier"),
        ("achat_pub","Achat publicité"),
        ("partage","Partage"),
        ("rewarded_ad","Rewarded Ad"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    cible_id = models.IntegerField(null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    montant_gain = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.user.username} - {self.type} - Gain: {self.montant_gain} Fc"

    def ajouter_gain(self, montant_fc):
        """Ajoute le montant gagné pour cette action"""
        self.montant_gain += montant_fc
        self.save()
        # Crée automatiquement un PaiementOrangeMoney fictif si nécessaire
        PaiementOrangeMoney.objects.create(
            user=self.user,
            montant=montant_fc,
            numero="",  # Numéro OM du user si paiement réel
            reference=str(uuid.uuid4()),
            statut="success"
        )


# ---------------------------------------------------------
# PUBLICITÉS RÉCOMPENSÉES
# ---------------------------------------------------------
class RewardedAd(models.Model):
    titre = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    coins_bonus = models.IntegerField(default=1)
    actif = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.titre} - {self.coins_bonus} Coins"

    def attribuer_bonus(self, user):
        modcoins, created = ModCoins.objects.get_or_create(user=user)
        modcoins.ajouter(self.coins_bonus)
        Interaction.objects.create(user=user, type="rewarded_ad", montant_gain=self.coins_bonus)


# ---------------------------------------------------------
# PUBLICATIONS & PUBLICITÉS
# ---------------------------------------------------------
class PublicationChaine(models.Model):
    chaine = models.ForeignKey("Chaine", on_delete=models.CASCADE, related_name="publications")
    auteur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="publications_chaine")
    titre = models.CharField(max_length=255, blank=True, null=True)
    contenu = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to="publications_chaines/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="publication_chaine_likes", blank=True)

    def __str__(self):
        return self.titre or f"PublicationChaine #{self.id}"


class PubliciteSponsorisee(models.Model):
    annonceur = models.CharField(max_length=255)
    image = models.ImageField(upload_to="ads/")
    lien = models.URLField(blank=True, null=True)
    actif = models.BooleanField(default=True)
    date_debut = models.DateTimeField()
    date_fin = models.DateTimeField()

    def __str__(self):
        return f"Pub {self.annonceur}"


# ---------------------------------------------------------
# PAIEMENT ORANGE MONEY
# ---------------------------------------------------------
class PaiementOrangeMoney(models.Model):
    STATUT_CHOICES = [
        ("en_attente", "En attente"),
        ("success", "Succès"),
        ("failed", "Échoué"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    numero = models.CharField(max_length=50)
    reference = models.CharField(max_length=100, unique=True, default=uuid.uuid4)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default="en_attente")
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"OM {self.user.username} - {self.montant} Fc - {self.statut}"

    def valider(self):
        self.statut = "success"
        self.save()

    def echouer(self):
        self.statut = "failed"
        self.save()

    def demarrer_transaction(self):
        """Démarre la transaction via l'API Orange Money"""
        url = "https://api.orange.com/orange-money-webpay/dev/v1/webpayment"
        headers = {
            "Authorization": f"Bearer {settings.OM_API_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "merchant_key": settings.OM_MERCHANT_KEY,
            "currency": "CDF",
            "order_id": self.reference,
            "amount": str(self.montant),
            "return_url": settings.OM_RETURN_URL,
            "cancel_url": settings.OM_CANCEL_URL,
            "notif_url": settings.OM_CALLBACK_URL,
            "lang": "fr",
        }
        response = requests.post(url, json=payload, headers=headers)
        return response.json()


# eglise/models.py

from django.db import models


class Membre(models.Model):
    SEXE_CHOICES = [
        ('M', 'Masculin'),
        ('F', 'Féminin'),
    ]

    STATUT_CHOICES = [
        ('membre', 'Membre'),
        ('nouveau', 'Nouveau Converti'),
        ('visiteur', 'Visiteur'),
        ('ancien', 'Ancien'),
        ('diacre', 'Diacre'),
        ('past', 'Pastoral'),
    ]

    nom = models.CharField(max_length=100)
    postnom = models.CharField(max_length=100, blank=True)
    prenom = models.CharField(max_length=100, blank=True)
    sexe = models.CharField(max_length=1, choices=SEXE_CHOICES)
    date_naissance = models.DateField(null=True, blank=True)
    telephone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)

    adresse = models.CharField(max_length=255, blank=True)
    statut = models.CharField(
        max_length=20, 
        choices=STATUT_CHOICES, 
        default='membre'
    )

    date_inscription = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    # Pour enregistrer photo ou dossier du membre
    photo = models.ImageField(upload_to='membres/photos/', blank=True, null=True)

    def __str__(self):
        return f"{self.nom} {self.postnom} {self.prenom}".strip()

