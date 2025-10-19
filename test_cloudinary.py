import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_project.settings')
django.setup()

from shop.models import Product
import cloudinary.uploader

# Test 1: Vérifier les variables d'environnement
print("=== VARIABLES ENV ===")
print("CLOUD_NAME:", os.environ.get('CLOUDINARY_CLOUD_NAME'))
print("API_KEY:", os.environ.get('CLOUDINARY_API_KEY')[:10] + "..." if os.environ.get('CLOUDINARY_API_KEY') else 'None')
print("API_SECRET:", "Présent" if os.environ.get('CLOUDINARY_API_SECRET') else 'None')

# Test 2: Upload direct vers Cloudinary
print("\n=== TEST UPLOAD ===")
try:
    result = cloudinary.uploader.upload("https://res.cloudinary.com/demo/image/upload/sample.jpg")
    print("✅ Upload réussi:", result['url'])
except Exception as e:
    print("❌ Erreur upload:", e)

# Test 3: Vérifier le stockage Django
print("\n=== STOCKAGE DJANGO ===")
from django.core.files.storage import default_storage
print("Storage:", default_storage.__class__.__name__)