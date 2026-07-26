"""
Aplicação Streamlit — Detecção de Componentes Arquiteturais e Modelagem STRIDE.

Ponto de entrada da aplicação. Integra o pipeline completo de análise:
pré-processamento da imagem, detecção de componentes com YOLOv8, extração
geométrica de relacionamentos, análise STRIDE baseada em regras e geração do
relatório PDF.

Ordem de execução do pipeline (Requirement 6.1):
``preprocess_image`` → ``Detector.detect`` → ``extract_relationships``
→ ``StrideEngine.analyze`` → ``generate_report``.

O ``Detector`` e o ``StrideEngine`` são instanciados uma única vez via
``st.cache_resource`` (carregam, respectivamente, o modelo YOLO e a base de
conhecimento apenas uma vez por sessão).
"""

import streamlit as st

from src.detector import Detector
from src.preprocessing import InvalidImageError, preprocess_image
from src.relationship_extractor import extract_relationships
from src.report_generator import generate_report
from src.stride_engine import StrideEngine
from src.utils import draw_detections


@st.cache_resource
def get_detector() -> Detector:
    """Instancia o ``Detector`` uma única vez (carrega o modelo YOLO)."""
    return Detector()


@st.cache_resource
def get_stride_engine() -> StrideEngine:
    """Instancia o ``StrideEngine`` uma única vez (carrega a Knowledge Base)."""
    return StrideEngine()


def _render_components(detections) -> None:
    """Exibe a lista de componentes detectados (nome e confiança)."""
    st.subheader("Componentes detectados")
    rows = [
        {
            "Componente": detection["class_name"],
            "Confiança": f"{float(detection['confidence']) * 100:.1f}%",
        }
        for detection in detections
    ]
    st.dataframe(rows, use_container_width=True, hide_index=True)


def _render_threats(threats) -> None:
    """Exibe as ameaças STRIDE identificadas, agrupadas por componente."""
    st.subheader("Ameaças STRIDE identificadas")

    if not threats:
        st.info("Nenhuma ameaça foi identificada.")
        return

    # Agrupa por componente para uma leitura mais organizada.
    grouped: dict = {}
    for threat in threats:
        grouped.setdefault(threat["component"], []).append(threat)

    for component, component_threats in grouped.items():
        st.markdown(f"**{component}**")
        for threat in component_threats:
            related = threat.get("related_to")
            related_suffix = f" — relacionado a `{related}`" if related else ""
            with st.expander(f"{threat['category']}{related_suffix}"):
                st.write(threat["description"])
                countermeasures = threat.get("countermeasures") or []
                if countermeasures:
                    st.markdown("**Contramedidas:**")
                    for countermeasure in countermeasures:
                        st.markdown(f"- {countermeasure}")


def _run_pipeline(uploaded_file, detector: Detector, stride_engine: StrideEngine) -> None:
    """Executa o pipeline completo e exibe os resultados.

    Todo o fluxo é envolvido em ``try/except`` pelo chamador para evitar que
    erros derrubem a aplicação.
    """
    with st.spinner("Analisando o diagrama..."):
        # 1. Pré-processamento (pode lançar InvalidImageError).
        image = preprocess_image(uploaded_file.getvalue())

        # 2. Detecção de componentes.
        detections = detector.detect(image)

        # 3. Nenhum componente detectado: informa e interrompe o fluxo (R6.6).
        if not detections:
            st.warning("Nenhum componente identificado.")
            return

        # 4. Extração de relacionamentos e 5. análise STRIDE.
        relationships = extract_relationships(detections)
        threats = stride_engine.analyze(detections, relationships)

        # 6. Imagem anotada (Requirement 7).
        annotated = draw_detections(image, detections)

        # 7. Relatório PDF.
        pdf_bytes = generate_report(detections, relationships, threats)

    # Exibição dos resultados (fora do spinner).
    st.image(
        annotated,
        caption="Componentes detectados",
        use_column_width=True
    )
    _render_components(detections)
    _render_threats(threats)

    st.download_button(
        label="Baixar relatório em PDF",
        data=pdf_bytes,
        file_name="relatorio_stride.pdf",
        mime="application/pdf",
    )


def main() -> None:
    """Renderiza a interface e orquestra o pipeline de análise."""
    st.set_page_config(page_title="STRIDE Diagram Analyzer", page_icon="🛡️")

    st.title("🛡️ STRIDE Diagram Analyzer")
    st.write(
        "Envie a imagem de um diagrama de arquitetura de software. A aplicação "
        "detecta os componentes arquiteturais, infere seus relacionamentos e "
        "gera um relatório de ameaças baseado na metodologia STRIDE."
    )

    uploaded_file = st.file_uploader(
        "Selecione uma imagem do diagrama",
        type=["png", "jpg", "jpeg"],
    )

    if uploaded_file is None:
        return

    # Todo o fluxo é protegido: qualquer falha (imagem inválida, carregamento do
    # modelo, inferência, etc.) é exibida via st.error sem derrubar o app (R6.5).
    try:
        detector = get_detector()
        stride_engine = get_stride_engine()
        _run_pipeline(uploaded_file, detector, stride_engine)
    except InvalidImageError as exc:
        st.error(f"Imagem inválida: {exc}")
    except Exception as exc:  # noqa: BLE001 - falha contida na camada de UI
        st.error(f"Ocorreu um erro durante a análise: {exc}")


if __name__ == "__main__":
    main()
