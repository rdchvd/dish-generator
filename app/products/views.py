from uuid import UUID

from fastapi import Depends
from fastapi_filter import FilterDepends
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlmodel import paginate as sqlmodel_paginate
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from sqlmodel import select

from app.products.filters import ProductFilter
from app.products.models import Product
from app.products.serializers import (
    ListProductResponseSerializer,
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
        products_filter: ProductFilter = FilterDepends(ProductFilter),
        page_params: Params = Depends(),
    ):
        # print()
        # Components = aliased(self.model)
        query = select(self.model)
        # if products_filter.recipe__components__name__in:
        #     query = query.join()

        query = products_filter.sort(query)
        query = products_filter.filter(query)
        return sqlmodel_paginate(session=self.db, query=query, params=page_params)

    @products_router.get(detail_url, response_model=RetrieveProductResponseSerializer)
    def retrieve(self, id_: UUID):
        return self.detail(id_=id_)
