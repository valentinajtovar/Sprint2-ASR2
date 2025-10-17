# views.py
from django.http import JsonResponse
from time import sleep

# monitoring/views.py
from django.http import JsonResponse, HttpResponse
from time import sleep

def health_check(request):
    return HttpResponse("OK", status=200)

def get_orders(request):
    # Simula consulta ligera
    sleep(0.1)
    return JsonResponse({"result": "orders retrieved"})

def update_order(request):
    # Simula actualización
    sleep(0.2)
    return JsonResponse({"result": "order updated"})
