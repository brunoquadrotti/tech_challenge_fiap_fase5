"""
Geração do relatório PDF da análise STRIDE.

A partir dos componentes detectados (:class:`~src.detector.Detection`), dos
relacionamentos inferidos (:class:`~src.relationship_extractor.Relationship`) e
das ameaças identificadas (:class:`~src.stride_engine.Threat`), este módulo
produz um relatório em PDF usando ReportLab.

A função principal, :func:`generate_report`, retorna os **bytes** do PDF (para
alimentar o ``st.download_button`` do Streamlit) e, opcionalmente, também grava
o arquivo em disco.

Os tipos de dados são importados apenas para checagem estática (``TYPE_CHECKING``)
a fim de manter o módulo desacoplado de dependências pesadas em tempo de
execução (por exemplo, o Ultralytics carregado por ``src.detector``). Em runtime,
os dados trafegam como dicts simples.
"""

from __future__ import annotations

import io
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, List, Optional, Union

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    ListFlowable,
    ListItem,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

if TYPE_CHECKING:  # apenas para type hints; evita dependência em runtime
    from src.detector import Detection
    from src.relationship_extractor import Relationship
    from src.stride_engine import Threat


def _build_styles() -> dict:
    """Cria os estilos de parágrafo usados no relatório."""
    styles = getSampleStyleSheet()

    styles.add(
        ParagraphStyle(
            name="ReportTitle",
            parent=styles["Title"],
            fontSize=20,
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="ReportSubtitle",
            parent=styles["Normal"],
            fontSize=10,
            textColor=colors.grey,
            spaceAfter=12,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SectionHeading",
            parent=styles["Heading2"],
            fontSize=14,
            spaceBefore=14,
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SubHeading",
            parent=styles["Heading3"],
            fontSize=11,
            spaceBefore=8,
            spaceAfter=4,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Body",
            parent=styles["Normal"],
            fontSize=9,
            alignment=TA_LEFT,
            spaceAfter=4,
        )
    )
    return styles


def _components_section(components: List["Detection"], styles: dict) -> list:
    """Monta a seção "Componentes detectados"."""
    flowables: list = [Paragraph("Componentes detectados", styles["SectionHeading"])]

    if not components:
        flowables.append(
            Paragraph("Nenhum componente foi detectado.", styles["Body"])
        )
        return flowables

    header = ["Componente", "Confiança", "Bounding box [x1, y1, x2, y2]"]
    rows = [header]
    for component in components:
        confidence = f"{float(component['confidence']) * 100:.1f}%"
        bbox = ", ".join(str(coord) for coord in component["bbox"])
        rows.append([str(component["class_name"]), confidence, f"[{bbox}]"])

    table = Table(rows, colWidths=[70 * mm, 30 * mm, 70 * mm], repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c3e50")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("ALIGN", (1, 0), (1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [colors.white, colors.HexColor("#f2f4f6")],
                ),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    flowables.append(table)
    return flowables


def _relationships_section(
    relationships: List["Relationship"], styles: dict
) -> list:
    """Monta a seção "Relacionamentos" no formato ``tipo: source -> target``."""
    flowables: list = [Paragraph("Relacionamentos", styles["SectionHeading"])]

    if not relationships:
        flowables.append(
            Paragraph("Nenhum relacionamento foi identificado.", styles["Body"])
        )
        return flowables

    items = [
        ListItem(
            Paragraph(
                f"{rel['type']}: {rel['source']} -&gt; {rel['target']}",
                styles["Body"],
            )
        )
        for rel in relationships
    ]
    flowables.append(ListFlowable(items, bulletType="bullet", leftIndent=12))
    return flowables


def _threats_section(threats: List["Threat"], styles: dict) -> list:
    """Monta a seção "Ameaças e contramedidas" agrupada por componente e categoria."""
    flowables: list = [Paragraph("Ameaças e contramedidas", styles["SectionHeading"])]

    if not threats:
        flowables.append(
            Paragraph("Nenhuma ameaça foi identificada.", styles["Body"])
        )
        return flowables

    # Agrupa por componente e, dentro dele, por categoria STRIDE, mantendo a
    # ordem determinística já produzida pelo StrideEngine.
    grouped: dict = {}
    for threat in threats:
        component = threat["component"]
        category = threat["category"]
        grouped.setdefault(component, {}).setdefault(category, []).append(threat)

    for component in grouped:
        flowables.append(Paragraph(f"Componente: {component}", styles["SubHeading"]))

        for category in grouped[component]:
            flowables.append(
                Paragraph(f"<b>{category}</b>", styles["Body"])
            )

            for threat in grouped[component][category]:
                related = threat.get("related_to")
                related_suffix = (
                    f" (relacionado a {related})" if related else ""
                )
                flowables.append(
                    Paragraph(
                        f"{threat['description']}{related_suffix}", styles["Body"]
                    )
                )

                countermeasures = threat.get("countermeasures") or []
                if countermeasures:
                    flowables.append(
                        Paragraph("Contramedidas:", styles["Body"])
                    )
                    items = [
                        ListItem(Paragraph(str(cm), styles["Body"]))
                        for cm in countermeasures
                    ]
                    flowables.append(
                        ListFlowable(
                            items, bulletType="bullet", leftIndent=18
                        )
                    )
                flowables.append(Spacer(1, 4))

    return flowables


def generate_report(
    components: List["Detection"],
    relationships: List["Relationship"],
    threats: List["Threat"],
    output: Optional[Union[str, Path]] = None,
) -> bytes:
    """Gera o relatório PDF da análise STRIDE e retorna seus bytes.

    Args:
        components: Componentes detectados na imagem.
        relationships: Relacionamentos inferidos entre os componentes.
        threats: Ameaças STRIDE identificadas.
        output: Caminho opcional para gravar o PDF em disco. Quando informado,
            os mesmos bytes retornados também são escritos nesse caminho.

    Returns:
        Os bytes do PDF gerado.
    """
    styles = _build_styles()
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        title="Relatório de Análise STRIDE",
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
    )

    generated_at = datetime.now().strftime("%d/%m/%Y %H:%M")

    story: list = [
        Paragraph("Relatório de Análise STRIDE", styles["ReportTitle"]),
        Paragraph(f"Gerado em {generated_at}", styles["ReportSubtitle"]),
    ]
    story.extend(_components_section(components, styles))
    story.extend(_relationships_section(relationships, styles))
    story.extend(_threats_section(threats, styles))

    doc.build(story)

    pdf_bytes = buffer.getvalue()
    buffer.close()

    if output is not None:
        output_path = Path(output)
        if output_path.parent and not output_path.parent.exists():
            output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(pdf_bytes)

    return pdf_bytes
