"""
Pré-processamento da imagem de entrada.

Converte a entrada enviada pelo usuário (bytes do uploader do Streamlit,
caminho de arquivo, array NumPy/OpenCV ou objeto Pillow) em um ``PIL.Image``
em modo ``RGB``, formato aceito diretamente pelo :class:`~src.detector.Detector`.

O módulo é intencionalmente enxuto: valida e normaliza a entrada, sem
redimensionamento agressivo nem filtros, pois o YOLO já cuida do resize interno.
"""

from __future__ import annotations

import io
from pathlib import Path
from typing import Union

import numpy as np
from PIL import Image, UnidentifiedImageError

# Tipos de entrada aceitos pelo pré-processamento.
PreprocessInput = Union[str, Path, bytes, np.ndarray, Image.Image]


class InvalidImageError(ValueError):
    """Sinaliza que a entrada não pôde ser lida como imagem válida."""


def preprocess_image(image: PreprocessInput) -> Image.Image:
    """Valida e normaliza a entrada para um ``PIL.Image`` RGB.

    Args:
        image: Imagem de entrada. Aceita bytes (uploader do Streamlit),
            caminho de arquivo (``str``/``Path``), array NumPy/OpenCV
            (``np.ndarray``) ou objeto Pillow (``PIL.Image.Image``).

    Returns:
        Um ``PIL.Image.Image`` em modo ``RGB``, pronto para o ``Detector``.

    Raises:
        InvalidImageError: Se a entrada for ``None`` ou não puder ser
            decodificada como uma imagem válida.
    """
    if image is None:
        raise InvalidImageError("A imagem de entrada não pode ser None.")

    try:
        if isinstance(image, Image.Image):
            pil_image = image
        elif isinstance(image, (bytes, bytearray)):
            pil_image = Image.open(io.BytesIO(bytes(image)))
        elif isinstance(image, (str, Path)):
            pil_image = Image.open(image)
        elif isinstance(image, np.ndarray):
            pil_image = Image.fromarray(image)
        else:
            raise InvalidImageError(
                f"Tipo de entrada não suportado: {type(image).__name__}. "
                "Esperado bytes, caminho de arquivo, np.ndarray ou PIL.Image."
            )

        # Força o carregamento dos dados para detectar arquivos corrompidos
        # e converte para RGB (formato esperado pelo Detector).
        return pil_image.convert("RGB")
    except InvalidImageError:
        raise
    except (UnidentifiedImageError, FileNotFoundError, OSError, ValueError, TypeError) as exc:
        raise InvalidImageError(
            f"Não foi possível decodificar a entrada como imagem válida: {exc}"
        ) from exc
