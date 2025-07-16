from fpdf import FPDF
import barcode
from barcode.writer import ImageWriter
import os

def generate_pdf(book_name, codes, output_path="book_output.pdf"):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", size=10)

    row_height = 30
    col_width = 60
    margin_x = 15
    margin_y = 15
    max_cols = 3

    for i, row in enumerate(codes):
        if i % (max_cols * 9) == 0 and i != 0:
            pdf.add_page()

        row_index = (i % (max_cols * 9)) // max_cols
        col_index = i % max_cols
        x = margin_x + col_index * col_width
        y = margin_y + row_index * row_height

        code_str = str(row["Code"])
        desc = row.get("Description", "")

        pdf.set_xy(x, y)
        pdf.multi_cell(col_width, 5, f"{code_str}\n{desc}", border=1, align="C")

    pdf.output(output_path)
    return output_path
