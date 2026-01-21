// frontend/src/services/api.js
// Servicio centralizado para todas las llamadas a la API del backend Flask.

// Importamos axios (ya está instalado porque lo usas en Productos.vue)
import axios from "axios";

/*
  OPCIÓN A: Dejar que Vite redirija /api al backend (recomendado)
  ---------------------------------------------------------------

  Esto significa que NO ponemos baseURL aquí:
  axios.defaults.baseURL = "/";

  Y las llamadas axios.get("/api/...") funcionarán igual en desarrollo y en Docker.
*/

// Interceptor opcional por si en un futuro añades tokens o logs
axios.interceptors.request.use(
  (config) => {
    // Si algún día añades auth:
    // const token = localStorage.getItem("token");
    // if (token) config.headers.Authorization = `Bearer ${token}`;
    return config;
  },
  (error) => Promise.reject(error)
);

// Interceptor de respuestas (útil para manejar errores globales)
axios.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error("API error:", error);
    return Promise.reject(error);
  }
);

/* -------------------------------------------------------------
 * FUNCIONES ESPECÍFICAS PARA PRODUCTOS
 * ------------------------------------------------------------- */

/**
 * GET /api/productos/filtrar
 * params = { tipo, marca, precio_min, precio_max, ordenar, pagina, por_pagina }
 */
export async function filtrarProductos(params = {}) {
  const query = new URLSearchParams();

  for (const [key, value] of Object.entries(params)) {
    if (value !== null && value !== undefined && value !== "")
      query.append(key, value);
  }

  const res = await axios.get(`/api/productos/filtrar?${query.toString()}`);
  return res.data; // devuelve { productos, total_resultados, pagina_actual, total_paginas }
}

/**
 * GET /api/productos/buscar?termino=...
 */
export async function buscarProductos(termino) {
  const res = await axios.get(
    `/api/productos/buscar?termino=${encodeURIComponent(termino)}`
  );
  return res.data; // array simple
}

/**
 * GET /api/productos
 */
export async function listarTodos() {
  const res = await axios.get(`/api/productos`);
  return res.data;
}

/**
 * POST /api/productos
 */
export async function crearProducto(payload) {
  const res = await axios.post(`/api/productos`, payload);
  return res.data;
}

/**
 * PUT /api/productos/:id
 */
export async function actualizarProducto(id, payload) {
  const res = await axios.put(`/api/productos/${id}`, payload);
  return res.data;
}

/**
 * DELETE /api/productos/:id
 */
export async function eliminarProducto(id) {
  const res = await axios.delete(`/api/productos/${id}`);
  return res.data;
}

/**
 * DELETE /api/productos/ejercicio
 */
export async function eliminarProductosPorFiltros(params = {}) {
  const query = new URLSearchParams();

  for (const [key, value] of Object.entries(params)) {
    if (value !== null && value !== undefined && value !== "") {
      query.append(key, value);
    }
  }

  const res = await axios.delete(`/api/productos/eliminar?${query.toString()}`);
  return res.data; 
}
