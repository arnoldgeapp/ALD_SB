import barcode
from barcode.writer import ImageWriter
import os

def generate_code128_image(value, output_path):
    code128 = barcode.get('code128', value, writer=ImageWriter())
    filename = code128.save(output_path)
    return filename
