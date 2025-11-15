from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.conf import settings
from django.utils.text import slugify

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nom")
    description = models.TextField(blank=True, verbose_name="Description")
    image = models.ImageField(upload_to='categories/', blank=True, null=True)

    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"

    def __str__(self):
        return self.name


class Product(models.Model):
    PRODUCT_TYPES = [
        ('ELECTRONICS', 'Électronique & Accessoires'),
        ('DECORATION','Déco & Aménagement')
    ]

    # TAILLES pour les draps
    SHEET_SIZES = [
        ('SIMPLE', 'Simple (90x190cm)'),
        ('DOUBLE', 'Double (140x190cm)'),
        ('QUEEN', 'Queen (160x200cm)'),
        ('KING', 'King (180x200cm)'),
    ]

    # COULEURS pour les draps
    COLORS = [
        ('WHITE', 'Blanc'),
        ('GRAY', 'Gris'),
        ('BLUE', 'Bleu'),
        ('PINK', 'Rose'),
        ('GREEN', 'Vert'),
        ('BEIGE', 'Beige'),
        ('BLACK','Noir')
    ]

    # MARQUES pour les téléphones
    PHONE_BRANDS = [
        ('APPLE','Apple'),
        ('SAMSUNG','Samsung'),
        ('ITEL','Itel'),
        ('TECHNO','Techno'),
        ('HUAWEI','Huawei'),
        ('INFINIX','Infinix'),
        ('XIAOMI', 'Xiaomi'),
        ('PIXEL', 'Pixel'),


    ]

    PHONE_CATEGORIES = [
        ('BESTSELLER', 'Meilleures ventes'),
        ('OFFER', 'Offres spéciales'),
        ('REFURBISHED', 'Reconditionnés'),
        ('ACCESSORY', 'Accessoires'),
    ]
    ELECTRONICS_CATEGORIES = [
        ('SMARTPHONE', 'Smartphones'),
        ('TABLET', 'Tablettes'),
        ('HEADPHONE', 'Casques audio'),
        ('CHARGER', 'Chargeurs & Câbles'),
        ('SMARTWATCH', 'Montres connectées'),
        ('EARBUDS', 'Écouteurs'),
        ('POWERBANK', 'Power banks'),
        ('PHONE_CASE', 'Coques & Protection'),
        ('REFURBISHED', 'Reconditionnés'),
        ('OTHER_ACCESSORY', 'Autres accessoires'),
    ]

    name = models.CharField(max_length=200, verbose_name="Nom")
    description = models.TextField(verbose_name="Description")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Catégorie")
    product_type = models.CharField(max_length=15, choices=PRODUCT_TYPES, verbose_name="Type de produit")
    slug = models.SlugField(max_length=200,unique=True,blank=True,verbose_name="Identifiant URL")

    # Attributs spécifiques aux draps
    sheet_size = models.CharField(max_length=10, choices=SHEET_SIZES, blank=True, null=True, verbose_name="Taille")
    color = models.CharField(max_length=10, choices=COLORS, blank=True, null=True, verbose_name="Couleur")
    material = models.CharField(max_length=100,null=True,blank=True,verbose_name="Matière")

    # Attributs spécifiques aux téléphones
    phone_brand = models.CharField(max_length=20, choices=PHONE_BRANDS, blank=True, null=True, verbose_name="Marque")
    electronics_category = models.CharField(
        max_length=20,
        choices=ELECTRONICS_CATEGORIES,
        blank=True,
        null=True,
        verbose_name="Catégorie électronique"
    )
    phone_category = models.CharField(max_length=20, choices=PHONE_CATEGORIES, blank=True, null=True, verbose_name="Catégorie téléphone")
    storage = models.CharField(max_length=50, null=True,blank=True, verbose_name="Stockage")
    screen_size = models.CharField(max_length=50, null=True, blank=True, verbose_name="Taille écran")

    # NOUVEAUX CHAMPS pour les spécifications techniques
    processor = models.CharField(max_length=100, null=True, blank=True, verbose_name="Processeur")
    camera = models.CharField(max_length=200, null=True, blank=True, verbose_name="Appareil photo")
    battery = models.CharField(max_length=50, null=True, blank=True, verbose_name="Batterie")
    operating_system = models.CharField(max_length=50,null=True, blank=True, verbose_name="Système d'exploitation")
    ram = models.CharField(max_length=50, null=True, blank=True, verbose_name="Mémoire RAM")
    connectivity = models.CharField(max_length=200, null=True, blank=True, verbose_name="Connectivité")

    stock = models.IntegerField(default=0, verbose_name="Stock")
    image_url = models.URLField(blank=True, null=True, verbose_name="URL de l'image")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    on_sale = models.BooleanField(default=False, verbose_name="En promotion")
    discount_percentage = models.IntegerField(default=0, verbose_name="Pourcentage de réduction")
    needs_custom_quote = models.BooleanField(default=False,verbose_name='Nécessite un devis personnalisé')
    decoration_type = models.CharField(
        max_length=20,
        choices=[
            ('SHEET', 'Draps'),
            ('CURTAIN', 'Rideaux'),
            ('CARPET', 'Tapis'),
            ('OTHER', 'Autre décoration'),
        ],
        blank=True,
        null=True,
        verbose_name='Type de décoration'
    )
    price_per_sqm = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name='Prix au m² (pour tapis)'
    )
    class Meta:
        verbose_name = "Produit"
        verbose_name_plural = "Produits"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop:product_detail', kwargs={'slug': self.slug})


    # Méthode pour calculer le prix promotionnel
    def get_discounted_price(self):
        # Si c'est un produit nécessitant un devis, pas de prix fixe
        if self.needs_custom_quote:
            return None
        if self.on_sale and self.discount_percentage > 0:
            discount = self.price * self.discount_percentage / 100
            return self.price - discount
        return self.price

    def get_main_image_url(self):
        """Retourne l'URL de l'image principale"""
        if self.image_url:  # Garde la compatibilité avec l'image actuelle
            return self.image_url

        # Vérifie si la relation images existe (ProductImage peut ne pas être encore défini)
        if hasattr(self, 'images'):
            # Cherche une image marquée comme principale
            primary_image = self.images.filter(is_primary=True).first()
            if primary_image:
                return primary_image.image_url
            # Sinon retourne la première image
            first_image = self.images.first()
            if first_image:
                return first_image.image_url

        return None

    def get_all_images(self):
        """Retourne toutes les images du produit"""
        images = []

        # Ajouter l'image principale (si elle existe)
        if self.image_url:
            images.append({
                'image_url': self.image_url,
                'is_primary': True
            })

        # Ajouter les images supplémentaires de ProductImage
        if hasattr(self, 'images'):
            for img in self.images.all():
                images.append({
                    'image_url': img.image_url,
                    'is_primary': img.is_primary
                })

        return images

    def save(self, *args, **kwargs):
        # DÉPLACER LA GÉNÉRATION DE CATÉGORIE AVANT LE SUPER().SAVE()

        # Déterminer la catégorie automatiquement
        if self.product_type == 'ELECTRONICS':
            category_name = "Électronique & Accessoires"
        else:  # DECORATION
            category_name = "Déco & Aménagement Intérieur"

        # Récupérer ou créer la catégorie
        from .models import Category  # Import circulaire, donc importer ici
        category, created = Category.objects.get_or_create(
            name=category_name,
            defaults={'description': f'Catégorie pour les {category_name.lower()}'}
        )
        self.category = category

        # GÉNÉRER LE SLUG SI VIDE - AJOUTER CETTE PARTIE
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            # S'assurer que le slug est unique
            while Product.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug

        super().save(*args, **kwargs)

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images', verbose_name="Produit")
    image_url = models.URLField(verbose_name="URL de l'image")  # Pour Supabase
    is_primary = models.BooleanField(default=False, verbose_name="Image principale")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")

    class Meta:
        verbose_name = "Image du produit"
        verbose_name_plural = "Images du produit"
        ordering = ['-is_primary', 'created_at']

    def __str__(self):
        return f"Image pour {self.product.name}"


