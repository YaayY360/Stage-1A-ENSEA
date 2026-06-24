import csv
from django.core.management.base import BaseCommand
from rfid_reader_app.models import Component, Category, Subcategory

class Command(BaseCommand):

    def add_arguments(self, parser):
        # Permet de passer le chemin du fichier CSV en argument dans le terminal
        parser.add_argument('csv_file', type=str, help="Chemin vers le fichier CSV")

    def handle(self, *args, **options):
        csv_file_path = options['csv_file']

        try:
            with open(csv_file_path, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                # Optionnel : si ton CSV utilise des points-virgules, décommmente la ligne suivante :
                # reader = csv.DictReader(file, delimiter=';')

                count = 0
                for row in reader:
                    # 1. Gestion/Récupération de la Catégorie
                    category_name = row.get('Category', '').strip()
                    category, _ = Category.objects.get_or_create(name=category_name)

                    # 2. Gestion/Récupération de la Sous-catégorie liée à la catégorie
                    subcategory_name = row.get('Subcategory', '').strip()
                    subcategory = None
                    if subcategory_name:
                        subcategory, _ = Subcategory.objects.get_or_create(
                            name=subcategory_name,
                            category=category
                        )

                    # 3. Création ou mise à jour du composant (basé sur le MPN unique)
                    component, created = Component.objects.update_or_create(
                        mpn=row.get('MPN', '').strip(),
                        defaults={
                            'category': category,
                            'subcategory': subcategory,
                            'spn': row.get('SPN', '').strip(),
                            'quantity': int(row.get('Quantity', 0) or 0),
                            'smd_or_tht': row.get('SMD/THT', 'SMD').strip(),
                            'datasheet_url': row.get('Datasheet', '').strip(),
                            # 'unit_price_ht': float(row.get('Unit Price HT (Euro€)', 0.0) or 0.0),
                            # Ajoute ici 'datasheet_url' ou 'image_url' si présents dans ton CSV
                        }
                    )

                    if created:
                        self.stdout.write(self.style.SUCCESS(f"Créé : {component.mpn}"))
                    else:
                        self.stdout.write(self.style.WARNING(f"Mis à jour : {component.mpn}"))
                    
                    count += 1

                self.stdout.write(self.style.SUCCESS(f"Importation terminée ! {count} composants traités."))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"Le fichier {csv_file_path} est introuvable."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Une erreur est survenue : {str(e)}"))