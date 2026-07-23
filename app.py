"""
Aplicação Streamlit — Detecção de Componentes Arquiteturais e Modelagem STRIDE.

Ponto de entrada da aplicação. Nesta etapa (Etapa 2 - Fundação do projeto)
a interface é intencionalmente mínima: exibe título, descrição e um componente
de upload de imagem. Nenhum processamento é realizado.

O fluxo completo (pré-processamento, detecção YOLOv8, engine STRIDE e geração
de relatório) será integrado nas próximas etapas.
"""

import streamlit as st


def main() -> None:
    """Renderiza a interface mínima da aplicação."""
    st.set_page_config(page_title="STRIDE Diagram Analyzer", page_icon="🛡️")

    st.title("🛡️ STRIDE Diagram Analyzer")
    st.write(
        "Envie a imagem de um diagrama de arquitetura de software. "
        "Nas próximas etapas, a aplicação detectará os componentes arquiteturais "
        "e gerará um relatório de ameaças baseado na metodologia STRIDE."
    )

    uploaded_file = st.file_uploader(
        "Selecione uma imagem do diagrama",
        type=["png", "jpg", "jpeg"],
    )

    if uploaded_file is not None:
        st.success("Imagem recebida com sucesso.")


if __name__ == "__main__":
    main()
