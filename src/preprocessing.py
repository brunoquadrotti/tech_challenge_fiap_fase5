"""
Pré-processamento de imagem.

Responsável por preparar a imagem enviada pelo usuário antes da inferência:
leitura, conversão de formato e redimensionamento, utilizando OpenCV e Pillow.

A implementação será realizada na etapa de processamento de imagem.
"""


def preprocess_image(image):
    """Prepara a imagem para a inferência do modelo.

    Args:
        image: Imagem de entrada (upload do usuário).

    Returns:
        Imagem tratada, pronta para o detector.
    """
    # TODO: ler a imagem (OpenCV / Pillow)
    # TODO: converter formato/canais de cor conforme necessário
    # TODO: redimensionar para o tamanho esperado pelo modelo
    raise NotImplementedError("Pré-processamento será implementado em etapa futura.")
