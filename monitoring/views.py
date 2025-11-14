from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

# Vistas básicas que ya deberían existir
def index(request):
    return render(request, 'index.html')

def variables(request):
    return render(request, 'variables.html')

def measurements(request):
    return render(request, 'measurements.html')

# Diccionario temporal para simular una base de datos
orders_db = {
    1: {"id": 1, "cliente": "cliente_normal", "estado": "PENDIENTE", "monto": 100.50},
    2: {"id": 2, "cliente": "cliente_regular", "estado": "EN_PROCESO", "monto": 250.75},
    3: {"id": 3, "cliente": "cliente_test", "estado": "REVISION", "monto": 500.00}
}

@csrf_exempt
@require_http_methods(["GET", "POST"])
def orders_list(request):
    if request.method == 'GET':
        # Listar todos los orders
        return JsonResponse({"orders": list(orders_db.values())})
    
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Validar campos requeridos
            required_fields = ['cliente', 'estado', 'monto']
            for field in required_fields:
                if field not in data:
                    return JsonResponse({"error": f"Campo requerido: {field}"}, status=400)
            
            # Crear nuevo order
            new_id = max(orders_db.keys()) + 1 if orders_db else 1
            new_order = {
                "id": new_id,
                "cliente": data['cliente'],
                "estado": data['estado'],
                "monto": float(data['monto'])
            }
            
            # Agregar campos opcionales
            if 'producto' in data:
                new_order['producto'] = data['producto']
            if 'cantidad' in data:
                new_order['cantidad'] = int(data['cantidad'])
            
            orders_db[new_id] = new_order
            
            return JsonResponse(new_order, status=201)
            
        except json.JSONDecodeError:
            return JsonResponse({"error": "JSON inválido"}, status=400)
        except ValueError as e:
            return JsonResponse({"error": f"Error en datos: {str(e)}"}, status=400)
        except Exception as e:
            return JsonResponse({"error": f"Error interno: {str(e)}"}, status=500)

@csrf_exempt
@require_http_methods(["GET", "PUT", "PATCH", "DELETE"])
def order_detail(request, order_id):
    if order_id not in orders_db:
        return JsonResponse({"error": "Order no encontrado"}, status=404)
    
    order = orders_db[order_id]
    
    if request.method == 'GET':
        return JsonResponse(order)
    
    elif request.method in ['PUT', 'PATCH']:
        try:
            data = json.loads(request.body)
            
            # Actualizar campos permitidos
            allowed_fields = ['cliente', 'estado', 'monto', 'producto', 'cantidad']
            for field in allowed_fields:
                if field in data:
                    if field == 'monto':
                        order[field] = float(data[field])
                    elif field == 'cantidad':
                        order[field] = int(data[field])
                    else:
                        order[field] = data[field]
            
            orders_db[order_id] = order
            return JsonResponse(order)
            
        except json.JSONDecodeError:
            return JsonResponse({"error": "JSON inválido"}, status=400)
        except ValueError as e:
            return JsonResponse({"error": f"Error en datos: {str(e)}"}, status=400)
    
    elif request.method == 'DELETE':
        del orders_db[order_id]
        return JsonResponse({"message": "Order eliminado"}, status=204)

@csrf_exempt
@require_http_methods(["PATCH"])
def order_status(request, order_id):
    if order_id not in orders_db:
        return JsonResponse({"error": "Order no encontrado"}, status=404)
    
    try:
        data = json.loads(request.body)
        
        if 'estado' not in data:
            return JsonResponse({"error": "Campo 'estado' requerido"}, status=400)
        
        # Validar estado (simulación de lógica de negocio)
        estados_permitidos = ['PENDIENTE', 'EN_PROCESO', 'REVISION', 'APROBADO', 'RECHAZADO', 'FINALIZADO']
        nuevo_estado = data['estado']
        
        if nuevo_estado not in estados_permitidos:
            return JsonResponse({"error": f"Estado no permitido: {nuevo_estado}"}, status=400)
        
        # Simular validación de autorización
        current_user = request.headers.get('X-User', 'anonimo')
        if nuevo_estado == 'APROBADO' and not current_user.startswith('admin'):
            return JsonResponse({"error": "No autorizado para aprobar orders"}, status=403)
        
        # Actualizar estado
        orders_db[order_id]['estado'] = nuevo_estado
        
        # Log de la operación (para pruebas de tampering)
        print(f"[AUDIT] Order {order_id} actualizado a {nuevo_estado} por {current_user}")
        
        return JsonResponse({
            "message": "Estado actualizado",
            "order_id": order_id,
            "estado_anterior": orders_db[order_id].get('estado_anterior', 'N/A'),
            "estado_actual": nuevo_estado
        })
        
    except json.JSONDecodeError:
        return JsonResponse({"error": "JSON inválido"}, status=400)