import uuid
from app.extensions import db
from sqlalchemy.dialects.postgresql import UUID, BIGINT, JSON


class Users(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chat_id = db.Column(BIGINT, unique=True, nullable=False)  # Explicitly use BIGINT for large chat IDs
    state = db.Column(db.String, nullable=True)
    balance = db.Column(db.Float, nullable=False, default=0)
    account_number = db.Column(db.String, nullable=True)
    bank_code = db.Column(db.String, nullable=True)
    account_name = db.Column(db.String, nullable=True)
    bank_name = db.Column(db.String, nullable=True)
    temp_details = db.Column(JSON, default=dict)  # Use JSON for storing mutable objects

