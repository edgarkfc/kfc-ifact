from dataclasses import dataclass, asdict
from typing import Optional
from datetime import datetime

@dataclass
class PivotQR:
    """Modelo PivotQR - Equivalente al modelo de Laravel"""
    id: Optional[int] = None
    nropases: Optional[str] = None
    nrotarjetas: Optional[int] = None
    hora: Optional[int] = None
    minutos: Optional[int] = None
    status: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def to_dict(self):
        """Convierte el modelo a diccionario (como toArray() en Laravel)"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict):
        """Crea modelo desde diccionario (como fill() en Laravel)"""
        return cls(**data)
    
    def __repr__(self):
        return f"<PivotQR(id={self.id}, status={self.status})>"