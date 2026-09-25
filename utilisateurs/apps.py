import os
from django.apps import AppConfig
from django.conf import settings


class UtilisateursConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'utilisateurs'

    def ready(self):
        import firebase_admin
        from firebase_admin import credentials

        configured_path = os.getenv('FIREBASE_CREDENTIALS_PATH')
        if configured_path:
            cred_path = configured_path
            if not os.path.isabs(cred_path):
                cred_path = os.path.join(settings.BASE_DIR, cred_path)
        else:
            cred_path = os.path.join(settings.BASE_DIR, 'firebase_credentials.json')

        if not firebase_admin._apps:
            if cred_path and os.path.exists(cred_path):
                try:
                    cred = credentials.Certificate(cred_path)
                    firebase_admin.initialize_app(cred)
                except Exception as exc:
                    print(f"⚠️ Firebase credentials invalides : {exc}")
            else:
                print("⚠️ Firebase non initialisé en local (fichier credentials manquant).")