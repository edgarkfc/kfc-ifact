#  server/migrations/versions/001_create_print_messages_table.py
"""Create print_messages table

Revision ID: 001
Revises: 
Create Date: 2024-01-15 10:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Tabla print_messages
    op.create_table('print_messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=10), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('order', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    
    # Tabla pivot_qrs
    op.create_table('pivot_qrs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('num_pases', sa.Integer(), nullable=True),
        sa.Column('num_tarjetas', sa.Integer(), nullable=True),
        sa.Column('horas', sa.Integer(), nullable=True),
        sa.Column('minutos', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('pivot_qrs')
    op.drop_table('print_messages')