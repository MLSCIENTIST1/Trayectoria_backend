# ═══════════════════════════════════════════════════════════════════════════════
# ███████╗██╗   ██╗██╗  ██╗ ██████╗ ███╗   ███╗███████╗██████╗  ██████╗██╗ ██████╗ 
# ╚══██╔══╝██║   ██║██║ ██╔╝██╔═══██╗████╗ ████║██╔════╝██╔══██╗██╔════╝██║██╔═══██╗
#    ██║   ██║   ██║█████╔╝ ██║   ██║██╔████╔██║█████╗  ██████╔╝██║     ██║██║   ██║
#    ██║   ██║   ██║██╔═██╗ ██║   ██║██║╚██╔╝██║██╔══╝  ██╔══██╗██║     ██║██║   ██║
#    ██║   ╚██████╔╝██║  ██╗╚██████╔╝██║ ╚═╝ ██║███████╗██║  ██║╚██████╗██║╚██████╔╝
#    ╚═╝    ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝ ╚═════╝╚═╝ ╚═════╝ 
# ═══════════════════════════════════════════════════════════════════════════════
#
# TUKOMERCIO - Plataforma de Comercio Electrónico, Gamificación y Gestión Empresarial
# Anteriormente conocido como: Trayectoria / BizFlow Studio
#
# ═══════════════════════════════════════════════════════════════════════════════
# AVISO DE PROPIEDAD INTELECTUAL Y DERECHOS DE AUTOR
# ═══════════════════════════════════════════════════════════════════════════════
#
# © 2024-2026 Carlos Eduardo Huérfano Bermúdez. Todos los derechos reservados.
#
# TITULAR DE DERECHOS:
#   Nombre:     Carlos Eduardo Huérfano Bermúdez
#   C.C.:       1.064.986.917 (Cereté, Córdoba, Colombia)
#   Contacto:   carlos-5100@hotmail.com | +57 322 818 8375
#   Ubicación:  Bogotá D.C., Colombia
#
# INFORMACIÓN DEL PROYECTO:
#   Nombre:     TuKomercio
#   Inicio:     Julio 24, 2024
#   Repositorio: github.com/routeres (routeres@gmail.com)
#
# ═══════════════════════════════════════════════════════════════════════════════
# TÉRMINOS DE USO Y RESTRICCIONES
# ═══════════════════════════════════════════════════════════════════════════════
#
# Este código fuente es CONFIDENCIAL y constituye un SECRETO COMERCIAL.
#
# QUEDA ESTRICTAMENTE PROHIBIDO sin autorización ESCRITA del titular:
#
#   1. Copiar, reproducir o duplicar este código, total o parcialmente
#   2. Modificar, adaptar o crear obras derivadas
#   3. Distribuir, publicar, sublicenciar o transferir a terceros
#   4. Usar para desarrollo de productos competidores
#   5. Realizar ingeniería inversa, descompilar o desensamblar
#   6. Remover o alterar este aviso de propiedad intelectual
#
# El acceso a este código NO otorga ninguna licencia implícita o explícita.
#
# ═══════════════════════════════════════════════════════════════════════════════
# PROTECCIÓN LEGAL
# ═══════════════════════════════════════════════════════════════════════════════
#
# Este software está protegido por:
#
#   • Ley 23 de 1982 - Derechos de Autor (Colombia)
#   • Ley 1915 de 2018 - Modernización Derechos de Autor (Colombia)
#   • Decisión Andina 351 de 1993 - Régimen Común sobre Derecho de Autor
#   • Convenio de Berna para la Protección de Obras Literarias y Artísticas
#   • Tratado OMPI sobre Derecho de Autor (WCT)
#   • Acuerdo ADPIC/TRIPS - Organización Mundial del Comercio
#
# SANCIONES POR INFRACCIÓN:
#   • Civiles: Indemnización por daños y perjuicios (Art. 57, Ley 23/1982)
#   • Penales: Prisión de 4 a 8 años y multa (Art. 271, Código Penal Colombiano)
#
# ═══════════════════════════════════════════════════════════════════════════════
# JURISDICCIÓN
# ═══════════════════════════════════════════════════════════════════════════════
#
# Cualquier disputa será resuelta exclusivamente por los tribunales de
# Bogotá D.C., Colombia, bajo las leyes de la República de Colombia.
#
# ═══════════════════════════════════════════════════════════════════════════════
#
# Para solicitar autorización de uso: carlos-5100@hotmail.com
#
# ═══════════════════════════════════════════════════════════════════════════════