class CustomQuoteRequest(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'En attente'),
        ('CONTACTED', 'Client contacté'),
        ('SCHEDULED', 'Rendez-vous planifié'),
        ('QUOTED', 'Devis envoyé'),
        ('COMPLETED', 'Terminé'),
        ('CANCELLED', 'Annulé'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Produit")
    full_name = models.CharField(max_length=200, verbose_name="Nom complet")
    phone_number = models.CharField(max_length=20, verbose_name="Numéro de téléphone")
    email = models.EmailField(verbose_name="Adresse email")
    address = models.TextField(verbose_name="Adresse de visite")
    city = models.CharField(max_length=100, verbose_name="Ville")

    # Préférences de rendez-vous
    preferred_date = models.DateField(verbose_name="Date préférée")
    preferred_time = models.CharField(
        max_length=20,
        choices=[
            ('MORNING', 'Matin (8h-12h)'),
            ('AFTERNOON', 'Après-midi (14h-18h)'),
            ('EVENING', 'Soir (18h-20h)'),
        ],
        verbose_name="Plage horaire préférée"
    )

    # Informations pour le devis
    room_dimensions = models.CharField(max_length=100, blank=True, verbose_name="Dimensions de la pièce")
    window_measurements = models.CharField(max_length=100, blank=True,
                                           verbose_name="Mesures des fenêtres (pour rideaux)")
    bed_size = models.CharField(max_length=50, blank=True, verbose_name="Taille du lit (pour draps)")
    special_requests = models.TextField(blank=True, verbose_name="Demandes spéciales")
    fabric_preference = models.CharField(max_length=100, blank=True, verbose_name="Préférence de tissu")
    color_preferences = models.CharField(max_length=200, blank=True, verbose_name="Préférences de couleurs")

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING', verbose_name="Statut")
    admin_notes = models.TextField(blank=True, verbose_name="Notes internes")
    quoted_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True,
                                       verbose_name="Prix devisé")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")

    class Meta:
        verbose_name = "Demande de devis personnalisé"
        verbose_name_plural = "Demandes de devis personnalisés"
        ordering = ['-created_at']

    def __str__(self):
        return f"Devis {self.product.name} - {self.full_name}"


