from django.contrib import admin

# Essayez d'importer les modèles
try:
    from .models import (
        DataUsage,
        ModCoins,
        VIPSubscription,
        PubliciteSponsorisee,
        PaiementOrangeMoney,
        Interaction,
        RewardedAd,
        Channel,
        Chaine,
        Video,
        Publication,
        PublicationTexte,
        PublicationChaine,
        Abonnement,
        Suivi,
        Notification,
        Commentaire,
        Media,
        Promotion,
        Amitie,
        Discussion,
        Message,
        Appel,
    )
except ImportError as e:
    print("Erreur d'import des modèles :", e)

# ---------------------------------------------------------
# DATA USAGE
# ---------------------------------------------------------
@admin.register(DataUsage)
class DataUsageAdmin(admin.ModelAdmin):
    list_display = ('user', 'mo_utilises', 'mo_payes')
    search_fields = ('user__username',)
    list_filter = ('user',)
    ordering = ('-mo_utilises',)

# ---------------------------------------------------------
# MODCOINS
# ---------------------------------------------------------
@admin.register(ModCoins)
class ModCoinsAdmin(admin.ModelAdmin):
    list_display = ('user', 'solde')
    search_fields = ('user__username',)
    ordering = ('-solde',)

# ---------------------------------------------------------
# VIP SUBSCRIPTION
# ---------------------------------------------------------
@admin.register(VIPSubscription)
class VIPSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'duration_days', 'start_date', 'end_date', 'is_active')
    list_filter = ('is_active', 'duration_days')
    search_fields = ('user__username', 'user__email')
    ordering = ('-start_date',)

# ---------------------------------------------------------
# PUBLICITÉS SPONSORISÉES
# ---------------------------------------------------------
@admin.register(PubliciteSponsorisee)
class PubliciteSponsoriseeAdmin(admin.ModelAdmin):
    list_display = ('annonceur', 'actif', 'date_debut', 'date_fin')
    search_fields = ('annonceur',)
    list_filter = ('actif', 'date_debut', 'date_fin')
    ordering = ('-date_debut',)

# ---------------------------------------------------------
# PAIEMENTS ORANGE MONEY
# ---------------------------------------------------------
@admin.register(PaiementOrangeMoney)
class PaiementOrangeMoneyAdmin(admin.ModelAdmin):
    list_display = ('user', 'montant', 'numero', 'reference', 'statut', 'date')
    search_fields = ('user__username', 'numero', 'reference')
    list_filter = ('statut', 'date')
    ordering = ('-date',)

# ---------------------------------------------------------
# INTERACTIONS
# ---------------------------------------------------------
@admin.register(Interaction)
class InteractionAdmin(admin.ModelAdmin):
    list_display = ('user', 'type', 'cible_id', 'date')
    search_fields = ('user__username', 'type')
    list_filter = ('type', 'date')
    ordering = ('-date',)

# ---------------------------------------------------------
# REWARDED ADS
# ---------------------------------------------------------
@admin.register(RewardedAd)
class RewardedAdAdmin(admin.ModelAdmin):
    list_display = ('titre', 'coins_bonus', 'actif')
    search_fields = ('titre',)
    list_filter = ('actif',)
    ordering = ('-coins_bonus',)

# ---------------------------------------------------------
# ABONNEMENTS
# ---------------------------------------------------------
if Abonnement not in admin.site._registry:
    @admin.register(Abonnement)
    class AbonnementAdmin(admin.ModelAdmin):
        list_display = ('utilisateur', 'chaine', 'date_abonnement')
        list_filter = ('chaine',)
        search_fields = ('utilisateur__username', 'chaine__nom')
        ordering = ('-date_abonnement',)
