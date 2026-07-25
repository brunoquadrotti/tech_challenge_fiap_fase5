"""
Treinamento supervisionado do modelo YOLOv8.

Responsável por treinar o modelo de detecção de componentes arquiteturais a
partir do dataset anotado (datasets/), utilizando a configuração definida em
dataset/data.yaml. Os pesos resultantes serão salvos em models/.
"""

from pathlib import Path

from ultralytics import YOLO


def main():
    project_root = Path(__file__).resolve().parent.parent

    dataset_yaml = (
        project_root
        / "datasets"
        / "stride-architecture-components-v1"
        / "data.yaml"
    )

    print(dataset_yaml)
    print(dataset_yaml.exists())

    model = YOLO("yolo11s.pt")

    model.train(
        data=str(dataset_yaml),
        epochs=100,
        imgsz=640,
        batch=-1,
        device=0,
        workers=8,
        project=str(project_root / "runs"),
        name="stride_yolo11s_baseline",
        pretrained=True,
        exist_ok=True,
        seed=42,
        deterministic=True,
        verbose=True,
        plots=True,
    )


if __name__ == "__main__":
    main()