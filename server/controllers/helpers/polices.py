# server/controllers/helpers/polices.py
def validar_impresion_qr(impresion_qr):
    """
    Valida si la impresión QR está habilitada
    """
    try:
        print(f"Tipo recibido: {type(impresion_qr)}")
        print(f"Valor recibido: {impresion_qr}")
        
        # Si es None, retornar False
        if impresion_qr is None:
            return False
        
        # Si es booleano, retornar directamente
        if isinstance(impresion_qr, bool):
            return impresion_qr
        
        # Si es string, convertir
        if isinstance(impresion_qr, str):
            return impresion_qr.lower() in ['true', '1', 'yes', 'si', 'sí']
        
        # Si es número, convertir a booleano
        if isinstance(impresion_qr, (int, float)):
            return bool(impresion_qr)
        
        # Para cualquier otro tipo, intentar convertir a booleano
        return bool(impresion_qr)
        
    except Exception as e:
        print(f"Error en validar_impresion_qr: {e}")
        import traceback
        traceback.print_exc()
        return False

def validar_mensaje_qr(impresion_msgqr):
    """
    Valida si el mensaje QR está habilitado
    """
    try:
        print(f"Tipo recibido: {type(impresion_msgqr)}")
        print(f"Valor recibido: {impresion_msgqr}")
        
        # Si es None, retornar False
        if impresion_msgqr is None:
            return False
        
        # Si es booleano, retornar directamente
        if isinstance(impresion_msgqr, bool):
            return impresion_msgqr
        
        # Si es string, convertir
        if isinstance(impresion_msgqr, str):
            return impresion_msgqr.lower() in ['true', '1', 'yes', 'si', 'sí']
        
        # Si es número, convertir a booleano
        if isinstance(impresion_msgqr, (int, float)):
            return bool(impresion_msgqr)
        
        # Para cualquier otro tipo, intentar convertir a booleano
        return bool(impresion_msgqr)
        
    except Exception as e:
        print(f"Error en validar_impresion_msgqr: {e}")
        import traceback
        traceback.print_exc()
        return False