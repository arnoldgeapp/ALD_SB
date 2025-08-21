from fpdf import FPDF
import os
import tempfile

# Try to import barcode libraries with fallback
try:
    import barcode
    from barcode.writer import ImageWriter
    BARCODE_AVAILABLE = True
except ImportError:
    BARCODE_AVAILABLE = False

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

def generate_pdf(book_name, codes, output_path="book_output.pdf"):
    """Generate a PDF with barcodes for each code"""
    # Check if barcode libraries are available
    if not BARCODE_AVAILABLE:
        print("Warning: Barcode library not available. Generating PDF without barcodes.")
        return generate_simple_pdf_fallback(book_name, codes, output_path)
    
    pdf = FPDF()
    # Use slightly smaller margins and title so we can reliably fit 10 rows per page
    pdf.set_margins(10, 8, 10)
    pdf.set_auto_page_break(auto=True, margin=10)
    pdf.add_page()

    # Set up layout parameters
    max_cols = 3
    max_rows_per_page = 10

    # Add title (smaller than before to save vertical space)
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_xy(pdf.l_margin, 8)
    pdf.cell(0, 8, f"Book: {book_name}", ln=True, align="C")

    # Compute dynamic layout values based on page dimensions and current y position
    def compute_layout():
        # Use printable width between left/right margins
        total_width = pdf.w - pdf.l_margin - pdf.r_margin
        col_width_local = total_width / max_cols

        # y_start just below the title
        y_start_local = pdf.get_y() + 1

        # Available height between y_start and bottom margin
        usable_height = pdf.h - pdf.b_margin - y_start_local - 2
        # Divide usable height into exactly max_rows_per_page rows
        row_height_local = usable_height / max_rows_per_page

        return col_width_local, row_height_local, y_start_local

    col_width, row_height, grid_y_start = compute_layout()
    
    temp_files = []  # Keep track of temporary files to clean up
    
    try:
        for i, row in enumerate(codes):
            # Add new page when needed
            if i % (max_cols * max_rows_per_page) == 0 and i != 0:
                pdf.add_page()
                # Re-add title on new pages with page number
                pdf.set_font("Helvetica", "B", 16)
                pdf.set_xy(pdf.l_margin, 8)
                pdf.cell(0, 8, f"Book: {book_name} - Page {pdf.page_no()}", ln=True, align="C")
                # Recompute layout for the new page
                col_width, row_height, grid_y_start = compute_layout()
            
            # Calculate position
            page_item_index = i % (max_cols * max_rows_per_page)
            row_index = page_item_index // max_cols
            col_index = page_item_index % max_cols
            
            # x anchored at left printable margin, y anchored at computed grid start
            x = pdf.l_margin + col_index * col_width
            y = grid_y_start + row_index * row_height
            
            # Get code and description
            code_str = str(row["Code"]).strip()
            # Remove .0 from whole numbers but preserve leading zeros
            if code_str.endswith('.0') and code_str.replace('.0', '').replace('0', '').replace('.', ''):
                without_decimal = code_str[:-2]
                if without_decimal.isdigit() or (without_decimal.startswith('0') and len(without_decimal) > 1):
                    code_str = without_decimal
            
            desc = str(row.get("Description", "")).strip()
            if desc == "nan":
                desc = ""
            
            try:
                # Generate barcode image
                temp_dir = tempfile.mkdtemp()
                barcode_path = os.path.join(temp_dir, f"barcode_{i}")
                
                writer_options = {
                    'module_width': 0.2,    # bar width
                    'module_height': 2.0,   # bar height
                    'font_size': 60,        # printed code font size (ignored when write_text=False)
                    # Disable writer-rendered human-readable text; we'll render one controlled label below
                    'write_text': False,
                    'text_distance': .5,
                    'quiet_zone': 1.0,      # side margins
                    'background': 'white',
                    'foreground': 'black',
                    'dpi': 300,
                }

                code128 = barcode.get('code128', code_str, writer=ImageWriter())
                # Pass writer options to save so generated image has desired appearance
                barcode_filename = code128.save(barcode_path, options=writer_options)
                temp_files.append(barcode_filename)
                temp_files.append(temp_dir)
                
                # Add barcode image at top; compute actual image height used so we can place a single
                # controlled human-readable label below the barcode (writer won't render text).
                barcode_y = y + 2  # Reduced padding from top
                image_height_used = 0
                try:
                    # Resize barcode to fit in the cell
                    if PIL_AVAILABLE:
                        with Image.open(barcode_filename) as img:
                            # Calculate size to fit within our constraints
                            max_width = col_width - 4
                            # Make image height relative to available row height so 10 rows fit correctly
                            # Reserve smaller space for the code label and description to fit 10 rows
                            reserved_for_text = 10  # label + small gap
                            max_height = max(10, row_height - reserved_for_text - 4)

                            # Calculate scaling factor
                            scale_x = max_width / img.width
                            scale_y = max_height / img.height
                            scale = min(scale_x, scale_y, 1.0)  # Don't scale up

                            new_width = img.width * scale
                            new_height = img.height * scale

                            # Center the barcode
                            barcode_x = x + (col_width - new_width) / 2

                            pdf.image(barcode_filename, barcode_x, barcode_y, new_width, new_height)
                            image_height_used = new_height
                    else:
                        # Use default size if PIL not available
                        default_height = 28
                        pdf.image(barcode_filename, x + 5, barcode_y, col_width - 10, default_height)
                        image_height_used = default_height
                except Exception as img_error:
                    # If image fails, add text representation and reserve a small height
                    pdf.set_font("Courier", "", 8)
                    pdf.set_xy(x, barcode_y)
                    pdf.cell(col_width, 6, "||||| " + code_str + " |||||", align="C")
                    image_height_used = 8

                # Add code text below barcode (single controlled label)
                code_text_y = barcode_y + image_height_used + 2
                pdf.set_font("Helvetica", "B", 9)
                pdf.set_xy(x, code_text_y)
                pdf.cell(col_width, 5, code_str, align="C")

                # Add description below code text with tighter spacing
                if desc:
                    pdf.set_font("Helvetica", "", 7)
                    desc_y = code_text_y + 4
                    pdf.set_xy(x, desc_y)
                    if len(desc) > 35:
                        line1 = desc[:35]
                        line2 = desc[35:70] + ("..." if len(desc) > 70 else "")
                        pdf.cell(col_width, 3, line1, align="C")
                        pdf.set_xy(x, desc_y + 3)
                        pdf.cell(col_width, 3, line2, align="C")
                    else:
                        pdf.cell(col_width, 4, desc, align="C")

                # Add border around the cell
                pdf.rect(x, y, col_width, row_height - 0.5)
                
            except Exception as barcode_error:
                # Fallback: just add text if barcode generation fails
                pdf.set_font("Helvetica", "B", 9)
                pdf.set_xy(x, y + 12)  # Center the text vertically
                pdf.cell(col_width, 6, code_str, align="C")
                
                if desc:
                    pdf.set_font("Helvetica", "", 7)
                    pdf.set_xy(x, y + 20)
                    if len(desc) > 35:
                        line1 = desc[:35]
                        line2 = desc[35:70] + ("..." if len(desc) > 70 else "")
                        pdf.cell(col_width, 3, line1, align="C")
                        pdf.set_xy(x, y + 23)
                        pdf.cell(col_width, 3, line2, align="C")
                    else:
                        pdf.cell(col_width, 4, desc, align="C")
                
                # Add border
                pdf.rect(x, y, col_width, row_height - 1)
    
    finally:
        # Clean up temporary files
        for temp_file in temp_files:
            try:
                if os.path.isfile(temp_file):
                    os.remove(temp_file)
                elif os.path.isdir(temp_file):
                    os.rmdir(temp_file)
            except:
                pass  # Ignore cleanup errors
    
    # Save the PDF
    pdf.output(output_path)
    return output_path


