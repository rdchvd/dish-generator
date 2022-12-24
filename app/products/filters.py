from typing import Any, Optional

from fastapi_filter import FilterDepends, with_prefix
from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import validator

from app.products.models import Product, Recipe


class ComponentFilter(Filter):
    name__in: Optional[list[str]]

    class Constants(Filter.Constants):
        model = Product


class RecipeFilter(Filter):
    components: Optional[ComponentFilter] = FilterDepends(
        with_prefix("components", ComponentFilter)
    )

    class Constants(Filter.Constants):
        model = Recipe


class ProductFilter(Filter):
    id__in: Optional[list[str]] = None
    id__not_in: Optional[list[str]] = None
    name: Optional[str] = None
    name__in: Optional[list[str]] = None
    name__not_in: Optional[list[str]] = None
    calories__lte: Any
    calories__gte: Any
    proteins__lte: Any
    proteins__gte: Any
    fats__lte: Any
    fats__gte: Any
    carbohydrates__lte: Any
    carbohydrates__gte: Any

    order_by: Optional[list[str]] = None
    search: Optional[str] = None

    class Constants(Filter.Constants):
        model = Product
        search_model_fields = ["name"]

    @validator("calories__lte")
    def validate_calories__lte(cls, value):
        return float(value) if value else None

    @validator("calories__gte")
    def validate_calories__gte(cls, value):
        return float(value) if value else None

    @validator("proteins__lte")
    def validate_proteins__lte(cls, value):
        return float(value) if value else None

    @validator("proteins__gte")
    def validate_proteins__gte(cls, value):
        return float(value) if value else None

    @validator("fats__lte")
    def validate_fats__lte(cls, value):
        return float(value) if value else None

    @validator("fats__gte")
    def validate_fats__gte(cls, value):
        return float(value) if value else None

    @validator("carbohydrates__lte")
    def validate_carbohydrates__lte(cls, value):
        return float(value) if value else None

    @validator("carbohydrates__gte")
    def validate_carbohydrates__gte(cls, value):
        return float(value) if value else None
