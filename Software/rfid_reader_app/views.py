from django.shortcuts import render,get_object_or_404
from .models import Category, Subcategory, Criteria, CriteriaSubcategory, Package, Component, ComponentCriteria, Tiroclass,Drawer,Position
from .APIs.mouser_api import get_component_info

def component_list(request):
    components = Component.objects.all().select_related(
        'category', 'subcategory', 'package'
    ).order_by('-id')
    return render(request, 'component_list.html', {
        'components': components
    })

def component_detail(request, component_id):
    # 1. Récupérer le composant
    component = get_object_or_404(
        Component.objects.select_related(
            'category', 'subcategory', 'package'
        ).prefetch_related('criterias__criteria'),
        id=component_id
    )
    
    # 2. Récupérer les données Mouser si nécessaire
    mouser_data = None 
    if component.spn:
        mouser_data = get_component_info(component.spn)
        if mouser_data:
            component.unit_price_ht = mouser_data.get("unit_price_ht") or 0.0
            component.datasheet_url = mouser_data.get("datasheet") or ""
            component.save()

    # 3. Réutiliser ta logique "drawer_view" intégrée pour ce composant
    # On cherche la première position enregistrée pour ce composant
    position_du_composant = Position.objects.filter(component=component).select_related('drawer__tiroclass').first()
    
    # Initialisation des variables de la grille à vide (au cas où le composant n'est rangé nulle part)
    grid = {}
    rows = ['A','B','C','D','E','F','G','H']
    cols = [str(i) for i in range(1, 13)]
    
    if position_du_composant:
        # On extrait le tiroir où se trouve le composant actuel
        drawer = position_du_composant.drawer
        
        # On récupère TOUTES les positions de ce même tiroir pour afficher la grille complète
        all_positions_in_drawer = Position.objects.filter(drawer=drawer).select_related('component')
        
        # On remplit ton dictionnaire (exactement ton code)
        for pos in all_positions_in_drawer:
            grid[(pos.row, pos.column)] = pos.component
            
        print("GRID CONTENT GENERATED:", grid)

    # 4. On envoie TOUT au template unifié
    return render(request, 'component_detail.html', {
        'component': component,
        'mouser_data': mouser_data,
        'position_du_composant' : position_du_composant,
        'rows': rows,
        'cols': cols,
        'grid': grid,  # Si grid est vide, le HTML affichera proprement le message d'absence d'emplacement
    })




# def component_list(request):
#     components = Component.objects.all()
#     return render(request, 'component_list.html', {'components': components})



# def component_detail(request, component_id):
#     component = get_object_or_404(Component, id=component_id)
#     mouser_data = None

#     if component.mpn:
#         mouser_data = get_component_info(component.mpn)

#         # Option : mettre à jour automatiquement les champs depuis Mouser
#         if mouser_data and not component.unit_price:
#             component.unit_price = mouser_data.get("price_ht") or 0.0
#             component.datasheet_url = mouser_data.get("datasheet") or ""
#             component.save()

#     return render(request, 'component_detail.html', {
#         'component': component,
#         'mouser_data': mouser_data,
#     })



# def drawer_view(request, tiroclass_id, drawer_number):
#     tiroclass = get_object_or_404(Tiroclass, id=tiroclass_id)
#     drawer   = get_object_or_404(Drawer, tiroclass=tiroclass, number=drawer_number)

#     # Construire la matrice 8x12 vide
#     rows = ['A','B','C','D','E','F','G','H']
#     cols = [str(i) for i in range(1, 13)]
    
#     positions = Position.objects.filter(drawer=drawer).select_related('component')
    
#     # Créer un dictionnaire {(row, col): component}
#     grid = {}
#     for pos in positions:
#         grid[(pos.row, pos.column)] = pos.component
        
#     print("GRID CONTENT:", grid)
    
#     return render(request, 'drawer.html', {
#         'tiroclass': tiroclass,
#         'drawer':   drawer,
#         'rows':     rows,
#         'cols':     cols,
#         'grid':     grid,
#     })
