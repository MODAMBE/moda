from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from .models import (
    Profile, Publication, Video, Chaine, Channel, PublicationTexte
)

User = get_user_model()

# ===========================
# Formulaire d'inscription
# ===========================
class InscriptionForm(forms.ModelForm):
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Nom d'utilisateur"})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Mot de passe"})
    )
    conf_password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Confirmer mot de passe"})
    )

    class Meta:
        model = Profile
        fields = [
            'nom', 'postnom', 'prenom', 'sexe', 'date_naissance', 'ville',
            'continent', 'pays', 'phone', 'image'
        ]
        widgets = {
            "nom": forms.TextInput(attrs={"class": "form-control"}),
            "postnom": forms.TextInput(attrs={"class": "form-control"}),
            "prenom": forms.TextInput(attrs={"class": "form-control"}),
            "sexe": forms.Select(attrs={"class": "form-select"}),
            "date_naissance": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "ville": forms.TextInput(attrs={"class": "form-control"}),
            "continent": forms.Select(attrs={"class": "form-select"}),
            "pays": forms.TextInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "image": forms.FileInput(attrs={"class": "form-control"}),
        }

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if User.objects.filter(username=username).exists():
            raise ValidationError("Ce nom d'utilisateur est déjà utilisé.")
        return username

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("password") != cleaned_data.get("conf_password"):
            raise ValidationError("Les mots de passe ne correspondent pas.")
        return cleaned_data

# ===========================
# ProfileForm
# ===========================
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'pseudo_publique', 'bio', 'image', 'theme', 'langue', 'flux',
            'notif_messages', 'notif_activites', 'notif_emails', 'notif_push',
            'public_profile', 'newsletter', 'accept_cookies'
        ]

# ===========================
# PublicationForm
# ===========================
class PublicationForm(forms.ModelForm):
    class Meta:
        model = Publication
        fields = ['contenu', 'type', 'visibilite', 'prix', 'booster']
        widgets = {
            'contenu': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Écrire une publication...'
            })
        }

# ===========================
# MediaForm
# ===========================
class MediaForm(forms.Form):
    fichiers = forms.FileField(required=False, widget=forms.FileInput())

# ===========================
# VideoForm
# ===========================
class VideoForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ["titre", "description", "video_file", "thumbnail"]
        widgets = {
            "titre": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "video_file": forms.FileInput(attrs={"class": "form-control"}),
            "thumbnail": forms.FileInput(attrs={"class": "form-control"}),
        }

    def clean_video_file(self):
        file = self.cleaned_data.get("video_file")
        if file:
            content_type = getattr(file, "content_type", "")
            if not content_type.startswith("video"):
                raise forms.ValidationError("Le fichier doit être une vidéo.")
        return file

# ===========================
# VideoUploadForm (réintroduit)
# ===========================
class VideoUploadForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ["chaine", "titre", "description", "video_file", "thumbnail"]
        widgets = {
            "titre": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "video_file": forms.FileInput(attrs={"class": "form-control"}),
            "thumbnail": forms.FileInput(attrs={"class": "form-control"}),
        }

# ===========================
# PublicationTexteForm
# ===========================
class PublicationTexteForm(forms.ModelForm):
    class Meta:
        model = PublicationTexte
        fields = ["contenu", "bg_color", "text_color", "stickers"]
        widgets = {
            "contenu": forms.Textarea(attrs={"rows": 4}),
            "stickers": forms.HiddenInput(),
        }

# ===========================
# ChaineForm
# ===========================
class ChaineForm(forms.ModelForm):
    class Meta:
        model = Chaine
        fields = ["nom", "username", "bio", "avatar", "banner"]
        widgets = {
            "nom": forms.TextInput(attrs={"class": "form-control"}),
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "bio": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
            "avatar": forms.FileInput(attrs={"class": "form-control"}),
            "banner": forms.FileInput(attrs={"class": "form-control"}),
        }

# ===========================
# ChannelForm (pour Channel)
# ===========================
class ChannelForm(forms.ModelForm):
    class Meta:
        model = Channel
        fields = ["name", "username", "bio", "avatar", "banner"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "bio": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
            "avatar": forms.FileInput(attrs={"class": "form-control"}),
            "banner": forms.FileInput(attrs={"class": "form-control"}),
        }
