"""
Funções auxiliares compartilhadas.

Reúne helpers comuns utilizados pelos demais módulos:

- :func:`load_json`: carregamento seguro de arquivos JSON.
- :func:`draw_detections`: desenho de bounding boxes e rótulos sobre uma cópia
  da imagem, para visualização das detecções na interface Streamlit.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import List, Union

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from src.detector import Detection

# Cor padrão usada para desenhar os bounding boxes e rótulos (RGB).
_BOX_COLOR = (255, 0, 0)
_LABEL_TEXT_COLOR = (255, 255, 255)


def load_json(path: Union[str, Path]) -> dict:
    """Carrega e retorna o conteúdo de um arquivo JSON.

    Args:
        path: Caminho para o arquivo JSON.

    Returns:
        O conteúdo do JSON como um dicionário.

    Raises:
        FileNotFoundError: Se o arquivo não existir.
        json.JSONDecodeError: Se o conteúdo não for um JSON válido.
    """
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def draw_detections(
    image: Union[Image.Image, np.ndarray],
    detections: List[Detection],
) -> Image.Image:
    """Desenha bounding boxes e rótulos sobre uma cópia da imagem.

    A imagem original não é modificada: o desenho é feito sobre uma cópia,
    preservando as dimensões originais.

    Args:
        image: Imagem de entrada (``PIL.Image.Image`` ou ``np.ndarray``).
        detections: Lista de detecções. Cada detecção deve conter ``bbox``
            (``[x1, y1, x2, y2]``) e ``class_name``.

    Returns:
        Uma cópia da imagem (``PIL.Image.Image`` RGB) com os bounding boxes
        e rótulos desenhados.
    """
    # Normaliza a entrada para um PIL.Image RGB, trabalhando sobre uma cópia
    # para não alterar a imagem original.
    if isinstance(image, np.ndarray):
        annotated = Image.fromarray(image).convert("RGB")
    else:
        annotated = image.convert("RGB").copy()

    draw = ImageDraw.Draw(annotated)
    font = ImageFont.load_default()

    for detection in detections:
        x1, y1, x2, y2 = detection["bbox"]
        label = detection["class_name"]

        # Bounding box.
        draw.rectangle([(x1, y1), (x2, y2)], outline=_BOX_COLOR, width=2)

        # Fundo do rótulo para melhorar a legibilidade.
        text_box = draw.textbbox((x1, y1), label, font=font)
        text_width = text_box[2] - text_box[0]
        text_height = text_box[3] - text_box[1]
        label_top = max(0, y1 - text_height - 2)
        draw.rectangle(
            [(x1, label_top), (x1 + text_width + 2, label_top + text_height + 2)],
            fill=_BOX_COLOR,
        )
        draw.text((x1 + 1, label_top + 1), label, fill=_LABEL_TEXT_COLOR, font=font)

    return annotated
