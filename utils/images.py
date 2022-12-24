import uuid

import requests

from utils.s3 import S3Storage


def download_image_from_link(url):
    """
    It downloads an image from a given URL, saves it to a file, and uploads it to S3

    :param url: The URL of the image you want to download
    :return: The name of the file.
    """
    name = uuid.uuid4()
    fullname = str(name) + ".png"
    try:
        file = requests.get(url, allow_redirects=True)
    except requests.exceptions.ConnectionError:
        return

    with open(fullname, "wb"):
        S3Storage().upload_base64(file_obj=file.content, key=fullname)

    return fullname
