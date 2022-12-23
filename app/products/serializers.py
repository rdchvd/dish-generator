from typing import List, Optional
from uuid import UUID

from fastapi import Query
from pydantic import validator
from pydantic.dataclasses import dataclass

from utils.base_serailizer import BaseRequestSerializer, BaseResponseSerializer
from utils.s3 import S3Storage


@dataclass
class ProductRequestSerializer(BaseRequestSerializer):
    name: Optional[str] = Query(None)
    is_dish: Optional[bool] = Query(None)


@dataclass
class ListProductResponseSerializer(BaseResponseSerializer):
    id: UUID
    name: str
    calories: Optional[float] = None
    proteins: Optional[float] = None
    fats: Optional[float] = None
    carbohydrates: Optional[float] = None
    image: Optional[str] = None

    @validator("image")
    def photo_uri(cls, value):
        return S3Storage().get_url(value) if value else None


@dataclass
class ComponentResponseSerializer(BaseResponseSerializer):
    id: UUID
    name: str
    is_dish: bool
    calories: Optional[float] = None
    proteins: Optional[float] = None
    fats: Optional[float] = None
    carbohydrates: Optional[float] = None
    image: Optional[str] = None

    @validator("image")
    def photo_uri(cls, value):
        return S3Storage().get_url(value) if value else None


@dataclass
class RetrieveProductResponseSerializer(BaseResponseSerializer):
    id: UUID
    name: str
    is_dish: bool
    receipt: Optional[str] = None
    calories: Optional[float] = None
    proteins: Optional[float] = None
    fats: Optional[float] = None
    carbohydrates: Optional[float] = None
    image: Optional[str] = None
    components: Optional[List[Optional[ComponentResponseSerializer]]]

    @validator("image")
    def photo_uri(cls, value):
        return S3Storage().get_url(value) if value else None
