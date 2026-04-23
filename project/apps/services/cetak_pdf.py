import os
import re
from io import BytesIO

from django.conf import settings
from django.contrib.staticfiles import finders
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa


def _strip_manifest_hash(relative_path):
    """
    ManifestStaticFilesStorage appends a content hash before the extension,
    e.g. 'images/logo/ums_logo_color.490156a3b753.png'
         → 'images/logo/ums_logo_color.png'
    Strip it so finders.find() can locate the source file.
    """
    return re.sub(r'\.[a-f0-9]{12}(\.[^./]+)$', r'\1', relative_path)


def link_callback(uri, _rel):
    """
    Convert HTML URIs to absolute system paths so xhtml2pdf can access those resources.
    Handles ManifestStaticFilesStorage hashed filenames transparently.
    """
    if uri.startswith(settings.STATIC_URL):
        relative = uri.replace(settings.STATIC_URL, "")
        path = finders.find(relative) or finders.find(_strip_manifest_hash(relative))
    elif uri.startswith(settings.MEDIA_URL):
        path = os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, ""))
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

