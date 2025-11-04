from supabase import create_client
from django.conf import settings
import uuid


def upload_to_supabase(file, folder='products'):
    """Upload un fichier vers Supabase et retourne l'URL publique"""
    try:
        print(f"🔧 Début upload - Nom: {file.name}, Taille: {file.size}")

        supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

        # Génération d'un nom de fichier unique
        file_extension = file.name.split('.')[-1]
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = f"{folder}/{unique_filename}"

        print(f"🔧 Nom généré: {file_path}")

        # Lire le fichier
        file_content = file.read()
        print(f"🔧 Fichier lu - Taille: {len(file_content)} bytes")

        # Upload
        print("🔧 Tentative d'upload...")
        result = supabase.storage.from_("dsd-trading-images").upload(
            file_path,
            file_content,
            {"content-type": file.content_type}
        )

        print(f"🔧 Résultat upload: {result}")

        # Retourner l'URL publique
        url = f"{settings.SUPABASE_URL}/storage/v1/object/public/dsd-trading-images/{file_path}"
        print(f"🔧 URL générée: {url}")

        return url

    except Exception as e:
        print(f"❌ Erreur upload Supabase: {e}")
        return None