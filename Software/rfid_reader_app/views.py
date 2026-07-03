import csv
from django.shortcuts import render,get_object_or_404, redirect
from django.http import HttpResponse
from .models import Category, Subcategory, Criteria, CriteriaSubcategory, Package, Component, ComponentCriteria, Tiroclass,Drawer,Position
from .APIs.mouser_api import get_component_info
from .forms import ComponentForm
from django.contrib.auth.decorators import login_required, permission_required

@login_required
def component_list(request):
    components = Component.objects.all().select_related(
        'category', 'subcategory', 'package'
    ).order_by('-id')
    categories = Category.objects.all()
    subcategories = Subcategory.objects.all()
    
    # On vérifie si l'utilisateur appartient au groupe "Responsables Stock"
    est_responsable = request.user.groups.filter(name='stock_manager').exists()
    est_lecteur = request.user.groups.filter(name='reader').exists()
    
    return render(request, 'component_list.html', {
        'components': components,
        'categories': categories,         
        'subcategories': subcategories,  
        'est_responsable_stock': est_responsable,
        'est_reader': est_lecteur,
    })


@permission_required('rfid_reader_app.change_component_quantity', raise_exception=True)
def update_quantity(request, component_id, action):
    component = get_object_or_404(Component, id=component_id)
    
    if action == 'increase':
        component.quantity += 1
    elif action == 'decrease' and component.quantity > 0:
        component.quantity -= 1
    elif action == 'set':
        # On récupère le paramètre ?value=XX envoyé par le JavaScript
        new_val = request.GET.get('value', 0)
        try:
            component.quantity = max(0, int(new_val)) # Sécurité anti-négatif
        except ValueError:
            pass # Si ce n'est pas un nombre valide, on ne fait rien
        
    component.save()
    return redirect('component_list')



@login_required
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

@login_required
def export_components_csv(request):
    # 1. Préparer la réponse HTTP avec le bon type de contenu (MIME type)
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="components_export.csv"'

    # 2. Créer le writer CSV (on utilise le point-virgule souvent préféré par Excel en français)
    writer = csv.writer(response, delimiter=';')
    
    # 3. Écrire la ligne d'en-tête (les colonnes)
    writer.writerow(['MPN', 'SPN', 'Quantity', 'SMD/THT', 'Category', 'Subcategory', 'Datasheet URL'])

    # 4. Parcourir la base de données et écrire les lignes
    # On utilise select_related pour éviter de surcharger la base de données (Requêtes optimisées)
    components = Component.objects.select_related('category', 'subcategory').all()
    
    for comp in components:
        writer.writerow([
            comp.mpn,
            comp.spn or '—',
            comp.quantity,
            comp.smd_or_tht,
            comp.category.name if comp.category else '—',
            comp.subcategory.name if comp.subcategory else '—',
            comp.datasheet_url or '—'
        ])

    return response

from django.shortcuts import render
from .models import Category

def homepage(request):
    # Si l'utilisateur est DÉJÀ connecté, on le redirige direct vers les composants
    if request.user.is_authenticated:
        return redirect('component_list')
    
    # Sinon, on lui montre la page de garde avec le bouton
    return render(request, 'homepage.html')

@permission_required('rfid_reader_app.can_add_component', raise_exception=True)
def add_component_view(request):
    if request.method == 'POST':
        form = ComponentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('component_list')  # Remplace par le nom de ta page de liste/stock
    else:
        form = ComponentForm()
        
    return render(request, 'add_component.html', {'form': form})

