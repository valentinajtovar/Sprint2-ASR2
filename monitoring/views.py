# views.py
from django.http import JsonResponse
from time import sleep

def get_orders(request):
    sleep(0.1)  # simulación de procesamiento
    return JsonResponse({"result": "orders retrieved"})

def update_order(request):
    sleep(0.2)  # simulación de operación de escritura
    return JsonResponse({"result": "order updated"})
