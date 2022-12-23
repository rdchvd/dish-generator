from uuid import UUID

from fastapi import Depends
from fastapi_pagination import Page, Params
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter

from app.products.models import Product
from app.products.serializers import (
    ListProductResponseSerializer,
    ProductRequestSerializer,
    RetrieveProductResponseSerializer,
)
from utils.mixins import BaseModelMixin

products_router = InferringRouter(tags=["products"])


@cbv(products_router)
class ProductsViewSet(BaseModelMixin):
    base_url = "/products/"
    detail_url = "/products/{id_}/"
    serializer_class = None
    response_class = ListProductResponseSerializer
    model = Product
    searching_fields = ["name"]

    @products_router.get(base_url, response_model=Page[response_class])
    def list(
        self,
        params: ProductRequestSerializer = Depends(),
        page_params: Params = Depends(),
    ):
        return self.get(params, page_params)

    @products_router.get(detail_url, response_model=RetrieveProductResponseSerializer)
    def retrieve(self, id_: UUID):
        return self.detail(id_=id_)
