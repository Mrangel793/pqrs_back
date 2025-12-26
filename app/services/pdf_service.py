from jinja2 import Environment, FileSystemLoader
def generar_pdf(html_content: str, output_path: str):
    from weasyprint import HTML
    HTML(string=html_content).write_pdf(output_path)

import os
from datetime import datetime
from typing import Dict, Any

from app.config import settings
from app.core.exceptions import PDFGenerationException


class PDFService:
    """Servicio para generación de PDFs"""

    def __init__(self):
        self.template_dir = os.path.join(os.path.dirname(__file__), "..", "templates", "pdf")
        self.env = Environment(loader=FileSystemLoader(self.template_dir))

    def render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """Renderizar template HTML"""
        try:
            template = self.env.get_template(template_name)
            return template.render(**context)
        except Exception as e:
            raise PDFGenerationException(f"Error renderizando template: {str(e)}")

    def generate_pdf(self, html_content: str, output_path: str) -> str:
        """Generar PDF desde HTML"""
        try:
            HTML(string=html_content).write_pdf(output_path)
            return output_path
        except Exception as e:
            raise PDFGenerationException(f"Error generando PDF: {str(e)}")

    def generate_factura_pdf(self, data: Dict[str, Any]) -> str:
        """Generar PDF de factura"""
        context = {
            "fecha": datetime.now().strftime("%d/%m/%Y"),
            "numero_factura": data.get("numero_factura"),
            "cliente": data.get("cliente"),
            "items": data.get("items", []),
            "total": data.get("total", 0)
        }

        html = self.render_template("factura.html", context)
        output_path = os.path.join(settings.UPLOAD_DIR, f"factura_{data.get('numero_factura')}.pdf")
        return self.generate_pdf(html, output_path)

    def generate_postilla_apostilla_pdf(self, data: Dict[str, Any]) -> str:
        """Generar PDF de postilla/apostilla"""
        context = {
            "fecha": datetime.now().strftime("%d/%m/%Y"),
            "tipo": data.get("tipo", "Postilla"),
            "documento": data.get("documento"),
            "destinatario": data.get("destinatario"),
            "numero_caso": data.get("numero_caso")
        }

        html = self.render_template("postilla_apostilla.html", context)
        output_path = os.path.join(settings.UPLOAD_DIR, f"postilla_{data.get('numero_caso')}.pdf")
        return self.generate_pdf(html, output_path)

    def generate_falla_no_respuesta_pdf(self, data: Dict[str, Any]) -> str:
        """Generar PDF de falla/no respuesta"""
        context = {
            "fecha": datetime.now().strftime("%d/%m/%Y"),
            "numero_caso": data.get("numero_caso"),
            "asunto": data.get("asunto"),
            "descripcion": data.get("descripcion"),
            "fecha_vencimiento": data.get("fecha_vencimiento")
        }

        html = self.render_template("falla_no_respuesta.html", context)
        output_path = os.path.join(settings.UPLOAD_DIR, f"falla_{data.get('numero_caso')}.pdf")
        return self.generate_pdf(html, output_path)


pdf_service = PDFService()
