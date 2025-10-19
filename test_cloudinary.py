import os
import cloudinary
import cloudinary.uploader

# Configuration directe
cloudinary.config(
    cloud_name = "debxh9hje",
    api_key = "956162166938992",
    api_secret = "Azwan_08SWwBwoSllqKvEIhSGrk",  # Remplacez par votre vrai secret
    secure=True
)

# Test d'upload
try:
    upload_result = cloudinary.uploader.upload(
        "https://res.cloudinary.com/demo/image/upload/sample.jpg",
        public_id="test_image"
    )
    print("✅ UPLOAD RÉUSSI!")
    print("URL:", upload_result["secure_url"])
except Exception as e:
    print("❌ ERREUR:", e)