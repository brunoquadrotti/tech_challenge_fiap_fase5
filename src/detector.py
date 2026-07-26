"""
Detecção de componentes arquiteturais.

Responsável por carregar o modelo YOLOv8 treinado e executar a inferência sobre
uma imagem, retornando os componentes detectados (classe, id da classe,
confiança e bounding box).

O módulo encapsula completamente o uso do Ultralytics YOLO e é totalmente
desacoplado da interface (Streamlit) e da lógica STRIDE, podendo ser reutilizado
por qualquer parte da aplicação.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Tuple, TypedDict, Union

import numpy as np
from PIL import Image
from ultralytics import YOLO

# Caminho padrão para os pesos do modelo treinado.
DEFAULT_MODEL_PATH = "models/best.pt"

# Tipos de imagem aceitos: caminho, array NumPy/OpenCV ou objeto Pillow.
ImageInput = Union[str, Path, np.ndarray, Image.Image]


class Detection(TypedDict):
    """Estrutura de uma única detecção retornada pelo Detector."""

    class_name: str
    class_id: int
    confidence: float
    bbox: List[int]  # [x1, y1, x2, y2]
    width: int
    height: int
    center: Tuple[int, int]  # (cx, cy)


class Detector:
    """Encapsula o modelo YOLO e executa a inferência de componentes.

    O modelo é carregado uma única vez, durante a inicialização, e reutilizado
    em todas as chamadas a :meth:`detect`.
    """

    def __init__(self, model_path: Union[str, Path] = DEFAULT_MODEL_PATH) -> None:
        """Carrega o modelo YOLO treinado.

        Args:
            model_path: Caminho para o arquivo de pesos (.pt). Por padrão,
                ``models/best.pt``.

        Raises:
            FileNotFoundError: Se o arquivo de pesos não for encontrado.
            RuntimeError: Se ocorrer falha ao carregar o modelo.
        """
        self.model_path = Path(model_path)

        if not self.model_path.is_file():
            raise FileNotFoundError(
                f"Modelo não encontrado em '{self.model_path}'. "
                "Verifique se o treinamento foi concluído e os pesos foram salvos."
            )

        try:
            self.model = YOLO(str(self.model_path))
        except Exception as exc:  # noqa: BLE001 - encapsula falha de carregamento
            raise RuntimeError(
                f"Falha ao carregar o modelo YOLO de '{self.model_path}': {exc}"
            ) from exc

    def detect(self, image: ImageInput, confidence: float = 0.25) -> List[Detection]:
        """Executa a inferência sobre uma imagem.

        Args:
            image: Imagem de entrada. Aceita caminho de arquivo, array
                NumPy/OpenCV (BGR) ou objeto Pillow (``PIL.Image.Image``).
            confidence: Limiar mínimo de confiança para considerar uma
                detecção. Padrão ``0.25``.

        Returns:
            Lista de detecções. Cada item é um dicionário com:
                - ``class_name`` (str): nome da classe detectada.
                - ``class_id`` (int): índice numérico da classe.
                - ``confidence`` (float): confiança da detecção (0.0 a 1.0).
                - ``bbox`` (List[int]): caixa delimitadora [x1, y1, x2, y2]
                  em coordenadas de pixel.
                - ``width`` (int): largura da caixa em pixels.
                - ``height`` (int): altura da caixa em pixels.
                - ``center`` (Tuple[int, int]): centro da caixa (cx, cy) em pixels.

        Raises:
            ValueError: Se a imagem for ``None``.
            RuntimeError: Se ocorrer falha durante a inferência.
        """
        if image is None:
            raise ValueError("A imagem de entrada não pode ser None.")

        try:
            results = self.model.predict(source=image, conf=confidence, verbose=False)
        except Exception as exc:  # noqa: BLE001 - encapsula falha de inferência
            raise RuntimeError(f"Falha ao executar a inferência: {exc}") from exc

        detections: List[Detection] = []

        for result in results:
            boxes = getattr(result, "boxes", None)
            if boxes is None:
                continue

            names = result.names  # mapa {class_id: class_name}

            for box in boxes:
                class_id = int(box.cls[0])
                x1, y1, x2, y2 = (int(coord) for coord in box.xyxy[0])
                width = x2 - x1
                height = y2 - y1

                detections.append(
                    Detection(
                        class_name=str(names.get(class_id, str(class_id))),
                        class_id=class_id,
                        confidence=float(box.conf[0]),
                        bbox=[x1, y1, x2, y2],
                        width=width,
                        height=height,
                        center=(x1 + width // 2, y1 + height // 2),
                    )
                )

        return detections
