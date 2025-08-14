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
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Set up layout parameters
    row_height = 42  # Reduced from 45 to fit more content
    col_width = 62
    margin_x = 10  # Reduced from 12
    margin_y = 18  # Reduced from 20
    max_cols = 3
    max_rows_per_page = 6
    
    # Add title
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_xy(10, 10)
    pdf.cell(0, 10, f"Book: {book_name}", ln=True, align="C")
    
    temp_files = []  # Keep track of temporary files to clean up
    
    try:
        for i, row in enumerate(codes):
            # Add new page when needed
            if i % (max_cols * max_rows_per_page) == 0 and i != 0:
                pdf.add_page()
                # Re-add title on new pages
                pdf.set_font("Helvetica", "B", 16)
                pdf.set_xy(10, 10)
                pdf.cell(0, 10, f"Book: {book_name} (continued)", ln=True, align="C")
            
            # Calculate position
            page_item_index = i % (max_cols * max_rows_per_page)
            row_index = page_item_index // max_cols
            col_index = page_item_index % max_cols
            
            x = margin_x + col_index * col_width
            y = margin_y + row_index * row_height
            
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
                
                # Create Code 128 barcode
                code128 = barcode.get('code128', code_str, writer=ImageWriter())
                barcode_filename = code128.save(barcode_path)
                temp_files.append(barcode_filename)
                temp_files.append(temp_dir)
                
                # Add barcode image at top
                barcode_y = y + 2  # Reduced padding from top
                try:
                    # Resize barcode to fit in the cell
                    if PIL_AVAILABLE:
                        with Image.open(barcode_filename) as img:
                            # Calculate size to fit within our constraints
                            max_width = col_width - 4
                            max_height = 20
                            
                            # Calculate scaling factor
                            scale_x = max_width / img.width
                            scale_y = max_height / img.height
                            scale = min(scale_x, scale_y, 1.0)  # Don't scale up
                            
                            new_width = img.width * scale
                            new_height = img.height * scale
                            
                            # Center the barcode
                            barcode_x = x + (col_width - new_width) / 2
                            
                            pdf.image(barcode_filename, barcode_x, barcode_y, new_width, new_height)
                    else:
                        # Use default size if PIL not available
                        pdf.image(barcode_filename, x + 5, barcode_y, col_width - 10, 18)
                except Exception as img_error:
                    # If image fails, add text representation
                    pdf.set_font("Courier", "", 8)
                    pdf.set_xy(x, barcode_y)
                    pdf.cell(col_width, 6, "||||| " + code_str + " |||||", align="C")
                
                # Add code text below barcode (single display only)
                code_text_y = barcode_y + 18  # Reduced spacing
                pdf.set_font("Helvetica", "B", 9)  # Slightly smaller font
                pdf.set_xy(x, code_text_y)
                pdf.cell(col_width, 5, code_str, align="C")
                
                # Add description below code text with more space
                if desc:
                    pdf.set_font("Helvetica", "", 7)  # Smaller font for description
                    desc_y = code_text_y + 6  # Reduced spacing
                    pdf.set_xy(x, desc_y)
                    # Allow longer descriptions by using smaller font and more space
                    if len(desc) > 35:
                        # Split long descriptions into two lines
                        line1 = desc[:35]
                        line2 = desc[35:70] + ("..." if len(desc) > 70 else "")
                        pdf.cell(col_width, 3, line1, align="C")
                        pdf.set_xy(x, desc_y + 3)
                        pdf.cell(col_width, 3, line2, align="C")
                    else:
                        pdf.cell(col_width, 4, desc, align="C")
                
                # Add border around the cell
                pdf.rect(x, y, col_width, row_height - 1)  # Slightly thinner border
                
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
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    row_height = 30
    col_width = 60
    margin_x = 15
    margin_y = 25
    max_cols = 3
    
    # Add title
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_xy(10, 10)
    pdf.cell(0, 10, f"Book: {book_name}", ln=True, align="C")
    
    for i, row in enumerate(codes):
        if i % (max_cols * 9) == 0 and i != 0:
            pdf.add_page()
            # Re-add title
            pdf.set_font("Helvetica", "B", 16)
            pdf.set_xy(10, 10)
            pdf.cell(0, 10, f"Book: {book_name} (continued)", ln=True, align="C")

        page_item_index = i % (max_cols * 9)
        row_index = page_item_index // max_cols
        col_index = page_item_index % max_cols
        
        x = margin_x + col_index * col_width
        y = margin_y + row_index * row_height

        code_str = str(row["Code"]).strip()
        if code_str.endswith('.0') and code_str.replace('.0', '').replace('0', '').replace('.', ''):
            without_decimal = code_str[:-2]
            if without_decimal.isdigit() or (without_decimal.startswith('0') and len(without_decimal) > 1):
                code_str = without_decimal
                
        desc = str(row.get("Description", "")).strip()
        if desc == "nan":
            desc = ""

        # Create text representation of barcode
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_xy(x, y + 2)
        pdf.cell(col_width, 6, code_str, align="C")
        
        # Add simple barcode-like pattern
        pdf.set_font("Courier", "", 10)
        pdf.set_xy(x, y + 10)
        barcode_text = "||||| " + code_str + " |||||"
        pdf.cell(col_width, 6, barcode_text, align="C")
        
        if desc:
            pdf.set_font("Helvetica", "", 8)
            pdf.set_xy(x, y + 18)
            if len(desc) > 25:
                desc = desc[:22] + "..."
            pdf.cell(col_width, 4, desc, align="C")

        pdf.rect(x, y, col_width, row_height - 2)

    pdf.output(output_path)
    return output_path