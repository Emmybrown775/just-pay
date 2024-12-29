import uuid

from sqlalchemy import Integer, String, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.extensions import db

class Users(db.Model):
    id: Mapped[str] = mapped_column(primary_key=True, default=lambda : str(uuid.uuid4()))
    chat_id: Mapped[int] = mapped_column(unique=True, nullable=False)
    state: Mapped[str] = mapped_column(nullable=True)
    balance: Mapped[float] = mapped_column(nullable=False,default=0)
    account_number: Mapped[str] = mapped_column(nullable=True)
    bank_code: Mapped[str] = mapped_column(nullable=True)
    account_name: Mapped[str] = mapped_column(nullable=True)
    bank_name: Mapped[str] = mapped_column(nullable=True)
    temp_details: Mapped[dict] = mapped_column(JSON, default=dict)


