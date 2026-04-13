# tests/test_routes/test_api.py
"""
Pruebas para endpoints de la API
"""
import pytest
import json


class TestAPI:
    """Pruebas para endpoints de API"""
    
    @pytest.fixture
    def factura_con_datos_correctos(self, factura_valida):
        """Fixture con factura de datos correctos"""
        return factura_valida
    
    def test_procesar_factura_exitoso(self, client, factura_con_datos_correctos):
        """Prueba procesamiento exitoso de factura"""
        response = client.post(
            '/api/facturas/procesar',
            data=json.dumps(factura_con_datos_correctos),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['message'] == 'FACTURA procesada exitosamente'
        assert 'data' in data
    
    def test_procesar_factura_sin_json(self, client):
        """Prueba petición sin JSON"""
        response = client.post('/api/facturas/procesar')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
    
    def test_procesar_nota_credito_exitoso(self, client, nota_credito_valida):
        """Prueba procesamiento exitoso de nota de crédito"""
        response = client.post(
            '/api/notas-credito/procesar',
            data=json.dumps(nota_credito_valida),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
    
    def test_procesar_factura_con_qr(self, client, factura_sin_mensajes):
        """Prueba factura con QR habilitado"""
        # Agregar fecha requerida
        factura_sin_mensajes['factura']['cabecera_factura']['cabfact_fechacreacion'] = "2024-01-15 10:30:00"
        
        response = client.post(
            '/api/facturas/procesar',
            data=json.dumps(factura_sin_mensajes),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Verificar que el QR está presente
        factura_unificada = data['data']['factura_unificada']
        tiene_qr = any('y' in str(linea) for linea in factura_unificada)
        assert tiene_qr is True
    
    def test_procesar_factura_con_mensajes(self, client, factura_sin_qr):
        """Prueba factura con mensajes habilitados"""
        # Agregar fecha requerida
        factura_sin_qr['factura']['cabecera_factura']['cabfact_fechacreacion'] = "2024-01-15 10:30:00"
        
        response = client.post(
            '/api/facturas/procesar',
            data=json.dumps(factura_sin_qr),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Verificar que hay mensajes
        factura_unificada = data['data']['factura_unificada']
        tiene_mensajes = any('i0' in str(linea) for linea in factura_unificada)