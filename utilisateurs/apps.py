import os
from django.apps import AppConfig
from django.conf import settings


class UtilisateursConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'utilisateurs'

    def ready(self):
        import firebase_admin
        from firebase_admin import credentials

        cred_path = os.path.join(settings.BASE_DIR, 'firebase_credentials.json')

        if not firebase_admin._apps:
            if os.path.exists(cred_path):
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
            else:
                print("⚠️ Firebase non initialisé en local (fichier credentials manquant).")