"""
BizFlow Studio - API de Carga Masiva v2.0
Importación de productos desde CSV/Excel
Actualizado: Autenticación híbrida (sesión + headers)
"""

import logging
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from flask_login import current_user
from src.models.database import db
from src.models.colombia_data.contabilidad.operaciones_y_catalogo import ProductoCatalogo

carga_masiva_bp = Blueprint('carga_masiva_service', __name__)
logger = logging.getLogger(__name__)


# ==========================================
# FUNCIÓN DE AUTENTICACIÓN HÍBRIDA
# ==========================================
def get_authenticated_user_id():
    """
    Obtiene el ID del usuario autenticado de manera híbrida.
    Soporta tanto Flask-Login (sesión) como headers X-User-ID.
    """
    # Opción 1: Usuario autenticado via Flask-Login
    if current_user and current_user.is_authenticated:
        logger.info(f"✅ Usuario autenticado via sesión: {current_user.id_usuario}")
        return current_user.id_usuario
    
    # Opción 2: Header X-User-ID (para clientes móviles/SPA)
    user_id = request.headers.get('X-User-ID')
    if user_id:
        logger.info(f"✅ Usuario autenticado via X-User-ID: {user_id}")
        try:
            return int(user_id)
        except (ValueError, TypeError):
            logger.error(f"❌ X-User-ID inválido: {user_id}")
            return None
    
    logger.warning("❌ No se encontró autenticación")
    return None


