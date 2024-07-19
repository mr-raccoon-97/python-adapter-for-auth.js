from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, BigInteger
from sqlalchemy import Table, ForeignKey, MetaData, PrimaryKeyConstraint

metadata = MetaData()

users = Table(
    'users',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String(50)),
    Column('email', String(50)),
    Column('email_verified_at', DateTime(timezone=True)),
    Column('image_url', String(255)),
)

accounts = Table(
    'accounts',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('account_id', String(255), nullable=False),
    Column('account_type', String(255), nullable=False),
    Column('account_provider', String(255), nullable=False),
    Column('refresh_token', Text),
    Column('access_token', Text),
    Column('expires_at', BigInteger),
    Column('id_token', Text),
    Column('scope', Text),
    Column('session_state', Text),
    Column('token_type', Text),
    Column('user_id', Integer, ForeignKey('users.id')),
)

verification_token = Table(
    'verification_token',
    metadata,
    Column('identifier', Text, nullable=False),
    Column('expires', DateTime(timezone=True), nullable=False),
    Column('token', Text, nullable=False),
    PrimaryKeyConstraint('identifier', 'token')
)