# shop/apps.py

import os
from django.apps import AppConfig

# Ajoutez ces imports
import cloudinary
from dotenv import load_dotenv

# Chargez l'environnement ici aussi, pour être sûr de lire les variables
load_dotenv()


class ShopConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'shop'

    def ready(self):
        """Initialise Cloudinary avec les variables d'environnement au démarrage."""

        # 🚨 C'EST ICI QUE NOUS FORÇONS LA CONFIGURATION
        cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME')
        api_key = os.environ.get('CLOUDINARY_API_KEY')
        api_secret = os.environ.get('CLOUDINARY_API_SECRET')

        if cloud_name and api_key and api_secret:
            cloudinary.config(
                cloud_name=cloud_name,
                api_key=api_key,
                api_secret=api_secret,
                secure=True
            )
        else:
            print("⚠️ AVERTISSEMENT: Variables Cloudinary CLOUD_NAME, API_KEY ou API_SECRET manquantes.")