# pylint:disable=print-used
import time
import sys
from pypdf import PdfReader, PdfWriter

pdf_files = sys.argv[1:]
writer = PdfWriter()

for pdf in pdf_files:
    reader = PdfReader(pdf)
    for page in reader.pages:
        writer.add_page(page)

output = f'merged_{time.strftime("%Y%m%d_%H%M%S")}.pdf'

with open(output, "wb") as f:
    writer.write(f)
print(f"Generated merged file: {output}")
