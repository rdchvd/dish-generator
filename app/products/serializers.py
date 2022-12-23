from typing import List, Optional
from uuid import UUID

from fastapi import Query
from pydantic import validator

from utils.base_serailizer import BaseRequestSerializer, BaseResponseSerializer
from utils.s3 import S3Storage


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

    @validator("image")
    def photo_uri(cls, value):
        return S3Storage().get_url(value) if value else None


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


class ReceiptResponseSerializer(BaseResponseSerializer):
    text: str
    components: Optional[List[Optional[ComponentResponseSerializer]]]


class RetrieveProductResponseSerializer(BaseResponseSerializer):
    id: UUID
    name: str
    is_dish: bool
    receipts: Optional[List[Optional[ReceiptResponseSerializer]]] = None
    calories: Optional[float] = None
    proteins: Optional[float] = None
    fats: Optional[float] = None
    carbohydrates: Optional[float] = None
    image: Optional[str] = None

    @validator("image")
    def photo_uri(cls, value):
        return S3Storage().get_url(value) if value else None
