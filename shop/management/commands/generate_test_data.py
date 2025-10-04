import os
import random
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.core.files import File
from django.utils import timezone
from shop.models import Category, Product, Order, OrderItem, RepairRequest
from django.contrib.auth.models import User
import requests
from io import BytesIO


class Command(BaseCommand):
    help = 'Génère des données de test pour l\'interface administrateur'

    def handle(self, *args, **options):
        self.stdout.write('🚀 Génération des données de test...')

        # Créer un superutilisateur si nécessaire
        self.create_admin_user()

        # Créer les catégories
        categories = self.create_categories()

        # Créer les produits avec de vraies images
        products = self.create_products(categories)

        # Créer des commandes
        self.create_orders(products)

        # Créer des demandes de réparation
        self.create_repair_requests()

        self.stdout.write('✅ Données de test générées avec succès!')

    def create_admin_user(self):
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@techandhome.ci',
                password='admin123'
            )
            self.stdout.write('👤 Superutilisateur créé: admin/admin123')

    def create_categories(self):
        categories_data = [
            {'name': 'Draps de Luxe', 'description': 'Draps en coton de haute qualité'},
            {'name': 'Draps Économiques', 'description': 'Draps abordables et confortables'},
            {'name': 'Smartphones Premium', 'description': 'Téléphones haut de gamme'},
            {'name': 'Smartphones Reconditionnés', 'description': 'Téléphones reconditionnés comme neufs'},
        ]

        categories = []
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={'description': cat_data['description']}
            )
            categories.append(category)
            if created:
                self.stdout.write(f'📁 Catégorie créée: {category.name}')

        return categories

    def download_image(self, url, filename):
        """Télécharge une image depuis une URL"""
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return BytesIO(response.content)
        except:
            self.stdout.write(f'⚠️ Impossible de télécharger: {url}')
        return None

    def create_products(self, categories):
        products_data = [
            # DRAPS - avec des valeurs par défaut pour les champs téléphone
            {
                'name': 'Draps en Coton Égyptien 300 Fils',
                'description': 'Draps de luxe en coton égyptien 300 fils, extrêmement doux et respirants. Parfaits pour un sommeil confortable.',
                'price': 89.99,
                'product_type': 'SHEET',
                'category': categories[0],
                'sheet_size': 'QUEEN',
                'color': 'WHITE',
                'material': 'Coton Égyptien 300 fils',
                'stock': 45,
                'on_sale': False,
                'image_url': 'https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=500&h=500&fit=crop',
                # Champs téléphone avec valeurs par défaut pour les draps
                'storage': 'Non applicable',
                'screen_size': 'Non applicable',
                'processor': 'Non applicable',
                'ram': 'Non applicable',
                'camera': 'Non applicable',
                'battery': 'Non applicable',
                'operating_system': 'Non applicable',
                'connectivity': 'Non applicable',
            },
            {
                'name': 'Draps en Bambou Biologique',
                'description': 'Draps écologiques en bambou, hypoallergéniques et thermorégulateurs. Idéals pour les peaux sensibles.',
                'price': 74.99,
                'product_type': 'SHEET',
                'category': categories[0],
                'sheet_size': 'KING',
                'color': 'GRAY',
                'material': 'Bambou biologique',
                'stock': 32,
                'on_sale': True,
                'discount_percentage': 15,
                'image_url': 'https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=500&h=500&fit=crop',
                'storage': 'Non applicable',
                'screen_size': 'Non applicable',
                'processor': 'Non applicable',
                'ram': 'Non applicable',
                'camera': 'Non applicable',
                'battery': 'Non applicable',
                'operating_system': 'Non applicable',
                'connectivity': 'Non applicable',
            },
            {
                'name': 'Draps en Lin Naturel',
                'description': 'Draps en lin naturel, robustes et respirants. Parfaits pour les climats chauds.',
                'price': 99.99,
                'product_type': 'SHEET',
                'category': categories[0],
                'sheet_size': 'DOUBLE',
                'color': 'BEIGE',
                'material': 'Lin naturel',
                'stock': 28,
                'on_sale': False,
                'image_url': 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=500&h=500&fit=crop',
                'storage': 'Non applicable',
                'screen_size': 'Non applicable',
                'processor': 'Non applicable',
                'ram': 'Non applicable',
                'camera': 'Non applicable',
                'battery': 'Non applicable',
                'operating_system': 'Non applicable',
                'connectivity': 'Non applicable',
            },
            {
                'name': 'Draps en Coton Percale',
                'description': 'Draps en coton percale, légers et frais. Touche de luxe à prix abordable.',
                'price': 49.99,
                'product_type': 'SHEET',
                'category': categories[1],
                'sheet_size': 'SIMPLE',
                'color': 'BLUE',
                'material': 'Coton percale',
                'stock': 67,
                'on_sale': True,
                'discount_percentage': 20,
                'image_url': 'https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=500&h=500&fit=crop',
                'storage': 'Non applicable',
                'screen_size': 'Non applicable',
                'processor': 'Non applicable',
                'ram': 'Non applicable',
                'camera': 'Non applicable',
                'battery': 'Non applicable',
                'operating_system': 'Non applicable',
                'connectivity': 'Non applicable',
            },
            {
                'name': 'Draps Colorés en Jersey',
                'description': 'Draps stretch en jersey de coton, ultra-confortables et disponibles en plusieurs couleurs vives.',
                'price': 39.99,
                'product_type': 'SHEET',
                'category': categories[1],
                'sheet_size': 'DOUBLE',
                'color': 'PINK',
                'material': 'Jersey de coton',
                'stock': 0,  # Rupture de stock
                'on_sale': False,
                'image_url': 'https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=500&h=500&fit=crop',
                'storage': 'Non applicable',
                'screen_size': 'Non applicable',
                'processor': 'Non applicable',
                'ram': 'Non applicable',
                'camera': 'Non applicable',
                'battery': 'Non applicable',
                'operating_system': 'Non applicable',
                'connectivity': 'Non applicable',
            },
            {
                'name': 'Draps Satin de Soie',
                'description': 'Draps en satin de soie, d\'une douceur exceptionnelle. Pour des nuits de rêve.',
                'price': 129.99,
                'product_type': 'SHEET',
                'category': categories[0],
                'sheet_size': 'KING',
                'color': 'GREEN',
                'material': 'Satin de soie',
                'stock': 15,
                'on_sale': True,
                'discount_percentage': 10,
                'image_url': 'https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=500&h=500&fit=crop',
                'storage': 'Non applicable',
                'screen_size': 'Non applicable',
                'processor': 'Non applicable',
                'ram': 'Non applicable',
                'camera': 'Non applicable',
                'battery': 'Non applicable',
                'operating_system': 'Non applicable',
                'connectivity': 'Non applicable',
            },

            # TÉLÉPHONES - avec des valeurs par défaut pour les champs draps
            {
                'name': 'iPhone 15 Pro Max 256GB',
                'description': 'Dernier iPhone avec écran Dynamic Island, caméra 48MP et puce A17 Pro. Performance exceptionnelle.',
                'price': 1299.99,
                'product_type': 'PHONE',
                'category': categories[2],
                'phone_brand': 'APPLE',
                'phone_category': 'BESTSELLER',
                'storage': '256GB',
                'screen_size': '6.7" Super Retina XDR',
                'processor': 'Apple A17 Pro',
                'ram': '8GB',
                'camera': 'Triple 48MP + 12MP + 12MP',
                'battery': '4422mAh',
                'operating_system': 'iOS 17',
                'connectivity': '5G, Wi-Fi 6E, Bluetooth 5.3',
                'stock': 23,
                'on_sale': False,
                'image_url': 'https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=500&h=500&fit=crop',
                # Champs draps avec valeurs par défaut pour les téléphones
                'sheet_size': None,
                'color': None,
                'material': '',
            },
            {
                'name': 'Samsung Galaxy S24 Ultra',
                'description': 'Smartphone Android flagship avec S-Pen, écran Dynamic AMOLED et AI intégrée.',
                'price': 1199.99,
                'product_type': 'PHONE',
                'category': categories[2],
                'phone_brand': 'GALAXY',
                'phone_category': 'BESTSELLER',
                'storage': '512GB',
                'screen_size': '6.8" Dynamic AMOLED 2X',
                'processor': 'Snapdragon 8 Gen 3',
                'ram': '12GB',
                'camera': 'Quad 200MP + 50MP + 12MP + 10MP',
                'battery': '5000mAh',
                'operating_system': 'Android 14',
                'connectivity': '5G, Wi-Fi 7, Bluetooth 5.3',
                'stock': 18,
                'on_sale': True,
                'discount_percentage': 8,
                'image_url': 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=500&h=500&fit=crop',
                'sheet_size': None,
                'color': None,
                'material': '',
            },
            {
                'name': 'Google Pixel 8 Pro',
                'description': 'Smartphone Google avec les meilleures fonctionnalités photo et Android pur.',
                'price': 999.99,
                'product_type': 'PHONE',
                'category': categories[2],
                'phone_brand': 'PIXEL',
                'phone_category': 'OFFER',
                'storage': '128GB',
                'screen_size': '6.7" LTPO OLED',
                'processor': 'Google Tensor G3',
                'ram': '12GB',
                'camera': 'Triple 50MP + 48MP + 48MP',
                'battery': '5050mAh',
                'operating_system': 'Android 14',
                'connectivity': '5G, Wi-Fi 7, Bluetooth 5.3',
                'stock': 34,
                'on_sale': False,
                'image_url': 'https://images.unsplash.com/photo-1592899677977-9c10ca588bbd?w=500&h=500&fit=crop',
                'sheet_size': None,
                'color': None,
                'material': '',
            },
            {
                'name': 'OnePlus 12',
                'description': 'Performance extrême avec charge ultra-rapide 100W et écran Fluid AMOLED.',
                'price': 899.99,
                'product_type': 'PHONE',
                'category': categories[2],
                'phone_brand': 'ONEPLUS',
                'phone_category': 'BESTSELLER',
                'storage': '256GB',
                'screen_size': '6.82" LTPO AMOLED',
                'processor': 'Snapdragon 8 Gen 3',
                'ram': '16GB',
                'camera': 'Triple 50MP + 64MP + 48MP',
                'battery': '5400mAh',
                'operating_system': 'OxygenOS 14',
                'connectivity': '5G, Wi-Fi 7, Bluetooth 5.4',
                'stock': 27,
                'on_sale': True,
                'discount_percentage': 12,
                'image_url': 'https://images.unsplash.com/photo-1556656793-08538906a9f8?w=500&h=500&fit=crop',
                'sheet_size': None,
                'color': None,
                'material': '',
            },
            {
                'name': 'Xiaomi 14 Pro',
                'description': 'Smartphone innovant avec écran courbe et système photo Leica.',
                'price': 849.99,
                'product_type': 'PHONE',
                'category': categories[2],
                'phone_brand': 'XIAOMI',
                'phone_category': 'OFFER',
                'storage': '512GB',
                'screen_size': '6.73" LTPO AMOLED',
                'processor': 'Snapdragon 8 Gen 3',
                'ram': '16GB',
                'camera': 'Triple 50MP + 50MP + 50MP',
                'battery': '4880mAh',
                'operating_system': 'HyperOS',
                'connectivity': '5G, Wi-Fi 7, Bluetooth 5.4',
                'stock': 0,  # Rupture de stock
                'on_sale': False,
                'image_url': 'https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=500&h=500&fit=crop',
                'sheet_size': None,
                'color': None,
                'material': '',
            },
            {
                'name': 'iPhone 13 Reconditionné',
                'description': 'iPhone 13 reconditionné comme neuf, garantie 12 mois. Excellent rapport qualité-prix.',
                'price': 599.99,
                'product_type': 'PHONE',
                'category': categories[3],
                'phone_brand': 'APPLE',
                'phone_category': 'REFURBISHED',
                'storage': '128GB',
                'screen_size': '6.1" Super Retina XDR',
                'processor': 'Apple A15 Bionic',
                'ram': '4GB',
                'camera': 'Double 12MP + 12MP',
                'battery': '3240mAh',
                'operating_system': 'iOS 17',
                'connectivity': '5G, Wi-Fi 6, Bluetooth 5.0',
                'stock': 42,
                'on_sale': True,
                'discount_percentage': 15,
                'image_url': 'https://images.unsplash.com/photo-1632661674598-2fd40dcccdb8?w=500&h=500&fit=crop',
                'sheet_size': None,
                'color': None,
                'material': '',
            },
            {
                'name': 'Samsung Galaxy S22 Reconditionné',
                'description': 'Galaxy S22 reconditionné, état impeccable. Performance flagship à prix réduit.',
                'price': 449.99,
                'product_type': 'PHONE',
                'category': categories[3],
                'phone_brand': 'GALAXY',
                'phone_category': 'REFURBISHED',
                'storage': '256GB',
                'screen_size': '6.1" Dynamic AMOLED 2X',
                'processor': 'Snapdragon 8 Gen 1',
                'ram': '8GB',
                'camera': 'Triple 50MP + 12MP + 10MP',
                'battery': '3700mAh',
                'operating_system': 'Android 14',
                'connectivity': '5G, Wi-Fi 6, Bluetooth 5.2',
                'stock': 38,
                'on_sale': False,
                'image_url': 'https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=500&h=500&fit=crop',
                'sheet_size': None,
                'color': None,
                'material': '',
            },
        ]

        products = []
        for product_data in products_data:
            # Télécharger l'image
            image_file = None
            if product_data.get('image_url'):
                image_content = self.download_image(product_data['image_url'],
                                                    f"{product_data['name'].replace(' ', '_')}.jpg")
                if image_content:
                    image_file = File(image_content, name=f"{product_data['name'].replace(' ', '_')}.jpg")

            # Créer le produit avec TOUS les champs requis
            product = Product.objects.create(
                name=product_data['name'],
                description=product_data['description'],
                price=product_data['price'],
                category=product_data['category'],
                product_type=product_data['product_type'],
                stock=product_data['stock'],
                on_sale=product_data.get('on_sale', False),
                discount_percentage=product_data.get('discount_percentage', 0),
                is_active=True,

                # Champs spécifiques aux draps
                sheet_size=product_data.get('sheet_size'),
                color=product_data.get('color'),
                material=product_data.get('material', ''),

                # Champs spécifiques aux téléphones (TOUS requis)
                phone_brand=product_data.get('phone_brand', ''),
                phone_category=product_data.get('phone_category', ''),
                storage=product_data.get('storage', 'Non applicable'),
                screen_size=product_data.get('screen_size', 'Non applicable'),
                processor=product_data.get('processor', 'Non applicable'),
                ram=product_data.get('ram', 'Non applicable'),
                camera=product_data.get('camera', 'Non applicable'),
                battery=product_data.get('battery', 'Non applicable'),
                operating_system=product_data.get('operating_system', 'Non applicable'),
                connectivity=product_data.get('connectivity', 'Non applicable'),
            )

            # Ajouter l'image si téléchargée
            if image_file:
                product.image.save(f"{product_data['name'].replace(' ', '_')}.jpg", image_file)
                product.save()

            products.append(product)
            self.stdout.write(f'📦 Produit créé: {product.name}')

        return products

    def create_orders(self, products):
        customers = [
            {'name': 'Marie Koné', 'email': 'marie.kone@email.ci', 'phone': '+225 07 12 34 56 78'},
            {'name': 'Jean Traoré', 'email': 'jean.traore@email.ci', 'phone': '+225 05 23 45 67 89'},
            {'name': 'Amina Diarra', 'email': 'amina.diarra@email.ci', 'phone': '+225 01 34 56 78 90'},
            {'name': 'Paul Kouassi', 'email': 'paul.kouassi@email.ci', 'phone': '+225 07 45 67 89 01'},
            {'name': 'Fatou Bamba', 'email': 'fatou.bamba@email.ci', 'phone': '+225 05 56 78 90 12'},
            {'name': 'Marc Yapo', 'email': 'marc.yapo@email.ci', 'phone': '+225 01 67 89 01 23'},
            {'name': 'Sarah Cissé', 'email': 'sarah.cisse@email.ci', 'phone': '+225 07 78 90 12 34'},
            {'name': 'David Fofana', 'email': 'david.fofana@email.ci', 'phone': '+225 05 89 01 23 45'},
        ]

        statuses = ['PENDING', 'CONFIRMED', 'SHIPPED', 'DELIVERED', 'CANCELLED']
        status_weights = [2, 3, 2, 5, 1]  # Plus de commandes livrées

        # Créer des commandes sur les 6 derniers mois
        for i in range(120):  # 120 commandes au total
            customer = random.choice(customers)

            # Date aléatoire dans les 6 derniers mois
            days_ago = random.randint(1, 180)
            order_date = timezone.now() - timedelta(days=days_ago)

            # Statut basé sur l'ancienneté de la commande
            if days_ago <= 7:
                status = random.choices(statuses, weights=[4, 3, 2, 1, 1], k=1)[0]
            elif days_ago <= 30:
                status = random.choices(statuses, weights=[2, 3, 3, 2, 1], k=1)[0]
            else:
                status = random.choices(statuses, weights=[1, 2, 2, 4, 1], k=1)[0]

            order = Order.objects.create(
                full_name=customer['name'],
                email=customer['email'],
                phone_number=customer['phone'],
                address=f"{random.randint(1, 200)} Rue des Commerces",
                city="Abidjan",
                country="Côte d'Ivoire",
                total_price=0,  # Sera calculé après
                status=status,
                created_at=order_date,
                updated_at=order_date
            )

            # Générer un numéro de commande réaliste
            order.order_number = f"CMD{order.id:06d}"
            order.save()

            # Ajouter des articles à la commande
            total_price = 0
            num_items = random.randint(1, 4)
            selected_products = random.sample(products, min(num_items, len(products)))

            for product in selected_products:
                quantity = random.randint(1, 3)
                item_price = product.get_discounted_price() if product.on_sale else product.price
                item_total = item_price * quantity

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    product_name=product.name,
                    product_price=item_price,
                    quantity=quantity
                )

                total_price += item_total

            # Mettre à jour le prix total
            order.total_price = total_price
            order.save()

        self.stdout.write(f'📦 {Order.objects.count()} commandes créées')

    def create_repair_requests(self):
        devices = [
            'iPhone 12', 'iPhone 13', 'iPhone 14', 'Samsung Galaxy S21', 'Samsung Galaxy S22',
            'Huawei P40', 'Xiaomi Redmi Note 11', 'Oppo A96', 'Google Pixel 6', 'OnePlus 9'
        ]

        issues = [
            ('SCREEN', 'Écran cassé'),
            ('BATTERY', 'Problème de batterie'),
            ('CHARGE', 'Problème de charge'),
            ('SOFTWARE', 'Problème logiciel'),
            ('WATER', 'Dégât des eaux'),
            ('OTHER', 'Autre problème')
        ]

        statuses = ['PENDING', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED']
        status_weights = [3, 2, 4, 1]  # Plus de réparations terminées

        customers = [
            {'name': 'Koffi N\'Guessan', 'phone': '+225 07 11 22 33 44', 'email': 'koffi.nguessan@email.ci'},
            {'name': 'Adjoua Kouamé', 'phone': '+225 05 22 33 44 55', 'email': 'adjoua.kouame@email.ci'},
            {'name': 'Yao Bédié', 'phone': '+225 01 33 44 55 66', 'email': 'yao.bedie@email.ci'},
            {'name': 'Aïcha Touré', 'phone': '+225 07 44 55 66 77', 'email': 'aicha.toure@email.ci'},
            {'name': 'Moussa Konaté', 'phone': '+225 05 55 66 77 88', 'email': 'moussa.konate@email.ci'},
        ]

        descriptions = {
            'SCREEN': [
                "Écran complètement cassé après une chute",
                "Écran fissuré dans le coin supérieur gauche",
                "Écran noir mais téléphone allumé",
                "Écran qui clignote de manière aléatoire"
            ],
            'BATTERY': [
                "Batterie qui se décharge très rapidement",
                "Téléphone qui s'éteint à 30% de batterie",
                "Batterie qui gonfle",
                "Ne tient pas la charge plus de 2 heures"
            ],
            'CHARGE': [
                "Ne charge plus quand branché",
                "Charge par intermittence",
                "Port de charge endommagé",
                "Câble ne reste pas en place"
            ],
            'SOFTWARE': [
                "Téléphone qui redémarre tout seul",
                "Applications qui se ferment brutalement",
                "Lentesse générale du système",
                "Mise à jour impossible"
            ],
            'WATER': [
                "Tombé dans l'eau hier, plus de réponse",
                "Exposé à la pluie, problèmes d'affichage",
                "Liquéide renversé sur le clavier",
                "Humidité détectée dans le port de charge"
            ],
            'OTHER': [
                "Haut-parleur ne fonctionne plus",
                "Boutons volume défectueux",
                "Appareil photo flou",
                "Problème de connexion Wi-Fi"
            ]
        }

        for i in range(50):  # 50 demandes de réparation
            customer = random.choice(customers)
            device = random.choice(devices)
            issue_type, issue_display = random.choice(issues)
            status = random.choices(statuses, weights=status_weights, k=1)[0]

            # Date aléatoire dans les 3 derniers mois
            days_ago = random.randint(1, 90)
            created_date = timezone.now() - timedelta(days=days_ago)

            # Date de mise à jour (plus récente pour les statuts en cours)
            if status in ['PENDING', 'IN_PROGRESS']:
                updated_date = created_date + timedelta(days=random.randint(1, 7))
            else:
                updated_date = created_date + timedelta(days=random.randint(3, 14))

            RepairRequest.objects.create(
                full_name=customer['name'],
                phone_number=customer['phone'],
                email=customer['email'],
                issue_type=issue_type,
                device_model=device,
                description=random.choice(descriptions[issue_type]),
                status=status,
                created_at=created_date,
                updated_at=updated_date
            )

        self.stdout.write(f'🔧 {RepairRequest.objects.count()} demandes de réparation créées')