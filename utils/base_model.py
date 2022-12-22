import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime
from sqlmodel import Field, SQLModel

from utils.model_manager import ModelManager


class ModelBase(SQLModel):
    """
    Base class for database models.
    """

    @classmethod
    @property
    def objects(cls) -> ModelManager:
        return ModelManager(model=cls)

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4, primary_key=True, index=True, nullable=False
    )
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), default=datetime.utcnow)
    )
    updated_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True), onupdate=datetime.utcnow, default=datetime.utcnow
        )
    )
