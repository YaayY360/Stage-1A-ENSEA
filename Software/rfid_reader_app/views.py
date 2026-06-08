from django.shortcuts import render
from .models import Component

def component_list(request):
    components = Component.objects.all()
    return render(request, 'component_list.html', {'components': components})