"""
Motor de análise STRIDE baseado em regras.

A partir dos componentes detectados (:class:`~src.detector.Detection`) e dos
relacionamentos inferidos (:class:`~src.relationship_extractor.Relationship`),
este módulo consulta uma base de conhecimento (Knowledge Base) em JSON e produz
a lista de ameaças STRIDE identificadas.

A análise é **100% baseada em regras**, determinística e sem qualquer uso de
inteligência artificial: as ameaças resultam exclusivamente da correspondência
entre os componentes/relacionamentos e as entradas da Knowledge Base.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Literal, Optional, TypedDict, Union

from src.detector import Detection
from src.relationship_extractor import Relationship
from src.utils import load_json

# Caminho padrão para a base de conhecimento STRIDE.
DEFAULT_KNOWLEDGE_BASE_PATH = "data/stride_knowledge_base.json"

# As seis categorias canônicas do modelo STRIDE.
StrideCategory = Literal[
    "Spoofing",
    "Tampering",
    "Repudiation",
    "Information Disclosure",
    "Denial of Service",
    "Elevation of Privilege",
]


class Threat(TypedDict):
    """Ameaça STRIDE identificada para um componente ou relacionamento."""

    component: str                 # class_name do componente afetado
    category: StrideCategory       # categoria STRIDE
    description: str               # descrição da ameaça
    countermeasures: List[str]     # contramedidas recomendadas
    related_to: Optional[str]      # class_name do componente relacionado, ou None


class StrideEngine:
    """Aplica a análise STRIDE por regras consultando a Knowledge Base.

    A base de conhecimento é carregada uma única vez, durante a inicialização, e
    reutilizada em todas as chamadas a :meth:`analyze`.
    """

    def __init__(
        self,
        knowledge_base_path: Union[str, Path] = DEFAULT_KNOWLEDGE_BASE_PATH,
    ) -> None:
        """Carrega a Knowledge Base JSON.

        Args:
            knowledge_base_path: Caminho para o arquivo JSON da base de
                conhecimento. Por padrão, ``data/stride_knowledge_base.json``.

        Raises:
            FileNotFoundError: Se o arquivo da base não for encontrado.
            json.JSONDecodeError: Se o conteúdo não for um JSON válido.
        """
        self.knowledge_base_path = Path(knowledge_base_path)
        knowledge_base = load_json(self.knowledge_base_path)

        # Mapa: class_name -> lista de entradas de ameaça.
        self._components: dict = knowledge_base.get("components", {})
        # Mapa: RelationshipType -> lista de entradas de ameaça.
        self._relationship_rules: dict = knowledge_base.get("relationship_rules", {})

    def analyze(
        self,
        components: List[Detection],
        relationships: List[Relationship],
    ) -> List[Threat]:
        """Identifica as ameaças STRIDE dos componentes e relacionamentos.

        Args:
            components: Componentes detectados na imagem.
            relationships: Relacionamentos inferidos entre os componentes.

        Returns:
            Lista de :class:`Threat`. A saída é determinística: a mesma entrada
            sempre produz a mesma lista, ordenada de forma estável por
            ``component``, ``category`` e ``related_to``. Componentes sem
            correspondência na Knowledge Base não geram ameaças.
        """
        threats: List[Threat] = []

        # Ameaças por componente. Considera cada class_name uma única vez
        # (componentes repetidos não duplicam ameaças) e em ordem estável.
        unique_class_names = sorted({component["class_name"] for component in components})
        for class_name in unique_class_names:
            for entry in self._components.get(class_name, []):
                threats.append(
                    Threat(
                        component=class_name,
                        category=entry["category"],
                        description=entry["description"],
                        countermeasures=list(entry["countermeasures"]),
                        related_to=None,
                    )
                )

        # Ameaças por relacionamento. Cada par (source, target, type) é
        # considerado uma única vez e apenas se houver regra para o tipo.
        seen_relationships: set = set()
        for relationship in relationships:
            rel_type = relationship["type"]
            rules = self._relationship_rules.get(rel_type)
            if not rules:
                continue

            source = relationship["source"]
            target = relationship["target"]
            key = (rel_type, source, target)
            if key in seen_relationships:
                continue
            seen_relationships.add(key)

            for entry in rules:
                threats.append(
                    Threat(
                        component=source,
                        category=entry["category"],
                        description=entry["description"],
                        countermeasures=list(entry["countermeasures"]),
                        related_to=target,
                    )
                )

        # Ordenação estável e determinística por componente, categoria e
        # componente relacionado (None ordenado primeiro).
        threats.sort(
            key=lambda threat: (
                threat["component"],
                threat["category"],
                threat["related_to"] or "",
            )
        )

        return threats
