from django.contrib import admin
from .models import Category, Subcategory, Criteria, CriteriaSubcategory, Package, Component, ComponentCriteria, Tiroclass,Drawer,Position

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display=['id', "name"]
    
@admin.register(Subcategory)
class SubcategoryAdmin(admin.ModelAdmin):
    list_display=['id', "name"]
    
@admin.register(Criteria)
class CriteriaAdmin(admin.ModelAdmin):
    list_display=['id', "criteria","unit"]
    
@admin.register(CriteriaSubcategory)
class CriteriaSubcategoryAdmin(admin.ModelAdmin):
    list_display=['criteria', "subcategory"]
    
@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display=['id',"dimension"]
    
@admin.register(Component)
class ComponentAdmin(admin.ModelAdmin):
    list_display=['id',"mpn","spn","quantity","smd_or_tht","package","category","subcategory","datasheet_url" ]
    
@admin.register(ComponentCriteria)
class ComponentCriteriaAdmin(admin.ModelAdmin):
    list_display=['id',"component","criteria","value"]
    
@admin.register(Tiroclass)
class TiroclassAdmin(admin.ModelAdmin):
    list_display=['id',"tiroclass_name","drawer_count"]
    
@admin.register(Drawer)
class DrawerAdmin(admin.ModelAdmin):
    list_display=['id',"tiroclass","number","drawer_name"]
    
@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display=['id',"component","drawer","row","column"]
    
    
# @admin.register(Tiroclass)
# class TiroclassAdmin(admin.ModelAdmin):
#     list_display = ['id', 'drawer_count']
    
# @admin.register(Drawer)
# class DrawerAdmin(admin.ModelAdmin):
#     list_display = ['id', 'tiroclass', 'number']
  
# @admin.register(Position)
# class PositionAdmin(admin.ModelAdmin):
#     list_display = ['component', 'drawer', 'row', 'column']


# class ComponentSpecInline(admin.StackedInline):
#     model = ComponentSpec
#     extra = 1  # affiche 1 formulaire vide par défaut

#     # Champs affichés selon le type => gérés dynamiquement
#     def get_fields(self, request, obj=None):
#         if obj is None:
#             return []
#         type_fields = {
#             'led':       ['led_type', 'max_current_ma', 'tension_v'],
#             'resistor':  ['value_ohm'],
#             'capacitor': ['capacitor_type', 'capacitance_microf'],
#             'inductor':  ['inductance_mh'],
#             'other':     [],
#         }
#         return type_fields.get(obj.component_type, [])


# @admin.register(Component)
# class ComponentAdmin(admin.ModelAdmin):

#     # Champs affichés dans la liste
#     list_display = ['manufacturer', 'description','mpn','component_type', 
#                     'quantity', 'uid_rfid','unit_price']
    
#     # Champs en lecture seule (remplis automatiquement)
#     readonly_fields = ['supplier_pn', 'datasheet_url']

#     # Champs à remplir manuellement
#     fields = ['uid_rfid', 'mpn', 'component_type', 'quantity',
#               'comment', 'unit_price',
#               # Champs auto en dessous
#               'manufacturer', 'description', 
#               'supplier_pn', 'datasheet_url']
    
#     inlines        = [ComponentSpecInline]



#     def save_model(self, request, obj, form, change):
#         # Si le MPN a changé ou est nouveau → appel API Mouser
#         if obj.mpn:
#             data = get_component_info(obj.mpn)
#             if data:
#                 obj.manufacturer  = data.get("manufacturer", "")
#                 obj.description   = data.get("description", "")
#                 obj.supplier_pn   = data.get("supplier_pn", "")
#                 obj.datasheet_url = data.get("datasheet", "")
#                 # Ne remplace le prix que s'il n'est pas déjà renseigné
#                 if not obj.unit_price:
#                     obj.unit_price = data.get("price_ht") or 0.0

#         super().save_model(request, obj, form, change)
        

#     def save_related(self, request, form, formsets, change):
#         """Crée automatiquement un ComponentSpec si n'existe pas"""
#         super().save_related(request, form, formsets, change)
#         obj = form.instance
#         ComponentSpec.objects.get_or_create(component=obj)
        
