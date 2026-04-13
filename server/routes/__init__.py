# server/routes/__init__.py
from flask import Blueprint
import logging

logger = logging.getLogger(__name__)

api_bp = Blueprint('api', __name__, url_prefix='/api')


def register_routes(app):
    """Registra todas las rutas en la app"""
    
    # Rutas originales (compatibilidad)
    from server.routes.api import facturas_bp, notas_credito_bp
    
    app.register_blueprint(facturas_bp)
    app.register_blueprint(notas_credito_bp)
    
    # Health check general
    @app.route('/health', methods=['GET'])
    def health_check():
        return {
            'success': True,
            'message': 'API operativa',
            'database': 'connected'
        }, 200
    
    @app.route('/health/db', methods=['GET'])
    def health_check_db():
        """Verifica conexión a base de datos"""
        try:
            from server.config.database import db
            result = db.execute_query("SELECT GETDATE() as now", fetch=True)
            return {
                'success': True,
                'message': 'Database connected',
                'server_time': str(result[0]['now']) if result else None
            }, 200
        except Exception as e:
            return {
                'success': False,
                'message': f'Database error: {str(e)}'
            }, 500
    
    logger.info("✅ Rutas registradas exitosamente")