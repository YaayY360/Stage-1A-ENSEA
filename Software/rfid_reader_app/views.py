from django.shortcuts import render,get_object_or_404
from .models import Component
from .APIs.mouser_api import get_component_info 


def component_list(request):
    components = Component.objects.all()
    return render(request, 'component_list.html', {'components': components})

def component_detail(request, component_id):
    component = get_object_or_404(Component, id=component_id)
    mouser_data = None

    if component.mpn:
        mouser_data = get_component_info(component.mpn)

        # Option : mettre à jour automatiquement les champs depuis Mouser
        if mouser_data and not component.unit_price:
            component.unit_price = mouser_data.get("price_ht") or 0.0
            component.datasheet_url = mouser_data.get("datasheet") or ""
            component.save()

    return render(request, 'component_detail.html', {
        'component': component,
        'mouser_data': mouser_data,
    })