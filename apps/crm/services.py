from io import BytesIO
from datetime import datetime

from django.template.loader import render_to_string
from django.core.files.base import ContentFile

try:
    from weasyprint import HTML
except Exception:
    HTML = None


class ContractPDFService:
    """Servicio de generación de PDF para contratos.

    Genera un PDF a partir de una plantilla HTML ubicada en
    `apps/crm/templates/export/contract.html` y guarda el archivo
    en el campo `document` del contrato (upload_to='contracts/').
    """

    def __init__(self, tenant, user=None):
        self.tenant = tenant
        self.user = user

    def get_filename(self, contract):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"contrato_{contract.id}_{timestamp}.pdf"

    def render_html(self, contract):
        context = {
            'contract': contract,
            'client': contract.client,
            'tenant': contract.tenant,
            'generated_at': datetime.now(),
            'user': self.user,
        }
        return render_to_string('export/contract.html', context)

    def generate_pdf_bytes(self, html_content):
        if HTML is None:
            raise RuntimeError('WeasyPrint no está disponible en el entorno')

        pdf_bytes = HTML(string=html_content).write_pdf()
        return BytesIO(pdf_bytes)

    def generate_contract(self, contract):
        """Genera y guarda el PDF del contrato.

        - Renderiza el HTML de la plantilla `export/contract.html`.
        - Convierte el HTML a PDF usando WeasyPrint.
        - Guarda el archivo en `contracts/` a través de `contract.document`.
        - Retorna el nombre de archivo guardado.
        """
        html_content = self.render_html(contract)
        pdf_buffer = self.generate_pdf_bytes(html_content)

        filename = self.get_filename(contract)
        # Guardar en FileField respetando `upload_to='contracts/'`
        contract.document.save(filename, ContentFile(pdf_buffer.getvalue()), save=True)
        return filename