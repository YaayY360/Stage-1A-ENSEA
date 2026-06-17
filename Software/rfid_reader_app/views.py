from django.shortcuts import render,get_object_or_404
from .models import Category, Subcategory, Criteria, CriteriaSubcategory, Package, Component, ComponentCriteria, Tiroclass,Drawer,Position

def component_list(request):
    components = Component.objects.all().select_related(
        'category', 'subcategory', 'package'
    ).order_by('-id')
    return render(request, 'component_list.html', {
        'components': components
    })

def component_detail(request, component_id):
    component = get_object_or_404(
        Component.objects.select_related(
            'category', 'subcategory', 'package'
        ).prefetch_related('criterias__criteria'),
        id=component_id
    )
    return render(request, 'component_detail.html', {
        'component': component,
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
