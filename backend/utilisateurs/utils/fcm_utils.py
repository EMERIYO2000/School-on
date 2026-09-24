import os
import firebase_admin
from firebase_admin import credentials, messaging
from django.conf import settings

def get_firebase_credential_path():
    configured_path = os.getenv('FIREBASE_CREDENTIALS_PATH')
    if configured_path:
        cred_path = configured_path
        if not os.path.isabs(cred_path):
            cred_path = os.path.join(settings.BASE_DIR, cred_path)
        return cred_path
    return os.path.join(settings.BASE_DIR, 'firebase_credentials.json')


CREDENTIAL_PATH = get_firebase_credential_path()

# Initialisation unique du SDK Firebase
if not firebase_admin._apps:
    if os.path.exists(CREDENTIAL_PATH):
        try:
            cred = credentials.Certificate(CREDENTIAL_PATH)
            firebase_admin.initialize_app(cred)
        except Exception as exc:
            print(f"⚠️ Firebase credentials invalides : {exc}")
    else:
        print("⚠️ Attention: Fichier firebase_credentials.json introuvable. Les notifications ne fonctionneront pas.")


def send_fcm_notification(fcm_token: str, title: str, body: str, data: dict = None):
    """
    Envoie une notification push via Firebase Cloud Messaging à un appareil.
    """
    if not fcm_token:
        return False

    try:
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            data=data or {},
            token=fcm_token,
        )
        response = messaging.send(message)
        print(f"✅ Notification envoyée avec succès : {response}")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de l'envoi de la notification Push : {e}")
        return False