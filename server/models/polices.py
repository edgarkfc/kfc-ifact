from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime


@dataclass
class Politica:
    """Modelo para políticas activas - Tabla polices"""
    id: int
    name: str
    description: Optional[str]
    status: bool
    
    @classmethod
    def from_db_row(cls, row):
        if not row:
            return None
        return cls(
            id=row[0],
            name=row[1],
            description=row[2],
            status=bool(row[3])
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'status': self.status
        }


@dataclass
class PivotQR:
    """Modelo para configuración QR - Tabla pivotqrs"""
    id: int
    nropases: int
    nrotarjetas: int
    hora: int
    minutos: int
    status: bool
    
    @classmethod
    def from_db_row(cls, row):
        if not row:
            return None
        return cls(
            id=row[0],
            nropases=row[1],
            nrotarjetas=row[2],
            hora=row[3],
            minutos=row[4],
            status=bool(row[5])
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'nropases': self.nropases,
            'nrotarjetas': self.nrotarjetas,
            'hora': self.hora,
            'minutos': self.minutos,
            'status': self.status
        }
    
    def generar_contenido_qr(self, datos_factura: Dict) -> str:
        """Genera el contenido del QR basado en la configuración"""
        factura_id = datos_factura.get('cabecera', {}).get('cabfact_id', '')
        total = datos_factura.get('cabecera', {}).get('cabfact_total', 0)
        
        contenido = (
            f"PASES:{self.nropases}|"
            f"TARJETAS:{self.nrotarjetas}|"
            f"TIEMPO:{self.hora}:{self.minutos}|"
            f"FACTURA:{factura_id}|"
            f"TOTAL:{total}"
        )
        return contenido


@dataclass
class PrintMessage:
    """Modelo para mensajes de impresión - Tabla print_messages"""
    id: int
    code: str
    content: str
    order: int
    is_active: bool
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    
    @classmethod
    def from_db_row(cls, row):
        if not row:
            return None
        return cls(
            id=row[0],
            code=row[1],
            content=row[2],
            order=row[3],
            is_active=bool(row[4]),
            created_at=row[5],
            updated_at=row[6]
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'code': self.code,
            'content': self.content,
            'order': self.order,
            'is_active': self.is_active
        }


@dataclass
class TicketLine:
    """Modelo para líneas de ticket/cupón - Tabla ticket_lines"""
    id: int
    ticket_type: str
    line_content: str
    line_order: int
    is_active: bool
    date_active: Optional[datetime]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    
    @classmethod
    def from_db_row(cls, row):
        if not row:
            return None
        return cls(
            id=row[0],
            ticket_type=row[1],
            line_content=row[2],
            line_order=row[3],
            is_active=bool(row[4]),
            date_active=row[5],
            created_at=row[6],
            updated_at=row[7]
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'ticket_type': self.ticket_type,
            'line_content': self.line_content,
            'line_order': self.line_order,
            'is_active': self.is_active,
            'date_active': self.date_active.isoformat() if self.date_active else None
        }