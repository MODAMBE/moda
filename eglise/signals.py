# eglise/signals.py

from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .models import Membre


@receiver(post_save, sender=Membre)
def membre_saved(sender, instance, created, **kwargs):
    """Signal exécuté lorsqu'un Membre est créé ou modifié."""
    nom_complet = f"{instance.nom} {instance.postnom} {instance.prenom}".strip()

    if created:
        print(f"[SIGNAL] Nouveau membre ajouté : {nom_complet}")
    else:
        print(f"[SIGNAL] Membre modifié : {nom_complet}")


@receiver(pre_delete, sender=Membre)
def membre_deleted(sender, instance, **kwargs):
    """Signal exécuté lorsqu'un Membre est supprimé."""
    nom_complet = f"{instance.nom} {instance.postnom} {instance.prenom}".strip()
    print(f"[SIGNAL] Membre supprimé : {nom_complet}")