def generate_simple_pdf_fallback(book_name, codes, output_path="book_output.pdf"):
    """Fallback PDF generator without barcodes if barcode library fails"""
    pdf = FPDF()
    pdf.set_margins(10, 8, 10)
    pdf.set_auto_page_break(auto=True, margin=10)
    pdf.add_page()

    max_cols = 3
    max_rows_per_page = 10

    # Add title first, then compute layout
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_xy(pdf.l_margin, 8)
    pdf.cell(0, 8, f"Book: {book_name}", ln=True, align="C")

    # Compute layout
    total_width = pdf.w - pdf.l_margin - pdf.r_margin
    col_width = total_width / max_cols
    y_start = pdf.get_y() + 1
    usable_height = pdf.h - pdf.b_margin - y_start - 2
    row_height = usable_height / max_rows_per_page

    for i, row in enumerate(codes):
        if i % (max_cols * max_rows_per_page) == 0 and i != 0:
            pdf.add_page()
            # Re-add title on new pages with page number
            pdf.set_font("Helvetica", "B", 14)
            pdf.set_xy(pdf.l_margin, 8)
            pdf.cell(0, 8, f"Book: {book_name} - Page {pdf.page_no()}", ln=True, align="C")
            # Recompute grid start for new page
            y_start = pdf.get_y() + 1

        page_item_index = i % (max_cols * max_rows_per_page)
        row_index = page_item_index // max_cols
        col_index = page_item_index % max_cols

        x = pdf.l_margin + col_index * col_width
        y = y_start + row_index * row_height

        code_str = str(row["Code"]).strip()
        if code_str.endswith('.0') and code_str.replace('.0', '').replace('0', '').replace('.', ''):
            without_decimal = code_str[:-2]
            if without_decimal.isdigit() or (without_decimal.startswith('0') and len(without_decimal) > 1):
                code_str = without_decimal
                
        desc = str(row.get("Description", "")).strip()
        if desc == "nan":
            desc = ""

        # Create text representation of barcode with tighter spacing
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_xy(x, y + 1)
        pdf.cell(col_width, 6, code_str, align="C")

        # Add simple barcode-like pattern
        pdf.set_font("Courier", "", 10)
        pdf.set_xy(x, y + 8)
        barcode_text = "||||| " + code_str + " |||||"
        pdf.cell(col_width, 6, barcode_text, align="C")

        if desc:
            pdf.set_font("Helvetica", "", 7)
            pdf.set_xy(x, y + 16)
            if len(desc) > 25:
                desc = desc[:22] + "..."
            pdf.cell(col_width, 4, desc, align="C")

        pdf.rect(x, y, col_width, row_height - 1)

    pdf.output(output_path)
    return output_path