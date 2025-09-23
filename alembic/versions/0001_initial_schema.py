"""Initial database schema

Revision ID: 0001_initial_schema
Revises: 
Create Date: 2026-08-20 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '0001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('username', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('profile_picture_url', sa.String(length=1024), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    op.create_index('ix_users_username', 'users', ['username'], unique=True)
    op.create_index('ix_users_id', 'users', ['id'], unique=False)

    op.create_table(
        'songs',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('song_url', sa.String(length=1024), nullable=False),
        sa.Column('lyrics', sa.JSON(), nullable=False),
        sa.Column('description', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('owner_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_songs_id', 'songs', ['id'], unique=False)
    op.create_index('ix_songs_title', 'songs', ['title'], unique=False)

    op.create_table(
        'splits',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('song_id', sa.Integer(), nullable=False),
        sa.Column('bass_audio_url', sa.String(length=1024), nullable=True),
        sa.Column('vocals_audio_url', sa.String(length=1024), nullable=True),
        sa.Column('piano_audio_url', sa.String(length=1024), nullable=True),
        sa.Column('other_audio_url', sa.String(length=1024), nullable=True),
        sa.Column('drum_audio_url', sa.String(length=1024), nullable=True),
        sa.Column('bass_description', sa.JSON(), nullable=True),
        sa.Column('vocals_description', sa.JSON(), nullable=True),
        sa.Column('piano_description', sa.JSON(), nullable=True),
        sa.Column('drum_description', sa.JSON(), nullable=True),
        sa.Column('other_description', sa.JSON(), nullable=True),
        sa.Column('guitar_description', sa.JSON(), nullable=True),
        sa.Column('flute_description', sa.JSON(), nullable=True),
        sa.Column('violin_description', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['song_id'], ['songs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_splits_id', 'splits', ['id'], unique=False)
    op.create_index('ix_splits_song_id', 'splits', ['song_id'], unique=False)

    op.create_table(
        'password_reset_otps',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('otp', sa.String(length=10), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('is_used', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_password_reset_otps_email', 'password_reset_otps', ['email'], unique=False)
    op.create_index('ix_password_reset_otps_id', 'password_reset_otps', ['id'], unique=False)

def downgrade() -> None:
    op.drop_table('password_reset_otps')
    op.drop_table('splits')
    op.drop_table('songs')
    op.drop_table('users')
