@control_api_bp.route('/control/operacion/guardar', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def guardar_operacion():
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200

    user_id = request.headers.get('X-User-ID') or (current_user.id_usuario if current_user.is_authenticated else None)
    
    if not user_id:
        return jsonify({"success": False, "message": "Usuario no identificado"}), 401

    try:
        data = request.get_json()
        negocio_id = int(data.get('negocio_id'))
        tipo_op = data.get('tipo', 'VENTA') 

        # 1. Registrar la Transacción en el historial (TransaccionOperativa)
        nueva_t = TransaccionOperativa(
            negocio_id=negocio_id,
            usuario_id=int(user_id),
            sucursal_id=int(data.get('sucursal_id', 1)),
            tipo=tipo_op,
            concepto=data.get('concepto', 'Operación POS'),
            monto=float(data.get('monto', 0)),
            categoria=data.get('categoria', 'General'),
            metodo_pago=data.get('metodo_pago', 'Efectivo'),
            referencia_guia=data.get('referencia_guia', '')
        )
        db.session.add(nueva_t)

        # 2. Lógica de Actualización en ProductoCatalogo
        if tipo_op in ['VENTA', 'COMPRA', 'GASTO'] and 'items' in data:
            for item in data['items']:
                # Buscamos el producto en la tabla productos_catalogo
                prod = ProductoCatalogo.query.filter_by(
                    id_producto=int(item['id']), 
                    negocio_id=negocio_id
                ).first()
                
                if prod:
                    # 'qty' para ventas, 'cantidad' para compras
                    cant_operacion = int(item.get('qty') or item.get('cantidad') or 0)
                    
                    if tipo_op == 'VENTA':
                        prod.stock -= cant_operacion
                        
                    elif tipo_op == 'COMPRA' or (tipo_op == 'GASTO' and cant_operacion > 0):
                        costo_nuevo_unidad = float(item.get('costo', 0))
                        
                        # --- CÁLCULO DE COSTO PROMEDIO PONDERADO (PMP) ---
                        # Si hay stock previo y el costo nuevo es válido, promediamos
                        if prod.stock > 0 and costo_nuevo_unidad > 0:
                            valor_inventario_actual = prod.stock * (prod.costo or 0)
                            valor_compra_nueva = cant_operacion * costo_nuevo_unidad
                            nuevo_stock_total = prod.stock + cant_operacion
                            
                            # Actualizamos la columna 'costo' del modelo con el promedio
                            prod.costo = (valor_inventario_actual + valor_compra_nueva) / nuevo_stock_total
                        
                        # Si no había stock o el costo actual era 0, asignamos el nuevo costo directamente
                        elif costo_nuevo_unidad > 0:
                            prod.costo = costo_nuevo_unidad
                        
                        # Actualizamos el stock físico en la tabla
                        prod.stock += cant_operacion

                    # Alerta de stock crítico
                    if prod.stock <= 5:
                        nueva_alerta = AlertaOperativa(
                            negocio_id=negocio_id,
                            usuario_id=int(user_id),
                            tarea=f"Stock crítico: {prod.nombre} ({prod.stock} uds.)",
                            fecha_programada=datetime.utcnow(),
                            prioridad="ALTA"
                        )
                        db.session.add(nueva_alerta)

        # Guardamos todos los cambios en Neon DB
        db.session.commit()
        return jsonify({"success": True, "message": "Producto y Costo actualizados en catálogo"}), 201

    except Exception as e:
        db.session.rollback()
        print(f"❌ ERROR: {traceback.format_exc()}")
        return jsonify({"success": False, "message": str(e)}), 500