**Diagrama MVC completo (Modelo-Vista-Controlador)**

                           ┌──────────────────────────────┐
                           │            Usuario            │
                           │ (Navega, busca, pagina, etc.)│
                           └───────────────┬──────────────┘
                                           │
                                           ▼
                        ┌──────────────────────────────┐
                        │             Vista             │
                        │         (Vue.js SPA)          │
                        │  - Renderiza componentes      │
                        │  - Envía solicitudes API      │
                        │  - Muestra resultados/páginas │
                        └───────────────┬──────────────┘
                                        │ Axios (REST)
                                        ▼
                        ┌──────────────────────────────┐
                        │          Controlador          │
                        │          (Flask API)          │
                        │  - Recibe peticiones GET      │
                        │  - Procesa filtros/búsqueda   │
                        │  - Aplica paginación          │
                        │  - Valida datos               │
                        │  - Devuelve JSON estructurado │
                        └───────────────┬──────────────┘
                                        │
                                        ▼
                        ┌──────────────────────────────┐
                        │            Modelo             │
                        │          (SQLAlchemy)         │
                        │  - Define tablas              │
                        │  - Ejecuta queries            │
                        │  - Devuelve objetos/filas     │
                        └───────────────┬──────────────┘
                                        │
                                        ▼
                        ┌──────────────────────────────┐
                        │           MySQL DB            │
                        │ - Almacena datos persistentes │
                        │ - Consultas + filtros         │
                        └──────────────────────────────┘

**Diagrama de flujo de paginación (Backend + Frontend)

                   ┌────────────────────────┐
                   │ Usuario cambia página  │
                   │  (botón, número, etc.)│
                   └─────────────┬──────────┘
                                 │
                                 ▼
                   ┌────────────────────────┐
                   │ Frontend Vue.js        │
                   │ Calcula page, filtros  │
                   │ Construye URL API      │
                   └─────────────┬──────────┘
                                 │ Request API
                                 ▼
                   ┌────────────────────────┐
                   │ Flask Controller        │
                   │ - Lee parámetros        │
                   │   page, limit, q, etc. │
                   │ - Valida datos          │
                   └─────────────┬──────────┘
                                 │
                                 ▼
                   ┌────────────────────────┐
                   │ SQLAlchemy Model        │
                   │ - Ejecuta query         │
                   │ - Aplica filtros        │
                   │ - Aplica ORDER BY       │
                   │ - LIMIT + OFFSET        │
                   └─────────────┬──────────┘
                                 │
                                 ▼
                   ┌────────────────────────┐
                   │   MySQL Database        │
                   │     Devuelve filas      │
                   └─────────────┬──────────┘
                                 │
                                 ▼
                   ┌────────────────────────┐
                   │ Flask formatea respuesta│
                   │ products[], page_info{} │
                   └─────────────┬──────────┘
                                 │ JSON
                                 ▼
                   ┌────────────────────────┐
                   │ Frontend Vue.js         │
                   │ - Muestra resultados    │
                   │ - Actualiza paginación  │
                   │ - Gestiona loaders/UX   │
                   └─────────────────────────┘

**Arquitectura Docker**

                                   ┌────────────────────────┐
                                   │        Usuario         │
                                   └───────────┬────────────┘
                                               │
              ┌────────────────────────────────┼──────────────────────────────┐
              ▼                                ▼                              ▼
   ┌─────────────────────┐          ┌─────────────────────┐        ┌──────────────────────┐
   │  Frontend (Vue.js)  │◀────────▶│   Backend (Flask)   │◀──────▶│   MySQL Database     │
   │ Port: 8080          │  REST API│ Port: 5000           │        │ Port: 3306          │
   │ Container: vue_front│          │ Container: flask_back│        │ Container: mysql_db  │
   └─────────────────────┘          └─────────────────────┘        └───────────┬──────────┘
                                                                               │
                                                                               ▼
                                                                  ┌──────────────────────┐
                                                                  │     phpMyAdmin       │
                                                                  │  Port: 8081          │
                                                                  │  Container: phpadmin │
                                                                  │  Acceso DB: db:3306  │
                                                                  └──────────────────────┘

