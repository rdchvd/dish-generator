from typing import List, Optional, Text
from uuid import UUID

from sqlalchemy import Column, ForeignKey, Unicode
from sqlalchemy.orm import RelationshipProperty
from sqlmodel import Field, Relationship

from utils.base_model import ModelBase


class ReceiptComponentsLink(ModelBase, table=True):
    """Connects assessments and units."""

    __tablename__ = "receipt_components_link"

    # foreign keys
    component_id: UUID = Field(foreign_key="product.id", primary_key=True)
    receipt_id: UUID = Field(foreign_key="receipt.id", primary_key=True)


class Receipt(ModelBase, table=True):
    __tablename__ = "receipt"
    text: str = Field(Column(Text()))
    components: List["Product"] = Relationship(
        back_populates="dish_receipts", link_model=ReceiptComponentsLink
    )
    dish_id: Optional[UUID] = Field(
        sa_column=Column(ForeignKey("product.id", ondelete="SET NULL"), nullable=True)
    )

    dish: Optional["Product"] = Relationship(
        back_populates="receipts",
        sa_relationship=RelationshipProperty(
            "Product",
            primaryjoin="foreign(Receipt.dish_id) == Product.id",
            uselist=False,
        ),
    )


class Product(ModelBase, table=True):
    __tablename__ = "product"

    name: str = Field(
        Column(Text(), Unicode(2, collation="utf8_uk_UA")),
    )
    image: str = Field(default="", max_length=255)
    calories: Optional[float]
    proteins: Optional[float]
    fats: Optional[float]
    carbohydrates: Optional[float]
    is_dish: bool = Field(default=False)

    dish_receipts: List["Receipt"] = Relationship(
        back_populates="components", link_model=ReceiptComponentsLink
    )

    receipts: Optional[List["Receipt"]] = Relationship(
        back_populates="dish",
        sa_relationship=RelationshipProperty(
            "Receipt",
            primaryjoin="foreign(Receipt.dish_id) == Product.id",
            uselist=True,
        ),
    )
