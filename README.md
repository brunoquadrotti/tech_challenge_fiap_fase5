# STRIDE Diagram Analyzer

Aplicação capaz de analisar imagens de **diagramas de arquitetura de software**, detectar automaticamente os componentes arquiteturais presentes e relacioná-los às ameaças da metodologia **STRIDE**, gerando um relatório em PDF com ameaças e contramedidas.

> Projeto de Hackathon — Pós-Graduação em Inteligência Artificial para Desenvolvedores (FIAP).

## Objetivo

Unir **Visão Computacional supervisionada** (detecção de componentes com YOLOv8) a uma **engine de regras determinística** (modelagem de ameaças STRIDE a partir de uma base de conhecimento), entregando uma ferramenta de apoio à análise de segurança na fase de projeto (*security by design*).

A documentação de arquitetura completa está em [`docs/architecture.md`](docs/architecture.md).

## Estrutura de Diretórios

```
hackathon-stride/
├── app.py                      # Aplicação Streamlit (ponto de entrada)
├── requirements.txt            # Dependências do projeto
├── README.md                   # Este arquivo
├── .gitignore
│
├── docs/                       # Documentação (arquitetura)
│
├── src/                        # Código-fonte da aplicação
│   ├── preprocessing.py        # Pré-processamento de imagem (OpenCV / Pillow)
│   ├── detector.py             # Carregamento do modelo e inferência YOLOv8
│   ├── stride_engine.py        # Engine de regras que consulta a base JSON
│   ├── report_generator.py     # Geração do relatório em PDF (ReportLab)
│   └── utils.py                # Funções auxiliares compartilhadas
│
├── dataset/                    # Dados para o treinamento supervisionado
│   ├── images/                 # Imagens dos diagramas
│   ├── labels/                 # Anotações no formato YOLO
│   └── data.yaml               # Configuração do dataset (classes e splits)
│
├── training/                   # Pipeline de treinamento
│   ├── train.py                # Treinamento do modelo YOLOv8
│   └── evaluate.py             # Avaliação do modelo treinado
│
├── models/                     # Pesos do modelo treinado (best.pt)
│
├── data/                       # Base de conhecimento
│   └── stride_knowledge_base.json
│
└── assets/
    └── samples/                # Imagens de exemplo para testes/demonstração
```

## Pré-requisitos

- **Python 3.10**
- **pip** e **venv** disponíveis

## Criação do Ambiente Virtual

Linux / macOS:

```bash
python3.10 -m venv .venv
source .venv/bin/activate
```

Windows (PowerShell):

```powershell
py -3.10 -m venv .venv
.venv\Scripts\Activate.ps1
```

## Instalação das Dependências

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## Execução da Aplicação

Com o ambiente virtual ativado:

```bash
streamlit run app.py
```

A aplicação abrirá no navegador. Nesta etapa inicial, é possível enviar uma imagem e receber a confirmação de recebimento; o processamento será adicionado nas próximas etapas.

## Organização do Projeto

- **`src/`** concentra o código da aplicação, com um módulo por responsabilidade (pré-processamento, detecção, engine STRIDE, geração de relatório e utilidades).
- **`dataset/`** e **`training/`** isolam o ciclo de vida do modelo de IA (dados, anotação, treino e avaliação) do ciclo de vida da aplicação.
- **`data/`** guarda a base de conhecimento STRIDE, desacoplada do código.
- **`models/`** armazena os pesos do modelo treinado.
- **`docs/`** contém a documentação de arquitetura.

> Estado atual: **fundação do projeto** — estrutura, ambiente e interface mínima. As lógicas de treinamento, inferência, processamento de imagem, engine STRIDE e geração de PDF ainda não foram implementadas.
