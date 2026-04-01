import pytest
import json
from flask import url_for

class TestRoutes:
    """Tests para los endpoints de la API"""
    
    def test_health_check(self, client):
        """Test del endpoint health check"""
        response = client.get('/api/facturas/health')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['message'] == 'Servicio de facturas operativo'
        assert 'version' in data
    
    def test_validar_factura_valida(self, client, factura_valida_data):
        """Test validación de factura válida"""
        response = client.post(
            '/api/facturas/validar',
            json=factura_valida_data,
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['message'] == 'Factura válida'
        assert 'data' in data
        assert data['data']['validacion'] == 'exitosa'
    
    def test_validar_factura_invalida(self, client, factura_invalida_data):
        """Test validación de factura inválida"""
        response = client.post(
            '/api/facturas/validar',
            json=factura_invalida_data,
            content_type='application/json'
        )
        
        assert response.status_code == 422
        data = response.get_json()
        assert data['success'] is False
        assert data['message'] == 'Error de validación en la factura'
        assert 'errors' in data
    
    def test_validar_factura_diferencia_totales(self, client, factura_diferencia_totales_data):
        """Test factura con diferencia en totales"""
        response = client.post(
            '/api/facturas/validar',
            json=factura_diferencia_totales_data,
            content_type='application/json'
        )
        
        assert response.status_code == 422
        data = response.get_json()
        assert data['success'] is False
        assert 'errors' in data
        assert 'cabecera_factura' in data['errors']
    
    def test_validar_factura_sin_json(self, client):
        """Test envío sin JSON"""
        response = client.post(
            '/api/facturas/validar',
            data="texto plano",
            content_type='text/plain'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'JSON' in data['message']
    
    def test_validar_factura_vacia(self, client):
        """Test envío de JSON vacío"""
        response = client.post(
            '/api/facturas/validar',
            json={},
            content_type='application/json'
        )
        
        assert response.status_code == 422
        data = response.get_json()
        assert data['success'] is False
        assert 'errors' in data
    
    def test_procesar_factura_valida(self, client, factura_valida_data, mock_print_message):
        """Test procesamiento de factura válida"""
        response = client.post(
            '/api/facturas/procesar',
            json=factura_valida_data,
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['message'] == 'Factura procesada exitosamente'
        assert 'data' in data
        assert 'factura_unificada' in data['data']
        assert 'metadata' in data['data']
    
    def test_procesar_factura_invalida(self, client, factura_invalida_data):
        """Test procesamiento de factura inválida"""
        response = client.post(
            '/api/facturas/procesar',
            json=factura_invalida_data,
            content_type='application/json'
        )
        
        assert response.status_code == 422
        data = response.get_json()
        assert data['success'] is False
        assert data['message'] == 'Error de validación'
        assert 'errors' in data
    
    def test_armar_factura_valida(self, client, factura_valida_data, mock_print_message):
        """Test armar factura válida (compatibilidad)"""
        response = client.post(
            '/api/facturas/armar',
            json=factura_valida_data,
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['message'] == 'Factura armada exitosamente'
        assert 'data' in data
    
    def test_armar_factura_invalida(self, client, factura_invalida_data):
        """Test armar factura inválida (compatibilidad)"""
        response = client.post(
            '/api/facturas/armar',
            json=factura_invalida_data,
            content_type='application/json'
        )
        
        assert response.status_code == 422
        data = response.get_json()
        assert data['success'] is False
        assert 'error' in data or 'details' in data
    
    @pytest.mark.parametrize("endpoint", [
        '/api/facturas/validar',
        '/api/facturas/procesar',
        '/api/facturas/armar'
    ])
    def test_metodos_no_permitidos(self, client, endpoint):
        """Test métodos HTTP no permitidos"""
        response = client.get(endpoint)
        assert response.status_code == 405
        
        response = client.put(endpoint)
        assert response.status_code == 405
        
        response = client.delete(endpoint)
        assert response.status_code == 405
    
    def test_content_type_incorrecto(self, client):
        """Test content-type incorrecto"""
        response = client.post(
            '/api/facturas/validar',
            headers={'Content-Type': 'application/xml'},
            data='<xml></xml>'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False