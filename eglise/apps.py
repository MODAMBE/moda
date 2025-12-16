from django.apps import AppConfig


class EgliseConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'eglise'

    def ready(self):
        """
        Méthode appelée au chargement de l'application.
        Permet d'enregistrer les signaux Django.
        """
        try:
            import eglise.signals  # noqa: F401
        except Exception:
            # Optionnel : logger l'erreur si nécessaire
            pass
