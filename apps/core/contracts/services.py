from django.template.loader import render_to_string


class ContractPDFService:
    def __init__(self, tenant, user):
        self.tenant = tenant
        self.user = user

    def generate_contract(self, contract):
        # Importar WeasyPrint de forma perezosa para evitar errores de entorno
        from weasyprint import HTML  # noqa: WPS433

        html = render_to_string(
            "export/contract.html", {"contract": contract, "tenant": self.tenant}
        )
        pdf_bytes = HTML(string=html).write_pdf()
        filename = f"{contract.id}-{contract.title}.pdf"
        contract.document.save(filename, content=bytes(pdf_bytes))
        return filename