# ==========================================
# ENDPOINT 1: CARGA MASIVA DE PRODUCTOS
# ==========================================
@carga_masiva_bp.route('/control/inventario/carga-masiva', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def carga_masiva_productos():
    """
    Endpoint para carga masiva de productos desde CSV/Excel.
    
    Autenticación: Híbrida (sesión Flask-Login o header X-User-ID)
    
    Request body (JSON):
        {
            "negocio_id": 1,
            "sucursal_id": 1,
            "productos": [
                {
                    "nombre": "Producto 1",
                    "precio": 100,
                    "stock": 10,
                    "sku": "SKU001",
                    "costo": 50,
                    "categoria": "General",
                    "descripcion": "Descripción opcional"
                },
                ...
            ]
        }
    
    Returns:
        201: Productos cargados exitosamente
        400: Datos inválidos
        401: No autenticado
        500: Error interno
    """
    # Manejar preflight CORS
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200
    
    logger.info("🚀 Iniciando carga masiva de productos")
    
    # ==========================================
    # AUTENTICACIÓN
    # ==========================================
    user_id = get_authenticated_user_id()
    if not user_id:
        return jsonify({
            "success": False,
            "message": "Debes iniciar sesión para realizar esta acción"
        }), 401
    
    # ==========================================
    # VALIDACIÓN DE DATOS
    # ==========================================
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False, 
                "message": "No se recibieron datos"
            }), 400
        
        productos = data.get('productos', [])
        negocio_id = data.get('negocio_id')
        sucursal_id = data.get('sucursal_id') or 1

        if not productos:
            return jsonify({
                "success": False, 
                "message": "No se recibieron productos para procesar"
            }), 400

        if not negocio_id:
            return jsonify({
                "success": False,
                "message": "negocio_id es requerido"
            }), 400

        logger.info(f"📦 Procesando {len(productos)} productos para negocio {negocio_id}")

        # ==========================================
        # PROCESAMIENTO DE PRODUCTOS
        # ==========================================
        conteo_exitoso = 0
        conteo_actualizados = 0
        conteo_creados = 0
        errores = []

        for index, p in enumerate(productos):
            try:
                # Mapeo flexible de campos (soporta múltiples formatos)
                nombre_prod = (
                    p.get('nombre') or 
                    p.get('Nombre') or 
                    p.get('NOMBRE') or 
                    p.get('name') or 
                    p.get('producto') or 
                    p.get('PRODUCTO')
                )
                
                precio_val = (
                    p.get('precio') or 
                    p.get('Precio') or 
                    p.get('PRECIO') or 
                    p.get('price') or 
                    0
                )
                
                stock_val = (
                    p.get('stock') or 
                    p.get('Stock') or 
                    p.get('STOCK') or 
                    p.get('cantidad') or 
                    p.get('CANTIDAD') or 
                    p.get('qty') or 
                    0
                )
                
                sku_val = (
                    p.get('sku') or 
                    p.get('SKU') or 
                    p.get('codigo') or 
                    p.get('CODIGO') or 
                    p.get('referencia') or 
                    p.get('referencia_sku') or 
                    ''
                )
                
                costo_val = (
                    p.get('costo') or 
                    p.get('Costo') or 
                    p.get('COSTO') or 
                    p.get('cost') or 
                    0
                )
                
                categoria_val = (
                    p.get('categoria') or 
                    p.get('Categoria') or 
                    p.get('CATEGORIA') or 
                    p.get('category') or 
                    'General'
                )
                
                descripcion_val = (
                    p.get('descripcion') or 
                    p.get('Descripcion') or 
                    p.get('DESCRIPCION') or 
                    p.get('description') or 
                    ''
                )

                # Validación: nombre es obligatorio
                if not nombre_prod or str(nombre_prod).strip() == '':
                    errores.append(f"Fila {index + 1}: El nombre del producto es obligatorio")
                    continue

                # Limpiar y convertir valores
                nombre_prod = str(nombre_prod).strip()
                
                try:
                    precio_val = float(str(precio_val).replace(',', '.').replace('$', '').strip() or 0)
                except:
                    precio_val = 0
                    
                try:
                    stock_val = int(float(str(stock_val).replace(',', '.').strip() or 0))
                except:
                    stock_val = 0
                    
                try:
                    costo_val = float(str(costo_val).replace(',', '.').replace('$', '').strip() or 0)
                except:
                    costo_val = 0

                # ==========================================
                # BUSCAR SI EL PRODUCTO YA EXISTE
                # ==========================================
                producto_existente = None
                
                # Buscar primero por SKU (si tiene)
                if sku_val and str(sku_val).strip():
                    producto_existente = ProductoCatalogo.query.filter_by(
                        referencia_sku=str(sku_val).strip(),
                        negocio_id=int(negocio_id)
                    ).first()
                
                # Si no encontró por SKU, buscar por nombre
                if not producto_existente:
                    producto_existente = ProductoCatalogo.query.filter_by(
                        nombre=nombre_prod,
                        negocio_id=int(negocio_id)
                    ).first()

                if producto_existente:
                    # ==========================================
                    # ACTUALIZAR PRODUCTO EXISTENTE
                    # ==========================================
                    producto_existente.precio = precio_val
                    producto_existente.stock = stock_val
                    producto_existente.costo = costo_val
                    producto_existente.categoria = str(categoria_val).strip()
                    
                    if sku_val:
                        producto_existente.referencia_sku = str(sku_val).strip()
                    if descripcion_val:
                        producto_existente.descripcion = str(descripcion_val).strip()
                    
                    conteo_actualizados += 1
                    logger.debug(f"📝 Actualizado: {nombre_prod}")
                    
                else:
                    # ==========================================
                    # CREAR NUEVO PRODUCTO
                    # ==========================================
                    nuevo_prod = ProductoCatalogo(
                        nombre=nombre_prod,
                        precio=precio_val,
                        negocio_id=int(negocio_id),
                        usuario_id=user_id,
                        referencia_sku=str(sku_val).strip() if sku_val else None,
                        descripcion=str(descripcion_val).strip() if descripcion_val else None,
                        costo=costo_val,
                        stock=stock_val,
                        categoria=str(categoria_val).strip(),
                        sucursal_id=int(sucursal_id),
                        activo=True,
                        estado_publicacion=True
                    )
                    db.session.add(nuevo_prod)
                    conteo_creados += 1
                    logger.debug(f"📦 Creado: {nombre_prod}")
                
                conteo_exitoso += 1

            except ValueError as ve:
                errores.append(f"Fila {index + 1}: Error en formato numérico - {str(ve)}")
                logger.warning(f"⚠️ Fila {index + 1}: {str(ve)}")
                
            except Exception as e:
                errores.append(f"Fila {index + 1}: Error procesando - {str(e)}")
                logger.warning(f"⚠️ Fila {index + 1}: {str(e)}")

        # ==========================================
        # COMMIT A LA BASE DE DATOS
        # ==========================================
        db.session.commit()

        logger.info(f"✅ Carga masiva completada: {conteo_creados} creados, {conteo_actualizados} actualizados")

        return jsonify({
            "success": True,
            "message": f"{conteo_exitoso} productos procesados ({conteo_creados} nuevos, {conteo_actualizados} actualizados)",
            "total_procesados": conteo_exitoso,
            "creados": conteo_creados,
            "actualizados": conteo_actualizados,
            "errores": errores if errores else None,
            "total_errores": len(errores)
        }), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Error crítico en carga masiva: {str(e)}", exc_info=True)
        return jsonify({
            "success": False, 
            "message": "Error interno al procesar el archivo",
            "error": str(e)
        }), 500


