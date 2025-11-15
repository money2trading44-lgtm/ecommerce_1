from supabase import create_client
from django.conf import settings
import uuid


def upload_to_supabase(file, folder='products'):
    """Upload un fichier vers Supabase et retourne l'URL publique"""
    try:
        supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

        # Génération d'un nom unique
        file_extension = file.name.split('.')[-1]
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = f"{folder}/{unique_filename}"

        # Lecture et upload
        file_content = file.read()
        supabase.storage.from_("dsd-trading-images").upload(
            file_path,
            file_content,
            {"content-type": file.content_type}
        )

        # URL publique
        return f"{settings.SUPABASE_URL}/storage/v1/object/public/dsd-trading-images/{file_path}"

    except Exception as e:
        print(f"❌ Erreur upload Supabase: {e}")
        return None


def delete_from_supabase(image_url):
    """Supprime un fichier de Supabase Storage à partir de son URL publique"""
    try:
        supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

        bucket_name = "dsd-trading-images"
        # Extraire le chemin relatif (ex: products/uuid.png)
        path = image_url.split(f"/{bucket_name}/")[-1]

        supabase.storage.from_(bucket_name).remove([path])
        print(f"✅ Fichier supprimé de Supabase: {path}")
        return True

    except Exception as e:
        print(f"❌ Erreur suppression Supabase: {e}")
        return False
