"""
Capa de Modelo (Model) del patrón MVC.
Aquí se gestiona el acceso y manipulación de los datos en la base de datos MySQL.
Incluimos funciones de búsqueda, filtrado y paginación.

Modelo de datos para 'productos' - acceso directo a MySQL usando MySQLdb.

Contiene:
- conexión a la BD
- CRUD básico (obtener, crear, actualizar, eliminar)
- búsqueda flexible (LIKE)
- filtrado avanzado con paginación y ordenación

Aclaraciones:
- Este módulo es la única capa que contiene SQL.
- El controlador solo invoca estas funciones.
"""

import os
import math
import MySQLdb

# -----------------------------------------
# Conexión a base de datos MySQL
# -----------------------------------------
def obtener_conexion():
    """
    Crear una conexión a MySQL usando variables de entorno.
    - Host, user, password y DB se configuran desde docker-compose.
    """
    return MySQLdb.connect(
        host=os.getenv('MYSQL_HOST', 'db'),
        user=os.getenv('MYSQL_USER', 'mopii'),
        passwd=os.getenv('MYSQL_PASSWORD', 'daw'),
        db=os.getenv('MYSQL_DB', 'tienda_forestal'),
        charset='utf8mb4'
    )

# -----------------------------------------
# CRUD básico
# -----------------------------------------
def obtener_productos():
    """
    Devuelve todos los productos (sin paginar). Útil para debugging.
    """
    conn = obtener_conexion()
    cur = conn.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM productos ORDER BY id;")
    rows = cur.fetchall()
    conn.close()
    return rows

def obtener_producto_por_id(producto_id):
    """
    Devuelve un producto por su id o None si no existe.
    """
    conn = obtener_conexion()
    cur = conn.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM productos WHERE id=%s;", (producto_id,))
    row = cur.fetchone()
    conn.close()
    return row

def crear_producto(datos):
    """
    Inserta un producto. 'datos' es un dict con los campos:
    nombre, tipo, marca, descripcion, precio, stock, imagen
    """
    conn = obtener_conexion()
    cur = conn.cursor()
    query = """
        INSERT INTO productos (nombre, tipo, marca, descripcion, precio, stock, imagen)
        VALUES (%s, %s, %s, %s, %s, %s, %s);
    """
    cur.execute(query, (
        datos.get('nombre'),
        datos.get('tipo'),
        datos.get('marca'),
        datos.get('descripcion'),
        datos.get('precio'),
        datos.get('stock'),
        datos.get('imagen')
    ))
    conn.commit()
    last_id = cur.lastrowid
    conn.close()
    return last_id

def actualizar_producto(producto_id, datos):
    """
    Actualiza un producto por id. Devuelve el número de filas afectadas.
    """
    conn = obtener_conexion()
    cur = conn.cursor()
    query = """
        UPDATE productos
        SET nombre=%s, tipo=%s, marca=%s, descripcion=%s, precio=%s, stock=%s, imagen=%s
        WHERE id=%s;
    """
    cur.execute(query, (
        datos.get('nombre'),
        datos.get('tipo'),
        datos.get('marca'),
        datos.get('descripcion'),
        datos.get('precio'),
        datos.get('stock'),
        datos.get('imagen'),
        producto_id
    ))
    conn.commit()
    rows = cur.rowcount
    conn.close()
    return rows

def eliminar_producto(producto_id):
    """
    Elimina un producto por id. Devuelve filas afectadas.
    """
    conn = obtener_conexion()
    cur = conn.cursor()
    cur.execute("DELETE FROM productos WHERE id=%s;", (producto_id,))
    conn.commit()
    rows = cur.rowcount
    conn.close()
    return rows

# -----------------------------------------
# Búsqueda (LIKE)
# -----------------------------------------
def buscar_productos(termino):
    """
    Búsqueda simple: busca 'termino' en nombre, tipo o marca usando LIKE.
    Devuelve lista de filas.
    """
    conn = obtener_conexion()
    cur = conn.cursor(MySQLdb.cursors.DictCursor)
    like = f"%{termino}%"
    query = """
        SELECT * FROM productos
        WHERE nombre LIKE %s OR tipo LIKE %s OR marca LIKE %s
        ORDER BY id;
    """
    cur.execute(query, (like, like, like))
    rows = cur.fetchall()
    conn.close()
    return rows

# -----------------------------------------
# Filtrado avanzado + paginación + orden
# -----------------------------------------
def filtrar_productos(tipo=None, marca=None, precio_min=None, precio_max=None,
                      ordenar=None, pagina=1, por_pagina=10):
    """
    Filtra productos por tipo/marca/rango de precio, ordena por precio (asc/desc) y aplica paginación.
    Devuelve un dict con:
    - productos: lista de filas para la página
    - total_resultados: número total de coincidencias (sin paginar)
    - pagina_actual: página devuelta
    - total_paginas: número de páginas totales
    """
    # Conexión y cursor
    conn = obtener_conexion()
    cur = conn.cursor(MySQLdb.cursors.DictCursor)

    # Construir cláusula WHERE dinámica
    where = " WHERE 1=1"
    params = []

    if tipo:
        where += " AND tipo = %s"
        params.append(tipo)
    if marca:
        where += " AND marca = %s"
        params.append(marca)
    if precio_min is not None:
        where += " AND precio >= %s"
        params.append(precio_min)
    if precio_max is not None:
        where += " AND precio <= %s"
        params.append(precio_max)

    # 1) Contar total de resultados (sin LIMIT)
    count_query = "SELECT COUNT(*) AS total FROM productos" + where + ";"
    cur.execute(count_query, params)
    total_resultados = cur.fetchone()['total']

    # Si no hay resultados, devolvemos estructura vacía
    if total_resultados == 0:
        conn.close()
        return {
            "productos": [],
            "total_resultados": 0,
            "pagina_actual": pagina,
            "total_paginas": 0
        }

    # 2) Calcular total_paginas y ajustar 'pagina' si es necesario
    total_paginas = math.ceil(total_resultados / por_pagina)
    if pagina < 1:
        pagina = 1
    if pagina > total_paginas:
        pagina = total_paginas

    offset = (pagina - 1) * por_pagina

    # 3) Construir query final con ORDER BY y LIMIT/OFFSET
    select_query = "SELECT * FROM productos" + where

    if ordenar == "asc":
        select_query += " ORDER BY precio ASC"
    elif ordenar == "desc":
        select_query += " ORDER BY precio DESC"
    else:
        # orden por id por defecto para estabilidad
        select_query += " ORDER BY id ASC"

    select_query += " LIMIT %s OFFSET %s"
    params_with_limit = params + [por_pagina, offset]

    cur.execute(select_query, params_with_limit)
    productos = cur.fetchall()

    conn.close()

    return {
        "productos": productos,
        "total_resultados": total_resultados,
        "pagina_actual": pagina,
        "total_paginas": total_paginas
    }

