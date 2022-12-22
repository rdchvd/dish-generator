from typing import List, Optional, Text
from uuid import UUID

from sqlalchemy import Column
from sqlmodel import Field, Relationship

from utils.base_model import ModelBase


class DishComponentsLink(ModelBase, table=True):
    """Connects assessments and units."""

    __tablename__ = "dish_components_link"

    # foreign keys
    dish_id: UUID = Field(foreign_key="product.id", primary_key=True)
    component_id: UUID = Field(foreign_key="product.id", primary_key=True)


class Product(ModelBase, table=True):
    __tablename__ = "product"

    name: str = Field(Column(Text()))
    receipt: str = Field(Column(Text()))
    image: str = Field(default="", max_length=255)
    calories: Optional[float]
    proteins: Optional[float]
    fats: Optional[float]
    carbohydrates: Optional[float]
    is_dish: bool = Field(default=False)
    number: Optional[int] = Field(default=None)
    weight: Optional[int] = Field(default=None)

    components: List["Product"] = Relationship(
        back_populates="dishes", link_model=DishComponentsLink
    )
    dishes: List["Product"] = Relationship(
        back_populates="components", link_model=DishComponentsLink
    )
