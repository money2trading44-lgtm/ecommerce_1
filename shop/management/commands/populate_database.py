import os
import requests
from io import BytesIO
from django.core.files import File
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from shop.models import Category, Product
from django.conf import settings


class Command(BaseCommand):
    help = 'Peuple la base de données avec des produits de test'

    def handle(self, *args, **options):
        self.stdout.write('🧹 Nettoyage de la base de données...')
        # Nettoyer les données existantes (optionnel)
        Product.objects.all().delete()
        Category.objects.all().delete()

        self.stdout.write('📁 Création des catégories...')
        # Créer les catégories
        sheets_category, created = Category.objects.get_or_create(
            name="Draps et Literie",
            defaults={'description': 'Draps de qualité supérieure pour un sommeil confortable'}
        )

        phones_category, created = Category.objects.get_or_create(
            name="Téléphones",
            defaults={'description': 'Smartphones et accessoires high-tech'}
        )

        self.stdout.write('🛏️ Ajout des draps...')
        # Données pour les draps
        sheets_data = [
            {
                'name': 'Draps en Coton Égyptien Premium',
                'description': 'Draps 100% coton égyptien de la plus haute qualité. Doux, respirant et durable pour des nuits de sommeil parfaites.',
                'price': 89.99,
                'stock': 50,
                'sheet_size': 'QUEEN',
                'color': 'WHITE',
                'material': 'Coton Égyptien 100%',
                'image_url': 'https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=500'
            },
            {
                'name': 'Draps en Bambou Écologique',
                'description': 'Draps en bambou hypoallergéniques, respectueux de l\'environnement. Idéal pour les peaux sensibles.',
                'price': 74.99,
                'stock': 35,
                'sheet_size': 'KING',
                'color': 'GRAY',
                'material': 'Bambou 95%, Élasthanne 5%',
                'image_url': 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=500'
            },
            {
                'name': 'Draps en Lin Naturel',
                'description': 'Draps en lin naturel, parfaits pour les nuits d\'été. Absorbants et thermorégulateurs.',
                'price': 99.99,
                'stock': 25,
                'sheet_size': 'DOUBLE',
                'color': 'BEIGE',
                'material': 'Lin 100%',
                'image_url': 'https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=500'
            },
            {
                'name': 'Draps en Satin de Luxe',
                'description': 'Draps en satin brillant pour une expérience de sommeil luxueuse. Doux et soyeux.',
                'price': 119.99,
                'stock': 20,
                'sheet_size': 'QUEEN',
                'color': 'PINK',
                'material': 'Satin de soie',
                'image_url': 'https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=500'
            },
            {
                'name': 'Draps en Coton Bio Simple',
                'description': 'Draps en coton biologique certifié, taille simple. Confortables et écologiques.',
                'price': 49.99,
                'stock': 60,
                'sheet_size': 'SIMPLE',
                'color': 'BLUE',
                'material': 'Coton Bio 100%',
                'image_url': 'https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=500'
            },
            {
                'name': 'Draps Hôtelier en Percale',
                'description': 'Draps qualité hôtelière en percale de coton. Frais et croustillants au toucher.',
                'price': 69.99,
                'stock': 40,
                'sheet_size': 'DOUBLE',
                'color': 'WHITE',
                'material': 'Percale de coton 200 fils',
                'image_url': 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=500'
            }
        ]

        self.stdout.write('📱 Ajout des téléphones...')
        # Données pour les téléphones
        phones_data = [
            {
                'name': 'iPhone 15 Pro Max',
                'description': 'Dernier iPhone avec écran Dynamic Island, caméra 48MP et puce A17 Pro. Performance ultime.',
                'price': 1299.99,
                'stock': 15,
                'phone_brand': 'APPLE',
                'phone_category': 'BESTSELLER',
                'storage': '256GB',
                'screen_size': '6.7 pouces',
                'processor': 'A17 Pro',
                'ram': '8GB',
                'camera': 'Triple 48MP + 12MP + 12MP',
                'battery': '4422 mAh',
                'operating_system': 'iOS 17',
                'connectivity': '5G, Wi-Fi 6E, Bluetooth 5.3',
                'image_url': 'https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=500'
            },
            {
                'name': 'Samsung Galaxy S24 Ultra',
                'description': 'Smartphone Android flagship avec S-Pen, écran Dynamic AMOLED et caméra 200MP.',
                'price': 1199.99,
                'stock': 12,
                'phone_brand': 'GALAXY',
                'phone_category': 'BESTSELLER',
                'storage': '512GB',
                'screen_size': '6.8 pouces',
                'processor': 'Snapdragon 8 Gen 3',
                'ram': '12GB',
                'camera': 'Quad 200MP + 50MP + 12MP + 10MP',
                'battery': '5000 mAh',
                'operating_system': 'Android 14',
                'connectivity': '5G, Wi-Fi 7, Bluetooth 5.3',
                'image_url': 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=500'
            },
            {
                'name': 'Google Pixel 8 Pro',
                'description': 'Téléphone Google avec AI avancée, excellent appareil photo et Android pur.',
                'price': 999.99,
                'stock': 18,
                'phone_brand': 'PIXEL',
                'phone_category': 'OFFER',
                'storage': '128GB',
                'screen_size': '6.7 pouces',
                'processor': 'Google Tensor G3',
                'ram': '12GB',
                'camera': 'Triple 50MP + 48MP + 48MP',
                'battery': '5050 mAh',
                'operating_system': 'Android 14',
                'connectivity': '5G, Wi-Fi 7, Bluetooth 5.3',
                'on_sale': True,
                'discount_percentage': 10,
                'image_url': 'https://images.unsplash.com/photo-1592899677977-9c10ca588bbd?w=500'
            },
            {
                'name': 'OnePlus 12',
                'description': 'Performance pure avec charge rapide 100W, écran Fluid AMOLED et design premium.',
                'price': 899.99,
                'stock': 22,
                'phone_brand': 'ONEPLUS',
                'phone_category': 'OFFER',
                'storage': '256GB',
                'screen_size': '6.82 pouces',
                'processor': 'Snapdragon 8 Gen 3',
                'ram': '16GB',
                'camera': 'Triple 50MP + 48MP + 64MP',
                'battery': '5400 mAh',
                'operating_system': 'OxygenOS 14',
                'connectivity': '5G, Wi-Fi 7, Bluetooth 5.4',
                'on_sale': True,
                'discount_percentage': 15,
                'image_url': 'https://images.unsplash.com/photo-1556656793-08538906a9f8?w=500'
            },
            {
                'name': 'Xiaomi 14 Pro',
                'description': 'Smartphone innovant avec écran courbe, charge ultra-rapide et caméra Leica.',
                'price': 799.99,
                'stock': 25,
                'phone_brand': 'XIAOMI',
                'phone_category': 'REFURBISHED',
                'storage': '512GB',
                'screen_size': '6.73 pouces',
                'processor': 'Snapdragon 8 Gen 3',
                'ram': '12GB',
                'camera': 'Triple 50MP Leica + 50MP + 50MP',
                'battery': '4880 mAh',
                'operating_system': 'HyperOS',
                'connectivity': '5G, Wi-Fi 7, Bluetooth 5.4',
                'image_url': 'https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=500'
            },
            {
                'name': 'TechGiant Nova X',
                'description': 'Notre marque maison avec excellente performance/prix, parfait pour usage quotidien.',
                'price': 499.99,
                'stock': 30,
                'phone_brand': 'TECHGIANT',
                'phone_category': 'OFFER',
                'storage': '128GB',
                'screen_size': '6.5 pouces',
                'processor': 'MediaTek Dimensity 9000',
                'ram': '8GB',
                'camera': 'Double 64MP + 8MP',
                'battery': '5000 mAh',
                'operating_system': 'Android 13',
                'connectivity': '5G, Wi-Fi 6, Bluetooth 5.2',
                'on_sale': True,
                'discount_percentage': 20,
                'image_url': 'https://images.unsplash.com/photo-1565849904461-04a58ad377e0?w=500'
            },
            {
                'name': 'iPhone 14 Reconditionné',
                'description': 'iPhone 14 reconditionné comme neuf, garanti 12 mois. Excellente affaire !',
                'price': 699.99,
                'stock': 8,
                'phone_brand': 'APPLE',
                'phone_category': 'REFURBISHED',
                'storage': '128GB',
                'screen_size': '6.1 pouces',
                'processor': 'A15 Bionic',
                'ram': '6GB',
                'camera': 'Double 12MP + 12MP',
                'battery': '3279 mAh',
                'operating_system': 'iOS 16',
                'connectivity': '5G, Wi-Fi 6, Bluetooth 5.3',
                'image_url': 'https://images.unsplash.com/photo-1592899677977-9c10ca588bbd?w=500'
            }
        ]

        self.stdout.write('📥 Téléchargement des images et création des produits...')

        # Fonction pour télécharger et sauvegarder l'image
        def download_image(url, product_name):
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    image_name = f"{product_name.replace(' ', '_').lower()}.jpg"
                    image_file = BytesIO(response.content)
                    return File(image_file, name=image_name)
                else:
                    self.stdout.write(self.style.WARNING(f"⚠️ Impossible de télécharger l'image pour {product_name}"))
                    return None
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"⚠️ Erreur image {product_name}: {str(e)}"))
                return None

        # Créer les draps
        for sheet_data in sheets_data:
            try:
                image_file = download_image(sheet_data['image_url'], sheet_data['name'])

                product = Product(
                    name=sheet_data['name'],
                    description=sheet_data['description'],
                    price=sheet_data['price'],
                    category=sheets_category,
                    product_type='SHEET',
                    stock=sheet_data['stock'],
                    sheet_size=sheet_data['sheet_size'],
                    color=sheet_data['color'],
                    material=sheet_data['material'],
                    is_active=True
                )

                if image_file:
                    product.image.save(image_file.name, image_file, save=False)

                product.save()
                self.stdout.write(self.style.SUCCESS(f"✅ Draps créés: {sheet_data['name']}"))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Erreur avec {sheet_data['name']}: {str(e)}"))

        # Créer les téléphones
        for phone_data in phones_data:
            try:
                image_file = download_image(phone_data['image_url'], phone_data['name'])

                product = Product(
                    name=phone_data['name'],
                    description=phone_data['description'],
                    price=phone_data['price'],
                    category=phones_category,
                    product_type='PHONE',
                    stock=phone_data['stock'],
                    phone_brand=phone_data['phone_brand'],
                    phone_category=phone_data['phone_category'],
                    storage=phone_data['storage'],
                    screen_size=phone_data['screen_size'],
                    processor=phone_data['processor'],
                    ram=phone_data['ram'],
                    camera=phone_data['camera'],
                    battery=phone_data['battery'],
                    operating_system=phone_data['operating_system'],
                    connectivity=phone_data['connectivity'],
                    is_active=True,
                    on_sale=phone_data.get('on_sale', False),
                    discount_percentage=phone_data.get('discount_percentage', 0)
                )

                if image_file:
                    product.image.save(image_file.name, image_file, save=False)

                product.save()
                self.stdout.write(self.style.SUCCESS(f"✅ Téléphone créé: {phone_data['name']}"))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Erreur avec {phone_data['name']}: {str(e)}"))

        self.stdout.write(self.style.SUCCESS('🎉 Base de données peuplée avec succès !'))
        self.stdout.write(f'📊 Total produits: {Product.objects.count()}')
        self.stdout.write(f'🛏️ Draps: {Product.objects.filter(product_type="SHEET").count()}')
        self.stdout.write(f'📱 Téléphones: {Product.objects.filter(product_type="PHONE").count()}')