class RepairRequest(models.Model):
    ISSUE_TYPES = [
        ('SCREEN', 'Écran cassé'),
        ('BATTERY', 'Problème de batterie'),
        ('CHARGE', 'Problème de charge'),
        ('SOFTWARE', 'Problème logiciel'),
        ('WATER', 'Dégât des eaux'),
        ('OTHER', 'Autre'),
    ]

    STATUS_CHOICES = [
        ('PENDING', 'En attente'),
        ('IN_PROGRESS', 'En cours'),
        ('COMPLETED', 'Terminée'),
        ('CANCELLED', 'Annulée'),
    ]

    full_name = models.CharField(max_length=200, verbose_name="Nom complet")
    phone_number = models.CharField(max_length=20, verbose_name="Numéro de téléphone")
    email = models.EmailField(verbose_name="Adresse email")
    issue_type = models.CharField(max_length=20, choices=ISSUE_TYPES, verbose_name="Type de panne")
    device_model = models.CharField(max_length=100, verbose_name="Modèle de l'appareil")
    description = models.TextField(verbose_name="Description de la panne")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING', verbose_name="Statut")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")

    class Meta:
        verbose_name = "Demande de réparation"
        verbose_name_plural = "Demandes de réparation"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.full_name} - {self.get_issue_type_display()}"


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Utilisateur")
    session_key = models.CharField(max_length=40, null=True, blank=True, verbose_name="Clé de session")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")

    class Meta:
        verbose_name = "Panier"
        verbose_name_plural = "Paniers"

    def __str__(self):
        if self.user:
            return f"Panier de {self.user.username}"
        return f"Panier session {self.session_key}"

    def get_total_price(self):
        return sum(item.get_total_price() for item in self.items.all())

    def get_total_quantity(self):
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items', verbose_name="Panier")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Produit")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Quantité")
    added_at = models.DateTimeField(auto_now_add=True, verbose_name="Date d'ajout")

    class Meta:
        verbose_name = "Article du panier"
        verbose_name_plural = "Articles du panier"
        unique_together = ['cart', 'product']

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    def get_total_price(self):
        if self.product.on_sale:
            return self.product.get_discounted_price() * self.quantity
        return self.product.price * self.quantity


