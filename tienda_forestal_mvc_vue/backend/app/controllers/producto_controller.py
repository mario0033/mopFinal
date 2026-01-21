"""
Controlador de productos (BluePrint Flask).
Rutas expuestas (prefijo /api si registras el blueprint con url_prefix='/api'):
- GET  /productos                -> listar todos (simple)
- GET  /productos/<id>           -> obtener por id
- GET  /productos/buscar         -> buscar por 'termino' (query param)
- GET  /productos/filtrar        -> filtrado avanzado + paginación
- POST /productos                -> crear producto
- PUT  /productos/<id>           -> actualizar producto
- DELETE /productos/<id>         -> eliminar producto

Respuestas uniformes: en rutas críticas devolvemos JSON con status/message/data.
"""

from flask import Blueprint, request, jsonify
from models import producto_model

producto_blueprint = Blueprint("producto", __name__)

# ---------------------------
# Helpers para respuestas
# ---------------------------
def ok(data=None, message="OK", status=200):
    return jsonify({"status": "success", "message": message, "data": data}), status

def error(message="Error", status=400, details=None):
    payload = {"status": "error", "message": message}
    if details:
        payload["details"] = details
    return jsonify(payload), status

# ---------------------------
# Rutas CRUD básicas
# ---------------------------
@producto_blueprint.route("/productos", methods=["GET"])
def listar_productos():
    """
    Lista todos los productos (sin paginar).
    Útil para debugging o para endpoints simples.
    """
    try:
        productos = producto_model.obtener_productos()
        return ok(productos)
    except Exception as e:
        return error("Error obteniendo productos", 500, str(e))


@producto_blueprint.route("/productos/<int:producto_id>", methods=["GET"])
def obtener_producto(producto_id):
    try:
        p = producto_model.obtener_producto_por_id(producto_id)
        if not p:
            return error("Producto no encontrado", 404)
        return ok(p)
    except Exception as e:
        return error("Error al obtener producto", 500, str(e))


@producto_blueprint.route("/productos", methods=["POST"])
def crear_producto():
    """
    Crea un producto nuevo. Cuerpo JSON requerido.
    """
    datos = request.get_json()
    if not datos:
        return error("JSON body requerido", 400)
    # validación básica de campos obligatorios
    required = ["nombre", "tipo", "marca", "descripcion", "precio", "stock", "imagen"]
    missing = [f for f in required if f not in datos]
    if missing:
        return error(f"Campos faltantes: {', '.join(missing)}", 400)
    try:
        new_id = producto_model.crear_producto(datos)
        return ok({"id": new_id}, "Producto creado", 201)
    except Exception as e:
        return error("Error creando producto", 500, str(e))


@producto_blueprint.route("/productos/<int:producto_id>", methods=["PUT"])
def actualizar_producto(producto_id):
    datos = request.get_json()
    if not datos:
        return error("JSON body requerido", 400)
    try:
        filas = producto_model.actualizar_producto(producto_id, datos)
        if filas == 0:
            return error("Producto no encontrado", 404)
        return ok(message="Producto actualizado")
    except Exception as e:
        return error("Error actualizando producto", 500, str(e))


@producto_blueprint.route("/productos/<int:producto_id>", methods=["DELETE"])
def eliminar_producto(producto_id):
    try:
        filas = producto_model.eliminar_producto(producto_id)
        if filas == 0:
            return error("Producto no encontrado", 404)
        return ok(message="Producto eliminado")
    except Exception as e:
        return error("Error eliminando producto", 500, str(e))


# ---------------------------
# Rutas especializadas (BUSCAR y FILTRAR)
# ---------------------------

@producto_blueprint.route("/productos/buscar", methods=["GET"])
def buscar():
    """
    GET /productos/buscar?termino=...
    Devuelve un array simple con las filas encontradas (no envuelto en data).
    Esto facilita el consumo por el frontend en búsquedas.
    """
    termino = request.args.get("termino", "")
    if not termino:
        return error("Parámetro 'termino' requerido", 400)
    try:
        resultados = producto_model.buscar_productos(termino)
        return jsonify(resultados), 200
    except Exception as e:
        return error("Error en búsqueda", 500, str(e))


@producto_blueprint.route("/productos/filtrar", methods=["GET"])
def filtrar():
    """
    GET /productos/filtrar?tipo=&marca=&precio_min=&precio_max=&ordenar=&pagina=&por_pagina=
    Devuelve objeto con:
      productos, total_resultados, pagina_actual, total_paginas
    """
    # parseo seguro de parámetros numéricos
    def to_int(val, default):
        try:
            return int(val)
        except (TypeError, ValueError):
            return default

    def to_float(val, default):
        try:
            return float(val)
        except (TypeError, ValueError):
            return default

    tipo = request.args.get("tipo")
    marca = request.args.get("marca")
    precio_min = to_float(request.args.get("precio_min"), None)
    precio_max = to_float(request.args.get("precio_max"), None)
    ordenar = request.args.get("ordenar")
    pagina = to_int(request.args.get("pagina"), 1)
    por_pagina = to_int(request.args.get("por_pagina"), 10)

    if ordenar not in (None, "", "asc", "desc"):
        return error("Ordenar solo acepta 'asc' o 'desc'", 400)

    if pagina < 1 or por_pagina < 1:
        return error("'pagina' y 'por_pagina' deben ser >= 1", 400)

    try:
        resultado = producto_model.filtrar_productos(
            tipo=tipo,
            marca=marca,
            precio_min=precio_min,
            precio_max=precio_max,
            ordenar=ordenar,
            pagina=pagina,
            por_pagina=por_pagina
        )
        # Aquí devolvemos la estructura tal y como el frontend espera
        return jsonify(resultado), 200
    except Exception as e:
        return error("Error en filtrado", 500, str(e))

