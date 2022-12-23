from typing import Optional

from fastapi_filter import FilterDepends, with_prefix
from fastapi_filter.contrib.sqlalchemy import Filter

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
    id__in: Optional[list[str]]
    id__not_in: Optional[list[str]]
    name: Optional[str]
    name__in: Optional[list[str]]
    name__not_in: Optional[list[str]]

    recipe__components__name__in: Optional[str]
    recipe__components__name__not_in: Optional[str]

    calories__lte: Optional[float]
    calories__gte: Optional[float]
    proteins__lte: Optional[float]
    proteins__gte: Optional[float]
    fats__lte: Optional[float]
    fats__gte: Optional[float]
    carbohydrates__lte: Optional[float]
    carbohydrates__gte: Optional[float]

    order_by: Optional[list[str]]
    search: Optional[str]

    class Constants(Filter.Constants):
        model = Product
        search_model_fields = ["name"]
