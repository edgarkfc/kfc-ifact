
"""
Modelo de PivotQR para parámetros de generación QR
"""
from server.models.base import BaseModel, db


class PivotQR(BaseModel):
    """Modelo para parámetros de generación de QR"""
    __tablename__ = 'pivot_qrs'
    
    num_pases = db.Column(db.Integer, default=4)
    num_tarjetas = db.Column(db.Integer, default=300)
    horas = db.Column(db.Integer, default=1)
    minutos = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default='ACTIVO')
    is_active = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f"<PivotQR pases={self.num_pases}, tarjetas={self.num_tarjetas}>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'nropases': self.num_pases,
            'nrotarjetas': self.num_tarjetas,
            'hora': self.horas,
            'minutos': self.minutos,
            'status': self.status,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }