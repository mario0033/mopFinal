"""
Archivo de configuración de la aplicación Flask.
Define los parámetros de conexión a la base de datos.
"""

import os

class Config:
    MYSQL_HOST = os.getenv('DB_HOST', 'db')
    MYSQL_USER = os.getenv('DB_USER', 'mopii')
    MYSQL_PASSWORD = os.getenv('DB_PASSWORD', 'daw')
    MYSQL_DB = os.getenv('DB_NAME', 'tienda_forestal')
    MYSQL_CHARSET = 'utf8mb4'
    MYSQL_CURSOCLASS = 'DictCursor'
    #MYSQL_PORT = 3306

