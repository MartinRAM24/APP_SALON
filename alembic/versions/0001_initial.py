"""initial

Revision ID: 0001_initial
Revises: 
Create Date: 2026-03-03
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None


user_role = sa.Enum('cliente', 'admin', name='userrole')
appointment_status = sa.Enum('agendada', 'cancelada', 'completada', name='appointmentstatus')


def upgrade() -> None:
    user_role.create(op.get_bind(), checkfirst=True)
    appointment_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        'usuarios',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('nombre', sa.String(length=120), nullable=False),
        sa.Column('telefono', sa.String(length=20), nullable=False),
        sa.Column('email', sa.String(length=120), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('rol', user_role, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('telefono'),
    )
    op.create_index(op.f('ix_usuarios_email'), 'usuarios', ['email'], unique=False)
    op.create_index(op.f('ix_usuarios_telefono'), 'usuarios', ['telefono'], unique=False)

    op.create_table(
        'servicios',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nombre', sa.String(length=120), nullable=False),
        sa.Column('duracion_minutos', sa.Integer(), nullable=False),
        sa.Column('precio', sa.Numeric(10, 2), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('nombre')
    )
    op.create_index(op.f('ix_servicios_id'), 'servicios', ['id'], unique=False)

    op.create_table(
        'citas',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('usuario_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('servicio_id', sa.Integer(), nullable=False),
        sa.Column('fecha', sa.Date(), nullable=False),
        sa.Column('hora', sa.Time(), nullable=False),
        sa.Column('estado', appointment_status, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['servicio_id'], ['servicios.id'], ),
        sa.ForeignKeyConstraint(['usuario_id'], ['usuarios.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_citas_id'), 'citas', ['id'], unique=False)
    op.create_index('idx_citas_fecha_hora', 'citas', ['fecha', 'hora'], unique=False)


def downgrade() -> None:
    op.drop_index('idx_citas_fecha_hora', table_name='citas')
    op.drop_index(op.f('ix_citas_id'), table_name='citas')
    op.drop_table('citas')
    op.drop_index(op.f('ix_servicios_id'), table_name='servicios')
    op.drop_table('servicios')
    op.drop_index(op.f('ix_usuarios_telefono'), table_name='usuarios')
    op.drop_index(op.f('ix_usuarios_email'), table_name='usuarios')
    op.drop_table('usuarios')
    appointment_status.drop(op.get_bind(), checkfirst=True)
    user_role.drop(op.get_bind(), checkfirst=True)
