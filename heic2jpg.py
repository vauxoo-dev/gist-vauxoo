"""Transform all heic (MacOSX image format) files from the current path to JPG

It requires pillow python package installed
    pip install pillow_heif
"""
import os
from glob import glob

from PIL import Image
from pillow_heif import register_heif_opener

register_heif_opener()

images = []
for fname_img in glob("*.HEIC"):
    image = Image.open(fname_img)
    image.convert("RGB")
    extension = os.path.splitext(fname_img)[1]
    new_name = fname_img.replace(extension, ".jpg")
    image.save(new_name)
