"""Transform all jpg files from the current path to PDF
ordered by name

It requires pillow python package installed
    pip install pillow
"""

import sys
from glob import glob

from PIL import Image

images = []
paths = sys.argv[1:] or glob("*.jpg")
for fname_img in sorted(paths):
    image = Image.open(fname_img)
    image.convert("RGB")
    images.append(image)

images[0].save("my_images.pdf", save_all=True, append_images=images[1:])
