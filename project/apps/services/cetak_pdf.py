import os
from io import BytesIO

from django.conf import settings
from django.contrib.staticfiles import finders
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa


def link_callback(uri, rel):
    """
    Convert HTML URIs to absolute system paths so xhtml2pdf can access those resources
    """
    if uri.startswith(settings.STATIC_URL):
        path = finders.find(uri.replace(settings.STATIC_URL, ""))
    elif uri.startswith(settings.MEDIA_URL):
        path = os.path.join(
            settings.MEDIA_ROOT,
            uri.replace(settings.MEDIA_URL, "")
        )
    else:
        return uri

    if not path:
        raise Exception(f"Media file not found: {uri}")

    return os.path.realpath(path)



def render_to_pdf(template_src, context_dict={}, filename="document.pdf"):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()

    pdf = pisa.pisaDocument(
        BytesIO(html.encode("UTF-8")),
        result,
        link_callback=link_callback   # ⬅⬅⬅ INI WAJIB
    )

    if not pdf.err:
        response = HttpResponse(
            result.getvalue(),
            content_type='application/pdf'
        )
        response['Content-Disposition'] = f'inline; filename="{filename}"'
        return response

    return None

