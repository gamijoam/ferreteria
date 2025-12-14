from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import mm
from reportlab.graphics.barcode import code128
from reportlab.graphics import renderPDF
import os
import tempfile

class LabelGenerator:
    def __init__(self):
        # Avery 5160 / 30-up labels configuration (Generic)
        self.page_size = LETTER
        self.columns = 3
        self.rows = 10
        self.margin_x = 4 * mm
        self.margin_y = 12 * mm
        self.col_width = 66.6 * mm # Approx 2.625 inches
        self.row_height = 25.4 * mm # 1 inch
        self.padding_x = 2 * mm
        self.padding_y = 2 * mm

    def generate_pdf(self, items, output_path=None):
        """
        Generate PDF with labels.
        items: List of dicts {'name', 'sku', 'price', 'quantity'}
        output_path: If None, creates a temp file.
        Returns: Path to generated PDF.
        """
        if not output_path:
            temp_dir = tempfile.gettempdir()
            output_path = os.path.join(temp_dir, "etiquetas_ferreteria.pdf")

        c = canvas.Canvas(output_path, pagesize=self.page_size)
        width, height = self.page_size
        
        # Flatten queue items into individual labels
        labels_to_print = []
        for item in items:
            qty = item.get('quantity', 1)
            for _ in range(qty):
                labels_to_print.append(item)

        col = 0
        row = 0
        
        # Start top-left
        # Coordinates in ReportLab start at bottom-left
        # Calculate top-left of first label (row 0, col 0)
        # Row 0 is the TOP row on the physical sheet.
        
        for item in labels_to_print:
            # Calculate position
            # X = margin + col * width
            x = self.margin_x + (col * self.col_width)
            
            # Y = height - margin - (row + 1) * height
            y = height - self.margin_y - ((row + 1) * self.row_height)
            
            self._draw_label(c, x, y, item)
            
            # Advance position
            col += 1
            if col >= self.columns:
                col = 0
                row += 1
                
            if row >= self.rows:
                # New page
                c.showPage()
                row = 0
                col = 0

        c.save()
        return output_path

    def _draw_label(self, c, x, y, item):
        """Draw content of a single label at x, y (bottom-left of label)"""
        # Draw border (optional, helps for alignment)
        # c.rect(x, y, self.col_width, self.row_height)
        
        # Content setup
        name = item['name'][:25] # Truncate long names
        price = f"${item['price']:,.2f}"
        sku = item.get('sku', '') or 'N/A'
        
        # Text settings
        c.setFont("Helvetica-Bold", 10)
        
        # Draw Name (Top center-ish)
        c.drawString(x + 5*mm, y + 18*mm, name)
        
        # Draw Price (Below name)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(x + 5*mm, y + 12*mm, price)
        
        # Draw Barcode (Bottom)
        if sku and sku != 'N/A':
            try:
                # Generate Code128
                barcode = code128.Code128(sku, barHeight=6*mm, barWidth=1.2) # Adjusted width
                
                # Render barcode
                # x, y are absolute coords
                renderPDF.draw(barcode, c, x + 5*mm, y + 2*mm)
                
                # Draw SKU text below barcode? usually barcode includes text or we draw it
                c.setFont("Helvetica", 8)
                c.drawString(x + 40*mm, y + 4*mm, sku)
            except Exception as e:
                print(f"Error barcode: {e}")
                c.drawString(x + 5*mm, y + 5*mm, f"SKU: {sku}")
        else:
             c.drawString(x + 5*mm, y + 5*mm, "SIN SKU")
