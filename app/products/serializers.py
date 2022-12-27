from typing import List, Optional
from uuid import UUID

from fastapi import Query
from pydantic import validator

from app.products.models import Product, Recipe
from app.products.validators import set_photo_uri
from utils.base_serailizer import BaseRequestSerializer, BaseResponseSerializer


class ProductRequestSerializer(BaseRequestSerializer):
    name: Optional[str] = Query(None)
    is_dish: Optional[bool] = Query(None)


class ListProductResponseSerializer(BaseResponseSerializer):
    id: UUID
    name: str
    calories: Optional[float] = None
    proteins: Optional[float] = None
    fats: Optional[float] = None
    carbohydrates: Optional[float] = None
    image: Optional[str] = None

    _set_image_link = validator("image", allow_reuse=True)(set_photo_uri)


class ComponentResponseSerializer(BaseResponseSerializer):
    id: UUID
    name: str
    is_dish: bool
    calories: Optional[float] = None
    proteins: Optional[float] = None
    fats: Optional[float] = None
    carbohydrates: Optional[float] = None
    image: Optional[str] = None

    _set_image_link = validator("image", allow_reuse=True)(set_photo_uri)


class RecipeResponseSerializer(BaseResponseSerializer):
    text: str
    components: Optional[List[Optional[ComponentResponseSerializer]]]


class RetrieveProductResponseSerializer(BaseResponseSerializer):
    id: UUID
    name: str
    is_dish: bool
    recipes: Optional[List[Optional[RecipeResponseSerializer]]] = None
    calories: Optional[float] = None
    proteins: Optional[float] = None
    fats: Optional[float] = None
    carbohydrates: Optional[float] = None
    image: Optional[str] = None

    _set_image_link = validator("image", allow_reuse=True)(set_photo_uri)


class ComponentCreateSerializer(BaseResponseSerializer):
    name: str
    is_dish: bool
    calories: Optional[float] = None
    proteins: Optional[float] = None
    fats: Optional[float] = None
    carbohydrates: Optional[float] = None
    image: Optional[str] = None

    class Meta:
        orm_model = Product


class RecipeCreateSerializer(BaseResponseSerializer):
    text: str
    components: Optional[List[Optional[ComponentCreateSerializer]]]

    class Meta:
        orm_model = Recipe


class ProductCreateSerializer(BaseResponseSerializer):
    name: str
    is_dish: bool
    recipes: Optional[List[Optional[RecipeCreateSerializer]]] = None
    calories: Optional[float] = None
    proteins: Optional[float] = None
    fats: Optional[float] = None
    carbohydrates: Optional[float] = None
    image: Optional[str] = None

    class Meta:
        orm_model = Product
