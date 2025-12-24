import io

from PyPDF2 import PdfReader, PdfWriter
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def stream_sertifikat_pdf(template_path, position_data, context_data, scale=1.2):
    reader = PdfReader(template_path)
    writer = PdfWriter()

    for page_index, page in enumerate(reader.pages, start=1):
        media_box = page.mediabox
        page_width = float(media_box.width)
        page_height = float(media_box.height)

        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=(page_width, page_height))

        page_key = str(page_index)

        if page_key in position_data:
            for field, cfg in position_data[page_key].items():
                text = str(context_data.get(field, ""))
                size = cfg.get("size", 12)
                align = cfg.get("align", "left")

                css_x = cfg["x"]
                css_y = cfg["y"]

                pdf_x = css_x / scale
                pdf_y = page_height - (css_y / scale) - size

                can.setFont("Helvetica", size)

                if align == "center":
                    can.drawCentredString(pdf_x, pdf_y, text)
                elif align == "right":
                    can.drawRightString(pdf_x, pdf_y, text)
                else:
                    can.drawString(pdf_x, pdf_y, text)

        can.save()
        packet.seek(0)

        overlay = PdfReader(packet).pages[0]
        page.merge_page(overlay)
        writer.add_page(page)

    output = io.BytesIO()
    writer.write(output)
    output.seek(0)
    return output


