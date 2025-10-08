# production/management/commands/setup_petit_paris_data.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from production.models import LigneProduction, Produit, Equipe, ProductionRecord, Alerte


class Command(BaseCommand):
    help = 'Crée les données de base complètes pour Le Petit Paris'

    def handle(self, *args, **options):
        self.stdout.write("🚀 Création des données de base pour Le Petit Paris...")

        # ================================
        # 1. CRÉER LES LIGNES DE PRODUCTION
        # ================================
        self.stdout.write("\n📋 Création des lignes de production...")

        # Supprimer les anciennes si elles existent (pour éviter les doublons)
        LigneProduction.objects.all().delete()

        lignes_data = [
            {'numero': 1, 'nom': 'Ligne 1'},
            {'numero': 2, 'nom': 'Ligne 2'},
            {'numero': 3, 'nom': 'Ligne 3'},
        ]

        lignes = []
        for ligne_data in lignes_data:
            ligne = LigneProduction.objects.create(
                numero=ligne_data['numero'],
                nom=ligne_data['nom'],
                is_active=True
            )
            lignes.append(ligne)
            self.stdout.write(f"✅ Créé: {ligne}")

        # ================================
        # 2. CRÉER LES PRODUITS
        # ================================
        self.stdout.write("\n🥫 Création des produits...")

        # Supprimer les anciens produits
        Produit.objects.all().delete()

        # DCT - Double Concentré de Tomate
        produits_dct_data = [
            "DCT 5/1", "DCT 4/4", "DCT 1/2", "DCT 1/4", "DCT 1/6"
        ]
        produits_dct = []
        for nom in produits_dct_data:
            produit = Produit.objects.create(
                nom=nom,
                description=f"Double Concentré de Tomate - Boîte {nom.split(' ')[1]}"
            )
            produits_dct.append(produit)

        # Tomate Concassée
        varietes_concassee = ['Ail', 'Basilic', 'Nature']
        formats_concassee = ['5/1', '3/1', '1/2']
        produits_concassee = []
        
        for variete in varietes_concassee:
            for format_boite in formats_concassee:
                if variete == 'Nature':
                    nom = f"Tomate Concassée Nature {format_boite}"
                    description = f"Tomate Concassée Nature - Boîte {format_boite}"
                else:
                    nom = f"Tomate Concassée {variete} {format_boite}"
                    description = f"Tomate Concassée au {variete} - Boîte {format_boite}"
                
                produit = Produit.objects.create(nom=nom, description=description)
                produits_concassee.append(produit)

        # Sauce Pizza
        formats_pizza = ['5/1', '3/1', '1/2']
        produits_sauce_pizza = []
        for format_boite in formats_pizza:
            produit = Produit.objects.create(
                nom=f"Sauce Pizza {format_boite}",
                description=f"Sauce Pizza - Boîte {format_boite}"
            )
            produits_sauce_pizza.append(produit)

        # Confitures
        varietes_confiture = ['Pomme', 'Fraise', 'Figue', 'Abricot', 'Coing']
        formats_confiture = ['4/4', '1/2', '3/2']
        produits_confitures = []
        
        for variete in varietes_confiture:
            for format_boite in formats_confiture:
                nom = f"Confiture {variete} {format_boite}"
                description = f"Confiture de {variete} - Boîte {format_boite}"
                produit = Produit.objects.create(nom=nom, description=description)
                produits_confitures.append(produit)

        # Harissa
        formats_harissa = ['3/1', '1/2', '1/6']
        produits_harissa = []
        for format_boite in formats_harissa:
            produit = Produit.objects.create(
                nom=f"Harissa {format_boite}",
                description=f"Harissa - Boîte {format_boite}"
            )
            produits_harissa.append(produit)

        tous_produits = produits_dct + produits_concassee + produits_sauce_pizza + produits_confitures + produits_harissa

        self.stdout.write(f"\n✅ Créé {len(tous_produits)} produits:")
        self.stdout.write(f"   📦 DCT: {len(produits_dct)} formats")
        self.stdout.write(f"   🍅 Tomate Concassée: {len(produits_concassee)} variétés/formats")
        self.stdout.write(f"   🍕 Sauce Pizza: {len(produits_sauce_pizza)} formats")
        self.stdout.write(f"   🍓 Confitures: {len(produits_confitures)} variétés/formats")
        self.stdout.write(f"   🌶️ Harissa: {len(produits_harissa)} formats")

        # ================================
        # 3. CRÉER LES UTILISATEURS OPÉRATEURS
        # ================================
        self.stdout.write("\n👷 Création des utilisateurs opérateurs...")

        # Supprimer les anciens opérateurs s'ils existent
        User.objects.filter(username__startswith='operateur').delete()

        operateurs_data = [
            {
                'username': 'operateur1',
                'password': 'op123456',
                'first_name': 'Ahmed',
                'last_name': 'Ben Salah',
                'email': 'ahmed.bensalah@lepetitparis.com'
            },
            {
                'username': 'operateur2',
                'password': 'op123456',
                'first_name': 'Fatima',
                'last_name': 'Trabelsi',
                'email': 'fatima.trabelsi@lepetitparis.com'
            },
            {
                'username': 'operateur3',
                'password': 'op123456',
                'first_name': 'Mohamed',
                'last_name': 'Gharbi',
                'email': 'mohamed.gharbi@lepetitparis.com'
            }
        ]

        operateurs = []
        for op_data in operateurs_data:
            user = User.objects.create_user(
                username=op_data['username'],
                password=op_data['password'],
                first_name=op_data['first_name'],
                last_name=op_data['last_name'],
                email=op_data['email']
            )
            operateurs.append(user)
            self.stdout.write(f"✅ Créé utilisateur: {user.username} ({user.first_name} {user.last_name})")

        # Créer un admin si demandé
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'first_name': 'Admin',
                'last_name': 'Le Petit Paris',
                'email': 'admin@lepetitparis.com',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(f"✅ Créé administrateur: {admin_user.username}")

        # ================================
        # 4. CRÉER LES ÉQUIPES
        # ================================
        self.stdout.write("\n⏰ Création des équipes de travail...")

        # Supprimer les anciennes équipes
        Equipe.objects.all().delete()

        equipes_data = [
            {'nom': 'Équipe du Matin', 'horaire': '6h-14h', 'operateur': operateurs[0]},
            {'nom': 'Équipe de l\'Après-midi', 'horaire': '14h-22h', 'operateur': operateurs[1]},
            {'nom': 'Équipe de Nuit', 'horaire': '22h-6h', 'operateur': operateurs[2]},
        ]

        equipes = []
        for equipe_data in equipes_data:
            equipe = Equipe.objects.create(
                nom=equipe_data['nom'],
                horaire=equipe_data['horaire'],
                operateur=equipe_data['operateur']
            )
            equipes.append(equipe)
            self.stdout.write(f"✅ Créé équipe: {equipe}")

        # ================================
        # 5. CRÉER QUELQUES DONNÉES DE TEST
        # ================================
        self.stdout.write("\n📊 Création de données de test...")

        # Créer quelques enregistrements de production pour tester
        test_records = []

        # Production DCT sur Ligne 1
        test_record1 = ProductionRecord.objects.create(
            ligne_production=lignes[0],
            produit=produits_dct[0],  # DCT 5/1
            equipe=equipes[0],
            operateur=operateurs[0],
            palettes_produites=8,
            dechets_boites=3.2,
            duree_arret_minutes=0,
            commentaires="Production normale - DCT 5/1"
        )
        test_records.append(test_record1)

        # Production Tomate Concassée avec arrêt
        test_record2 = ProductionRecord.objects.create(
            ligne_production=lignes[1],
            produit=produits_concassee[0],  # Tomate Concassée Ail 5/1
            equipe=equipes[1],
            operateur=operateurs[1],
            palettes_produites=6,
            dechets_boites=2.1,
            duree_arret_minutes=25,
            cause_arret="Nettoyage changement de produit",
            commentaires="Changement Basilic vers Ail"
        )
        test_records.append(test_record2)

        # Production Confiture
        test_record3 = ProductionRecord.objects.create(
            ligne_production=lignes[2],
            produit=produits_confitures[0],  # Confiture Pomme 4/4
            equipe=equipes[2],
            operateur=operateurs[2],
            palettes_produites=4,
            dechets_boites=1.8,
            duree_arret_minutes=0,
            commentaires="Production de nuit - Confiture pomme"
        )
        test_records.append(test_record3)

        for record in test_records:
            self.stdout.write(f"✅ Créé enregistrement test: {record}")

        # Créer une alerte pour l'arrêt
        alerte_test = Alerte.objects.create(
            production_record=test_record2,
            type_alerte='arret',
            message=f"Arrêt de {test_record2.duree_arret_minutes} minutes sur {test_record2.ligne_production}. Cause: {test_record2.cause_arret}"
        )

        self.stdout.write(f"✅ Créé alerte test: {alerte_test}")

        # ================================
        # 6. RÉSUMÉ
        # ================================
        self.stdout.write("\n" + "="*60)
        self.stdout.write("🎉 DONNÉES DE BASE CRÉÉES AVEC SUCCÈS!")
        self.stdout.write("="*60)

        self.stdout.write(f"\n📋 Lignes de production: {LigneProduction.objects.count()}")
        for ligne in LigneProduction.objects.all():
            self.stdout.write(f"   - {ligne}")

        self.stdout.write(f"\n🥫 Produits par catégorie:")
        self.stdout.write(f"   📦 DCT: {len(produits_dct)} formats (5/1, 4/4, 1/2, 1/4, 1/6)")
        self.stdout.write(f"   🍅 Tomate Concassée: {len(produits_concassee)} produits (Ail, Basilic, Nature)")
        self.stdout.write(f"   🍕 Sauce Pizza: {len(produits_sauce_pizza)} formats (5/1, 3/1, 1/2)")
        self.stdout.write(f"   🍓 Confitures: {len(produits_confitures)} produits (Pomme, Fraise, Figue, Abricot, Coing)")
        self.stdout.write(f"   🌶️ Harissa: {len(produits_harissa)} formats (3/1, 1/2, 1/6)")
        self.stdout.write(f"   📊 TOTAL: {Produit.objects.count()} produits")

        self.stdout.write(f"\n👷 Opérateurs: {User.objects.filter(username__startswith='operateur').count()}")
        for user in User.objects.filter(username__startswith='operateur'):
            self.stdout.write(f"   - {user.username} ({user.first_name} {user.last_name})")

        self.stdout.write(f"\n⏰ Équipes: {Equipe.objects.count()}")
        for equipe in Equipe.objects.all():
            self.stdout.write(f"   - {equipe}")

        self.stdout.write(f"\n📊 Enregistrements de test: {ProductionRecord.objects.count()}")
        self.stdout.write(f"🚨 Alertes de test: {Alerte.objects.count()}")

        self.stdout.write("\n" + "="*60)
        self.stdout.write("INFORMATIONS DE CONNEXION:")
        self.stdout.write("="*60)
        self.stdout.write("🔑 Opérateurs:")
        self.stdout.write("   - operateur1 / op123456 (Ahmed Ben Salah - Équipe 6h-14h)")
        self.stdout.write("   - operateur2 / op123456 (Fatima Trabelsi - Équipe 14h-22h)")
        self.stdout.write("   - operateur3 / op123456 (Mohamed Gharbi - Équipe 22h-6h)")
        self.stdout.write("   - admin / admin123 (Administrateur)")
        self.stdout.write("\n💻 URL de l'application: http://127.0.0.1:8000/login/")
        
        self.stdout.write(
            self.style.SUCCESS("\n✅ L'application est maintenant prête pour la production agroalimentaire!")
        )