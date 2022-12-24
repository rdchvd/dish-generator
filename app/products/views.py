from uuid import UUID

from fastapi import Depends
from fastapi_filter import FilterDepends
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlmodel import paginate as sqlmodel_paginate
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from sqlmodel import select

from app.products.filters import ProductFilter
from app.products.models import Product, Recipe, RecipeComponentsLink
from app.products.serializers import (
    ListProductResponseSerializer,
    ProductCreateSerializer,
    RetrieveProductResponseSerializer,
)
from utils.images import download_image_from_link
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
        query = select(self.model)

        query = products_filter.sort(query)
        query = products_filter.filter(query)
        return sqlmodel_paginate(session=self.db, query=query, params=page_params)

    @products_router.get(detail_url, response_model=RetrieveProductResponseSerializer)
    def retrieve(self, id_: UUID):
        return self.detail(id_=id_)

    @products_router.post(
        base_url, response_model=RetrieveProductResponseSerializer, status_code=201
    )
    def save(self, data: ProductCreateSerializer):

        data_on_create = []
        session = self.db
        image_path = download_image_from_link(data.image) if data.image else None
        product = Product(
            calories=data.calories,
            carbohydrates=data.carbohydrates,
            fats=data.fats,
            is_dish=data.is_dish,
            name=data.name,
            proteins=data.proteins,
            image=image_path,
        )

        session.add(product)
        session.flush()

        for recipe in data.recipes:
            recipe_instance = Recipe(text=recipe.text, dish_id=product.id)
            session.add(recipe_instance)
            session.flush()

            for component in recipe.components:
                existent_component = Product.objects.get_or_none(name=component.name)
                if not existent_component:
                    # if not component.image:
                    #     downloader.download(f"animated {component.name}", limit=1, output_dir='dataset')

                    image_path = (
                        download_image_from_link(component.image)
                        if component.image
                        else None
                    )
                    component_instance = Product(
                        calories=component.calories,
                        carbohydrates=component.carbohydrates,
                        fats=component.fats,
                        is_dish=component.is_dish,
                        name=component.name,
                        proteins=component.proteins,
                        image=image_path,
                    )

                    session.add(component_instance)
                    session.flush()
                    component_id = component_instance.id
                else:
                    component_id = existent_component.id

                data_on_create.append(
                    RecipeComponentsLink(
                        component_id=component_id, recipe_id=recipe_instance.id
                    )
                )
        session.add_all(data_on_create)
        session.flush()
        session.commit()

        return product
