"""
Servicio para generar PDFs de planes de comidas
"""

from datetime import datetime
from io import BytesIO
from typing import Any, Dict, List

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


class PlanComidasPDFGenerator:
    """Generador de PDF para planes de comidas semanales"""

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Configurar estilos personalizados"""
        self.styles.add(
            ParagraphStyle(
                name="CustomTitle",
                parent=self.styles["Heading1"],
                fontSize=24,
                textColor=colors.HexColor("#2E7D32"),
                spaceAfter=30,
                alignment=TA_CENTER,
                fontName="Helvetica-Bold",
            )
        )

        self.styles.add(
            ParagraphStyle(
                name="CustomSubtitle",
                parent=self.styles["Heading2"],
                fontSize=14,
                textColor=colors.HexColor("#555555"),
                spaceAfter=20,
                alignment=TA_CENTER,
            )
        )

        self.styles.add(
            ParagraphStyle(
                name="ChildInfo",
                parent=self.styles["Normal"],
                fontSize=11,
                textColor=colors.HexColor("#333333"),
                spaceAfter=10,
            )
        )

        self.styles.add(
            ParagraphStyle(
                name="DayHeader",
                parent=self.styles["Heading3"],
                fontSize=13,
                textColor=colors.white,
                backColor=colors.HexColor("#2E7D32"),
                spaceAfter=8,
                spaceBefore=12,
                fontName="Helvetica-Bold",
            )
        )

    def generar_pdf_plan_semanal(
        self, plan_data: Dict[str, Any], nino_data: Dict[str, Any]
    ) -> BytesIO:
        """
        Genera un PDF del plan de comidas semanal

        Args:
            plan_data: Datos del plan de comidas con estructura de días y comidas
            nino_data: Información del niño (nombre, edad, etc.)

        Returns:
            BytesIO con el contenido del PDF
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40
        )

        story = []

        story.extend(self._crear_encabezado(plan_data, nino_data))

        story.extend(self._crear_info_nino(nino_data))

        story.append(Spacer(1, 0.3 * inch))

        story.extend(self._crear_plan_semanal(plan_data))

        story.append(Spacer(1, 0.3 * inch))
        story.extend(self._crear_resumen_nutricional(plan_data))

        story.extend(self._crear_pie_pagina())

        doc.build(story)
        buffer.seek(0)
        return buffer

    def _crear_encabezado(self, plan_data: Dict, nino_data: Dict) -> List:
        """Crear encabezado del PDF"""
        elements = []

        titulo = Paragraph("🍎 Plan de Comidas Semanal", self.styles["CustomTitle"])
        elements.append(titulo)

        periodo = plan_data.get("periodo", "No especificado")
        subtitulo = Paragraph(f"Período: {periodo}", self.styles["CustomSubtitle"])
        elements.append(subtitulo)

        elements.append(Spacer(1, 0.2 * inch))

        return elements

    def _crear_info_nino(self, nino_data: Dict) -> List:
        """Crear sección de información del niño"""
        elements = []

        data = [
            ["Información del Niño", ""],
            ["Nombre:", nino_data.get("nombre", "N/A")],
            ["Edad:", f"{nino_data.get('edad', 'N/A')} años"],
            ["Perfil Nutricional:", nino_data.get("clasificacion", "Normal")],
        ]

        table = Table(data, colWidths=[2 * inch, 4 * inch])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2E7D32")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 12),
                    ("SPAN", (0, 0), (-1, 0)),
                    ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                    ("BACKGROUND", (0, 1), (0, -1), colors.HexColor("#F5F5F5")),
                    ("FONTNAME", (0, 1), (0, -1), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 1), (-1, -1), 10),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 10),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                    ("TOPPADDING", (0, 0), (-1, -1), 8),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ]
            )
        )

        elements.append(table)
        return elements

    def _crear_plan_semanal(self, plan_data: Dict) -> List:
        """Crear tabla del plan semanal"""
        elements = []

        dias = plan_data.get("dias", [])
        dias_semana = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

        for idx, dia in enumerate(dias):
            dia_nombre = dias_semana[idx] if idx < len(dias_semana) else f"Día {idx + 1}"
            total_dia = dia.get("total_kcal", 0)

            elements.append(Spacer(1, 0.15 * inch))

            dia_header = Paragraph(
                f"<b>{dia_nombre}</b> - {total_dia:.0f} kcal", self.styles["DayHeader"]
            )
            elements.append(dia_header)

            comidas_data = [["Tipo", "Comida", "Calorías", "Proteínas"]]

            for comida in dia.get("comidas", []):
                comidas_data.append(
                    [
                        comida.get("tipo_comida", "N/A"),
                        comida.get("nombre", "N/A"),
                        f"{comida.get('kcal', 0):.0f} kcal",
                        f"{comida.get('proteina_g', 0):.1f} g",
                    ]
                )

            table = Table(comidas_data, colWidths=[1.2 * inch, 3 * inch, 1 * inch, 1 * inch])
            table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4CAF50")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, 0), 10),
                        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                        ("BACKGROUND", (0, 1), (0, -1), colors.HexColor("#E8F5E9")),
                        ("FONTNAME", (0, 1), (0, -1), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 1), (-1, -1), 9),
                        ("ALIGN", (2, 1), (-1, -1), "CENTER"),
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 8),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                        ("TOPPADDING", (0, 0), (-1, -1), 6),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                    ]
                )
            )

            elements.append(table)

        return elements

    def _crear_resumen_nutricional(self, plan_data: Dict) -> List:
        """Crear resumen nutricional semanal"""
        elements = []

        total_semanal = plan_data.get("total_semanal", 0)
        promedio_diario = plan_data.get("promedio_diario", 0)

        titulo = Paragraph("<b>Resumen Nutricional Semanal</b>", self.styles["Heading3"])
        elements.append(titulo)
        elements.append(Spacer(1, 0.1 * inch))

        data = [
            ["Concepto", "Valor"],
            ["Total Semanal", f"{total_semanal:.0f} kcal"],
            ["Promedio Diario", f"{promedio_diario:.0f} kcal"],
            ["Comidas por Semana", f"{len(plan_data.get('dias', [])) * 3} comidas"],
        ]

        table = Table(data, colWidths=[3 * inch, 2 * inch])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2E7D32")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 11),
                    ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                    ("BACKGROUND", (0, 1), (0, -1), colors.HexColor("#F5F5F5")),
                    ("FONTNAME", (0, 1), (0, -1), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 1), (-1, -1), 10),
                    ("ALIGN", (1, 1), (1, -1), "CENTER"),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 10),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                    ("TOPPADDING", (0, 0), (-1, -1), 8),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ]
            )
        )

        elements.append(table)
        return elements

    def _crear_pie_pagina(self) -> List:
        """Crear pie de página"""
        elements = []

        elements.append(Spacer(1, 0.5 * inch))

        fecha_generacion = datetime.now().strftime("%d/%m/%Y %H:%M")
        pie = Paragraph(
            f"<i>Documento generado automáticamente por NutriFamily - {fecha_generacion}</i>",
            self.styles["Normal"],
        )
        elements.append(pie)

        nota = Paragraph(
            "<i>Nota: Este plan de comidas ha sido personalizado según el perfil nutricional del niño. "
            "Consulte con un profesional de la salud para cualquier ajuste necesario.</i>",
            self.styles["Normal"],
        )
        elements.append(nota)

        return elements
