import os
import firebase_admin
from firebase_admin import credentials, messaging
from django.conf import settings

# Chemin vers le fichier JSON de clés Firebase
CREDENTIAL_PATH = os.path.join(settings.BASE_DIR, 'firebase_credentials.json')

# Initialisation unique du SDK Firebase
if not firebase_admin._apps:
    if os.path.exists(CREDENTIAL_PATH):
        cred = credentials.Certificate(CREDENTIAL_PATH)
        firebase_admin.initialize_app(cred)
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