# ==========================================
# ENDPOINT 2: OBTENER TEMPLATE/ESTRUCTURA
# ==========================================
@carga_masiva_bp.route('/control/inventario/carga-masiva/template', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def obtener_template():
    """
    Devuelve la estructura esperada para la carga masiva.
    Útil para generar CSV de ejemplo o validar estructura.
    """
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200
        
    return jsonify({
        "success": True,
        "template": {
            "campos_requeridos": ["nombre", "precio"],
            "campos_opcionales": ["stock", "sku", "costo", "categoria", "descripcion"],
            "aliases_soportados": {
                "nombre": ["nombre", "Nombre", "NOMBRE", "name", "producto", "PRODUCTO"],
                "precio": ["precio", "Precio", "PRECIO", "price", "valor"],
                "stock": ["stock", "Stock", "STOCK", "cantidad", "CANTIDAD", "qty"],
                "sku": ["sku", "SKU", "codigo", "CODIGO", "referencia", "referencia_sku"],
                "costo": ["costo", "Costo", "COSTO", "cost"],
                "categoria": ["categoria", "Categoria", "CATEGORIA", "category"],
                "descripcion": ["descripcion", "Descripcion", "DESCRIPCION", "description"]
            },
            "ejemplo": [
                {
                    "nombre": "Aceite Motor 10W40",
                    "precio": 89000,
                    "stock": 15,
                    "sku": "ACE-10W40",
                    "costo": 62000,
                    "categoria": "Lubricantes",
                    "descripcion": "Aceite sintético para motor"
                },
                {
                    "nombre": "Filtro de Aceite Universal",
                    "precio": 28000,
                    "stock": 30,
                    "sku": "FIL-ACE-001",
                    "costo": 18000,
                    "categoria": "Filtros",
                    "descripcion": "Compatible con múltiples marcas"
                }
            ],
            "notas": [
                "Si el SKU ya existe, el producto se actualizará",
                "Si el nombre ya existe (sin SKU), el producto se actualizará",
                "Los precios pueden incluir comas o puntos como separador decimal",
                "El stock debe ser un número entero"
            ]
        }
    }), 200


# ==========================================
# ENDPOINT 3: VALIDAR CSV SIN GUARDAR
# ==========================================
@carga_masiva_bp.route('/control/inventario/carga-masiva/validar', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def validar_carga():
    """
    Valida los datos sin guardarlos en la base de datos.
    Útil para preview antes de confirmar la carga.
    """
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200
    
    try:
        data = request.get_json()
        productos = data.get('productos', [])
        negocio_id = data.get('negocio_id')
        
        if not productos:
            return jsonify({
                "success": False,
                "message": "No hay productos para validar"
            }), 400
        
        if not negocio_id:
            return jsonify({
                "success": False,
                "message": "negocio_id es requerido"
            }), 400
        
        validados = []
        errores = []
        
        for index, p in enumerate(productos):
            fila = index + 1
            producto_validado = {"fila": fila, "valido": True, "errores": []}
            
            # Obtener nombre
            nombre = (
                p.get('nombre') or p.get('Nombre') or p.get('NOMBRE') or 
                p.get('name') or p.get('producto') or p.get('PRODUCTO')
            )
            
            if not nombre or str(nombre).strip() == '':
                producto_validado["valido"] = False
                producto_validado["errores"].append("Nombre es requerido")
            else:
                producto_validado["nombre"] = str(nombre).strip()
            
            # Obtener y validar precio
            precio = p.get('precio') or p.get('Precio') or p.get('PRECIO') or p.get('price') or 0
            try:
                precio_num = float(str(precio).replace(',', '.').replace('$', '').strip() or 0)
                if precio_num < 0:
                    producto_validado["valido"] = False
                    producto_validado["errores"].append("Precio no puede ser negativo")
                producto_validado["precio"] = precio_num
            except:
                producto_validado["valido"] = False
                producto_validado["errores"].append("Precio inválido")
            
            # Obtener y validar stock
            stock = p.get('stock') or p.get('Stock') or p.get('STOCK') or p.get('cantidad') or 0
            try:
                stock_num = int(float(str(stock).replace(',', '.').strip() or 0))
                if stock_num < 0:
                    producto_validado["valido"] = False
                    producto_validado["errores"].append("Stock no puede ser negativo")
                producto_validado["stock"] = stock_num
            except:
                producto_validado["valido"] = False
                producto_validado["errores"].append("Stock inválido")
            
            # Verificar si existe
            if producto_validado.get("nombre"):
                existe = ProductoCatalogo.query.filter_by(
                    nombre=producto_validado["nombre"],
                    negocio_id=int(negocio_id)
                ).first()
                producto_validado["existe"] = existe is not None
                producto_validado["accion"] = "actualizar" if existe else "crear"
            
            validados.append(producto_validado)
            
            if not producto_validado["valido"]:
                errores.extend([f"Fila {fila}: {e}" for e in producto_validado["errores"]])
        
        total_validos = sum(1 for v in validados if v["valido"])
        total_nuevos = sum(1 for v in validados if v.get("accion") == "crear")
        total_actualizar = sum(1 for v in validados if v.get("accion") == "actualizar")
        
        return jsonify({
            "success": True,
            "resumen": {
                "total": len(productos),
                "validos": total_validos,
                "invalidos": len(productos) - total_validos,
                "nuevos": total_nuevos,
                "a_actualizar": total_actualizar
            },
            "productos": validados[:20],  # Solo primeros 20 para preview
            "errores": errores
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error validando carga: {str(e)}")
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


# ==========================================
# HEALTH CHECK
# ==========================================
@carga_masiva_bp.route('/control/inventario/health', methods=['GET'])
def carga_masiva_health():
    """Health check del módulo de carga masiva"""
    return jsonify({
        "status": "online",
        "module": "carga_masiva",
        "version": "2.0.0",
        "endpoints": [
            "POST /api/control/inventario/carga-masiva",
            "GET  /api/control/inventario/carga-masiva/template",
            "POST /api/control/inventario/carga-masiva/validar",
            "GET  /api/control/inventario/health"
        ]
    }), 200