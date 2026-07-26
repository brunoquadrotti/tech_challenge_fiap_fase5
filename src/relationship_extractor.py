"""
Extração geométrica de relacionamentos entre componentes.

A partir da lista de :class:`~src.detector.Detection`, este módulo infere
relacionamentos entre os componentes usando **exclusivamente informação
geométrica** (``bbox`` e ``center``) — sem OCR e sem qualquer inteligência
artificial.

São inferidos dois tipos de relacionamento:

- ``"contains"``: um trust boundary (componente cujo ``class_name`` começa com
  ``boundary_``) contém geometricamente outro componente.
- ``"connected_to"``: dois componentes não-boundary estão próximos o suficiente
  para serem considerados conectados/vizinhos.

O módulo é totalmente desacoplado do Detector e da interface (Streamlit),
dependendo apenas do tipo de dado simples :class:`Detection`.
"""

from __future__ import annotations

from typing import List, Literal, Sequence, Tuple, TypedDict

from src.detector import Detection

# Prefixo que identifica trust boundaries entre os nomes de classe do modelo.
BOUNDARY_PREFIX = "boundary_"

# Tipos de relacionamento suportados.
RelationshipType = Literal["contains", "connected_to"]


class Relationship(TypedDict):
    """Relacionamento geométrico inferido entre dois componentes."""

    type: RelationshipType  # "contains" (boundary→componente) ou "connected_to"
    source: str  # class_name do componente de origem
    target: str  # class_name do componente de destino


def _is_boundary(detection: Detection) -> bool:
    """Indica se a detecção corresponde a um trust boundary."""
    return detection["class_name"].startswith(BOUNDARY_PREFIX)


def _center_inside_bbox(center: Tuple[int, int], bbox: Sequence[int]) -> bool:
    """Verifica se um ponto ``center`` está dentro de ``bbox`` [x1, y1, x2, y2]."""
    cx, cy = center
    x1, y1, x2, y2 = bbox
    return x1 <= cx <= x2 and y1 <= cy <= y2


def _distance(a: Tuple[int, int], b: Tuple[int, int]) -> float:
    """Distância euclidiana entre dois centros."""
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5


def _diagonal(detection: Detection) -> float:
    """Comprimento da diagonal do bbox, usado como escala do componente."""
    return (detection["width"] ** 2 + detection["height"] ** 2) ** 0.5


def extract_relationships(detections: List[Detection]) -> List[Relationship]:
    """Infere relacionamentos geométricos entre os componentes detectados.

    Usa apenas ``bbox`` e ``center`` de cada detecção (sem OCR).

    Args:
        detections: Lista de componentes detectados pelo Detector.

    Returns:
        Lista de :class:`Relationship`. Retorna uma lista vazia quando
        ``detections`` for vazia.
    """
    if not detections:
        return []

    relationships: List[Relationship] = []

    boundaries = [d for d in detections if _is_boundary(d)]
    components = [d for d in detections if not _is_boundary(d)]

    # Containment: um boundary "contém" um componente quando o centro do
    # componente está dentro do bbox do boundary. É uma heurística simples e
    # robusta a pequenas sobreposições de bordas.
    for boundary in boundaries:
        for component in components:
            if _center_inside_bbox(component["center"], boundary["bbox"]):
                relationships.append(
                    Relationship(
                        type="contains",
                        source=boundary["class_name"],
                        target=component["class_name"],
                    )
                )

    # Conexão/vizinhança: dois componentes não-boundary estão conectados quando
    # a distância entre seus centros é pequena em relação ao tamanho deles. A
    # escala é derivada da média das diagonais dos dois componentes, o que
    # torna a heurística independente da resolução da imagem. Cada par é
    # avaliado uma única vez (i < j) para evitar duplicatas simétricas.
    for i in range(len(components)):
        for j in range(i + 1, len(components)):
            comp_a = components[i]
            comp_b = components[j]

            scale = (_diagonal(comp_a) + _diagonal(comp_b)) / 2
            if scale <= 0:
                continue

            if _distance(comp_a["center"], comp_b["center"]) <= 1.5 * scale:
                relationships.append(
                    Relationship(
                        type="connected_to",
                        source=comp_a["class_name"],
                        target=comp_b["class_name"],
                    )
                )

    return relationships
