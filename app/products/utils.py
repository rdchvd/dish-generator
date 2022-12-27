from typing import Union

from app.products.models import Product
from app.products.serializers import ComponentCreateSerializer, ProductCreateSerializer
from utils.images import download_image_from_link


def create_product_instance_locally(
    product: Union[ComponentCreateSerializer, ProductCreateSerializer]
):
    """Download the image from the link, if it exists, and create a new product instance with the given data
    :param product: ComponentCreateSerializer - this is the serializer that we created earlier
    :type product: ComponentCreateSerializer
    :return: A Product object
    """
    image_path = download_image_from_link(product.image) if product.image else None
    return Product(
        calories=product.calories,
        carbohydrates=product.carbohydrates,
        fats=product.fats,
        is_dish=product.is_dish,
        name=product.name,
        proteins=product.proteins,
        image=image_path,
    )
