import csv
import re
from django.core.management.base import BaseCommand
# Ajustez le nom de l'application si nécessaire (ex: rfid_reader_app)
from rfid_reader_app.models import Category, Subcategory, Criteria 

class Command(BaseCommand):
    help = "Imports categories, subcategories, and technical criteria by auto-detecting model fields"

    def handle(self, *args, **options):
        file_path = "criteres.csv" 
        self.stdout.write(self.style.SUCCESS(f"Starting import from {file_path}..."))

        # --- DÉTECTION AUTOMATIQUE ET DYNAMIQUE DES CHAMPS ---
        # 1. Recherche du champ textuel pour Category ('category' ou 'name')
        cat_fields = [f.name for f in Category._meta.fields]
        cat_text_attr = 'category' if 'category' in cat_fields else 'name'
        
        # 2. Recherche du champ textuel pour Subcategory ('subcategory' ou 'name')
        subcat_fields = [f.name for f in Subcategory._meta.fields]
        subcat_text_attr = 'subcategory' if 'subcategory' in subcat_fields else 'name'
        
        # 3. Recherche du nom de la clé étrangère (ForeignKey) vers Category dans Subcategory
        subcat_fk_attr = 'category'
        for f in Subcategory._meta.fields:
            if f.is_relation and f.related_model == Category:
                subcat_fk_attr = f.name
                break

        # Affichage informatif pour le suivi dans la console
        self.stdout.write(f" -> Mapping Category text field to: '{cat_text_attr}'")
        self.stdout.write(f" -> Mapping Subcategory text field to: '{subcat_text_attr}' (FK: '{subcat_fk_attr}')")
        # -----------------------------------------------------

        try:
            with open(file_path, newline='', encoding='utf-8-sig') as csvfile:
                reader = csv.DictReader(csvfile, delimiter=',')
                
                count_lines = 0
                for row in reader:
                    cat_name = row['Category'].strip()
                    subcat_name = row['Subcategory'].strip()
                    criteria_string = row['Technical criteria'].strip()

                    if not cat_name or not subcat_name:
                        continue

                    # 1. Gestion de la Catégorie (s'adapte au nom du champ détecté)
                    cat_kwargs = {cat_text_attr: cat_name}
                    category, _ = Category.objects.get_or_create(**cat_kwargs)

                    # 2. Gestion de la Sous-catégorie (s'adapte aux champs détectés)
                    subcat_kwargs = {
                        subcat_text_attr: subcat_name,
                        subcat_fk_attr: category
                    }
                    subcategory, _ = Subcategory.objects.get_or_create(**subcat_kwargs)

                    # 3. Traitement des critères techniques
                    if criteria_string:
                        raw_criteria_list = [c.strip() for c in criteria_string.split('|')]
                        
                        for crit_raw in raw_criteria_list:
                            if not crit_raw:
                                continue
                            
                            # Extraction du nom du critère et de son unité entre parenthèses
                            match = re.match(r"^(.*?)\s*\((.*?)\)$", crit_raw)
                            if match:
                                crit_name = match.group(1).strip()
                                crit_unit = match.group(2).strip()
                            else:
                                crit_name = crit_raw
                                crit_unit = None

                            # Création du critère (on cible 'criteria' et 'unit' validés par votre dernière erreur)
                            criteria, _ = Criteria.objects.get_or_create(
                                criteria=crit_name,
                                defaults={'unit': crit_unit}
                            )

                            # Liaison ManyToMany via le champ 'subcategories'
                            criteria.subcategories.add(subcategory)

                    count_lines += 1

            self.stdout.write(self.style.SUCCESS(f"\nSuccessfully imported {count_lines} rows into the database!"))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"Error: The file '{file_path}' was not found."))
        except KeyError as e:
            self.stdout.write(self.style.ERROR(f"\n[ERROR] Column header missing: {str(e)}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"An unexpected error occurred: {str(e)}"))