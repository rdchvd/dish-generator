from typing import Any, Optional

from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import validator

from app.products.models import Product
from app.products.validators import validate_float


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

    _validate_calories__lte = validator("calories__lte", allow_reuse=True)(
        validate_float
    )
    _validate_calories__gte = validator("calories__gte", allow_reuse=True)(
        validate_float
    )
    _validate_proteins__lte = validator("proteins__lte", allow_reuse=True)(
        validate_float
    )
    _validate_proteins__gte = validator("proteins__gte", allow_reuse=True)(
        validate_float
    )
    _validate_fats__lte = validator("fats__lte", allow_reuse=True)(validate_float)
    _validate_fats__gte = validator("fats__lte", allow_reuse=True)(validate_float)
    _validate_carbohydrates__lte = validator("carbohydrates__lte", allow_reuse=True)(
        validate_float
    )
    _validate_carbohydrates__gte = validator("carbohydrates__gte", allow_reuse=True)(
        validate_float
    )