class Order(models.Model):

    STATUS_CHOICES = [
        ('PENDING_PAYMENT', 'En attente de paiement'),
        ('PENDING', 'En attente'),
        ('CONFIRMED', 'Confirmée'),
        ('SHIPPED', 'Expédiée'),
        ('DELIVERED', 'Livrée'),
        ('CANCELLED', 'Annulée'),
    ]

    PAYMENT_METHODS =[
        ('CASH','Paiement à la livraison'),
        ('ONLINE', 'Paiement en ligne'),
    ]

    PAYMENT_STATUS = [
        ('PENDING_PAYMENT', 'En attente de paiement'),
        ('PENDING', 'En attente'),
        ('INITIATED','Paiement initié'),
        ('PAID', 'Payé'),
        ('FAILED', 'Échoué'),
        ('CASH_ON_DELIVERY', 'À payer à la livraison'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Utilisateur"
    )
    order_number = models.CharField(max_length=20, unique=True, verbose_name='Numéro de commande')
    full_name = models.CharField(max_length=200, verbose_name="Nom complet")
    email = models.EmailField(verbose_name="Adresse email")
    phone_number = models.CharField(max_length=20, verbose_name="Numéro de téléphone")
    session_key = models.CharField(max_length=40,blank=True,null=True,verbose_name='Clé de session')
    address = models.TextField(verbose_name="Adresse")
    city = models.CharField(max_length=100, verbose_name="Ville")
    country = models.CharField(max_length=100, default="Cote d'ivoire", verbose_name="Pays")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix total")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING', verbose_name="Statut")  # NOUVEAU CHAMP
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")

    # Payment feature
    payment_method = models.CharField(max_length=20,choices=PAYMENT_METHODS,default='CASH',verbose_name='Méthode de paiement')
    payment_status = models.CharField(max_length=20,choices=PAYMENT_STATUS,default='PENDING',verbose_name='Statut paiement')
    payment_reference = models.CharField(max_length=100,blank=True,verbose_name='Référence paiement')
    winipayer_transaction_id = models.CharField(max_length=100,blank=True,verbose_name='ID Transaction Winipayer')
    winipayer_payment_url = models.URLField(blank=True,verbose_name='URL de paiement Winipayer')


    class Meta:
        verbose_name = "Commande"
        verbose_name_plural = "Commandes"
        ordering = ['-created_at']

    def __str__(self):
        return f"Commande {self.order_number} - {self.full_name}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self.generate_order_number()
        super().save(*args, **kwargs)

    def generate_order_number(self):
        import random
        import string
        return f"CMD{''.join(random.choices(string.digits, k=8))}"


class OrderItem(models.Model):
    """Articles d'une commande (sauvegardes separement du panier)"""
    order = models.ForeignKey(Order,on_delete=models.CASCADE,related_name='items',verbose_name='commande')
    product_name = models.CharField(max_length=200,verbose_name='Nom du produit')
    product_price = models.DecimalField(max_digits=10,decimal_places=2,verbose_name='Prix unitaire')
    quantity = models.PositiveIntegerField(default=1,verbose_name='Quantité')
    product = models.ForeignKey(Product,on_delete=models.SET_NULL,null=True,blank=True,verbose_name='Produit')

    class Meta:
        verbose_name = 'Article de commande'
        verbose_name_plural = 'Articles de commande'

    def __str__(self):
        return f'{self.quantity} x {self.product_name}'

    def get_total_price(self):
        return self.product_price * self.quantity