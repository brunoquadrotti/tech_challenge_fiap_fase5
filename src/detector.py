"""
Detecção de componentes arquiteturais.

Responsável por carregar o modelo YOLOv8 treinado e executar a inferência sobre
a imagem, retornando os componentes detectados (classe, confiança e bounding box).

A implementação será realizada na etapa de treinamento/inferência.
"""


class Detector:
    """Responsável por carregar o modelo YOLO e executar a inferência.

    Implementação será realizada na etapa de treinamento.
    """

    def __init__(self, model_path=None):
        # TODO: carregar os pesos do modelo YOLOv8 (models/best.pt)
        pass

    def detect(self, image):
        """Executa a inferência e retorna a lista estruturada de componentes.

        Args:
            image: Imagem já pré-processada.

        Returns:
            Lista de componentes detectados (classe, confiança, bounding box).
        """
        # TODO: executar a inferência com o modelo YOLOv8
        # TODO: converter a saída para a lista estruturada de componentes
        raise NotImplementedError("Detecção será implementada em etapa futura.")
