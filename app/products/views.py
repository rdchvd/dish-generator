from uuid import UUID

from fastapi import Depends
from fastapi_filter import FilterDepends
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlmodel import paginate as sqlmodel_paginate
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from sqlalchemy import func
from sqlmodel import select

from app.products.filters import ProductFilter
from app.products.models import Product, Recipe, RecipeComponentsLink
from app.products.serializers import (
    ListProductResponseSerializer,
    ProductCreateSerializer,
    RetrieveProductResponseSerializer,
)
from app.products.utils import create_product_instance_locally
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
        """Return a paginated list of products, filtered and sorted by the given ProductFilter
        :param products_filter: ProductFilter = FilterDepends(ProductFilter)
        :type products_filter: ProductFilter
        :param page_params: Params = Depends()
        :type page_params: Params
        :return: A list of products
        """
        query = select(self.model)

        query = products_filter.sort(query)
        query = products_filter.filter(query)
        return sqlmodel_paginate(session=self.db, query=query, params=page_params)

    @products_router.get(detail_url, response_model=RetrieveProductResponseSerializer)
    def retrieve(self, id_: UUID):
        """Retrieve a single product from the database
        :param id_: The id of the object to retrieve
        :type id_: UUID
        :return: The detail method is being returned.
        """
        return self.detail(id_=id_)

    @products_router.post(
        base_url, response_model=RetrieveProductResponseSerializer, status_code=201
    )
    def save(self, data: ProductCreateSerializer):
        """Create a product, create recipes, create components, and link them all together
        :param data: ProductCreateSerializer - this is the data that we get from the user
        :type data: ProductCreateSerializer
        :return: Product instance
        """

        data_on_create = []
        session = self.db

        product = create_product_instance_locally(data)
        session.add(product)
        session.flush()

        for recipe in data.recipes:
            recipe_instance = Recipe(text=recipe.text, dish_id=product.id)
            session.add(recipe_instance)
            session.flush()
            # create recipe

            for component in recipe.components:
                name = component.name.lower()
                # find product with given name
                existent_component = (
                    Product.objects.values(Product.id)
                    .filter(func.lower(Product.name).__eq__(name))
                    .first()
                )
                if not existent_component:
                    # create new component
                    component_instance = create_product_instance_locally(component)
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
        # commit transaction
        session.add_all(data_on_create)
        session.flush()
        session.commit()

        return product
