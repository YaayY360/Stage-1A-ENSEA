from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Subcategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE,related_name='subcategories')
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.category.name} → {self.name}"


class Criteria(models.Model):
    criteria = models.CharField(max_length=100)
    unit     = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.criteria} ({self.unit})"


class CriteriaSubcategory(models.Model):
    criteria    = models.ForeignKey(Criteria, on_delete=models.CASCADE,related_name='subcategories')
    subcategory = models.ForeignKey(Subcategory, on_delete=models.CASCADE, related_name='criterias')

    class Meta:
        unique_together = ['criteria', 'subcategory']

    def __str__(self):
        return f"{self.criteria} — {self.subcategory}"


class Package(models.Model):
    dimension = models.CharField(max_length=100)

    def __str__(self):
        return self.dimension


class Component(models.Model):
    SMD_THT_CHOICES = [
        ('SMD', 'SMD'),
        ('THT', 'THT'),
        ('other', 'Other'),
    ]

    mpn         = models.CharField(max_length=100)
    spn         = models.CharField(max_length=100, blank=True)
    quantity    = models.IntegerField(default=0)
    smd_or_tht     = models.CharField(max_length=10,choices=SMD_THT_CHOICES,default='SMD')
    package     = models.ForeignKey(Package, on_delete=models.SET_NULL,null=True, blank=True,related_name='components')
    category    = models.ForeignKey(Category, on_delete=models.SET_NULL,null=True, blank=True,related_name='components')
    subcategory = models.ForeignKey(Subcategory, on_delete=models.SET_NULL,null=True, blank=True,related_name='components')
    datasheet_url = models.CharField(max_length=1000,blank=True)
    unit_price_ht = models.FloatField(default=0.0)

    def __str__(self):
        return self.mpn


class ComponentCriteria(models.Model):
    component = models.ForeignKey(Component, on_delete=models.CASCADE,
                                   related_name='criterias')
    criteria  = models.ForeignKey(Criteria, on_delete=models.CASCADE,
                                   related_name='components')
    value = models.CharField(max_length=100, blank=True, default='')

    class Meta:
        unique_together = ['component', 'criteria']

    def __str__(self):
        return f"{self.component.mpn} — {self.criteria.criteria} : {self.value}"


class Tiroclass(models.Model):
    tiroclass_name = models.CharField(max_length=100, default='')
    drawer_count   = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.tiroclass_name} ({self.drawer_count} drawers)"


class Drawer(models.Model):
    tiroclass = models.ForeignKey(Tiroclass, on_delete=models.CASCADE,
                                   related_name='drawers')
    number    = models.IntegerField(default=1)
    drawer_name = models.CharField(max_length=100, default='')

    class Meta:
        unique_together = ['tiroclass', 'number']

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.number < 1 or self.number > self.tiroclass.drawer_count:
            raise ValidationError(
                f"Drawer number must be between 1 "
                f"and {self.tiroclass.drawer_count}"
            )

    def __str__(self):
        return f"{self.tiroclass.tiroclass_name} — Drawer {self.number}"


class Position(models.Model):
    ROW_CHOICES = [(r, r) for r in ['A','B','C','D','E','F','G','H']]
    COL_CHOICES = [(c, str(c)) for c in range(1, 13)]

    component = models.ForeignKey(Component, on_delete=models.CASCADE,related_name='positions')
    drawer    = models.ForeignKey(Drawer, on_delete=models.CASCADE,related_name='positions')
    row       = models.CharField(max_length=1, choices=ROW_CHOICES)
    column    = models.IntegerField(choices=COL_CHOICES)

    class Meta:
        unique_together = ['drawer', 'row', 'column']

    def __str__(self):
        return (f"{self.component.mpn} → "
                f"{self.drawer.tiroclass.tiroclass_name} / "
                f"Drawer {self.drawer.number} / "
                f"{self.row}{self.column}")






















# class Component(models.Model):
    
#     TYPE_CHOICES = [
#         ('led',        'LED'),
#         ('resistor',   'Resistor'),
#         ('capacitor',  'Capacitor'),
#         ('inductor',   'Inductor'),
#         ('other',      'Other'),
#     ]
    
#     uid_rfid = models.CharField(max_length=100)
#     mpn = models.CharField(max_length=100)
#     quantity = models.IntegerField(default=0)
#     datasheet_url= models.URLField(max_length=1000, blank=True)
#     component_type = models.CharField(max_length=20,choices=TYPE_CHOICES,default='other')
#     unit_price = models.FloatField(default=0.0)
#     comment = models.CharField(max_length=400)
#     created_at = models.DateTimeField(auto_now_add=True)
#     manufacturer   = models.CharField(max_length=200, blank=True)
#     description    = models.CharField(max_length=500, blank=True)
#     supplier_pn    = models.CharField(max_length=100, blank=True)
   


# class ComponentSpec(models.Model):
#     component = models.OneToOneField(Component, on_delete=models.CASCADE,
#                                      related_name='spec')

#     # LED
#     led_type       = models.CharField(max_length=50,  blank=True, null=True)
#     max_current_ma = models.FloatField(blank=True, null=True)
#     tension_v      = models.FloatField(blank=True, null=True)

#     # Resistor
#     value_ohm      = models.FloatField(blank=True, null=True)

#     # Capacitor
#     capacitor_type      = models.CharField(max_length=50, blank=True, null=True)
#     capacitance_microf  = models.FloatField(blank=True, null=True)

#     # Inductor
#     inductance_mh  = models.FloatField(blank=True, null=True)


   
# class Tiroclass(models.Model):
#     drawer_count = models.IntegerField(default=0)
#     def __str__(self):
#        return f"Tiroclass {self.id} ({self.drawer_count} drawers)"
    
    
    
# class Drawer(models.Model):
#     tiroclass = models.ForeignKey(Tiroclass, on_delete=models.CASCADE,related_name='drawers') #on récupère directement tiroclass.id 
#     number = models.IntegerField(default=1) 
    
#     class Meta:
#        unique_together = ['tiroclass', 'number'] # on définit l'unicité du tirroir 
    
#     def clean(self):
#         from django.core.exceptions import ValidationError
#         if self.number < 1 or self.number > self.tiroclass.drawer_count:
#             raise ValidationError(
#                 f"Drawer number must be between 1 "
#                 f"and {self.tiroclass.drawer_count}"
#             )
#     def __str__(self):
#         return f"Tiroclass {self.tiroclass.id} - Drawer {self.number}"
    
    
      
# class Position(models.Model):
#     component =  models.ForeignKey(Component, on_delete=models.CASCADE,related_name='positions')
#     drawer = models.ForeignKey(Drawer, on_delete=models.CASCADE,related_name='positions')

    
#    # Grille 8 lignes (A→H) x 12 colonnes (1→12)
#     ROW_CHOICES = [(r, r) for r in ['A','B','C','D','E','F','G','H']]
#     COL_CHOICES = [(c, str(c)) for c in range(1, 13)]

#     row    = models.CharField(max_length=1, choices=ROW_CHOICES)
#     column = models.IntegerField(choices=COL_CHOICES)
    
#     class Meta:
#         unique_together = ['drawer', 'row', 'column'] # on définit l'unicité de la position
    
#     def __str__(self):
#         return (f"{self.component.mpn} → "
#                 f"Tiroclass {self.drawer.tiroclass.id} / "
#                 f"Drawer {self.drawer.number} / "
#                 f"{self.row}{self.column}")    
    
    