# STRIDE Diagram Analyzer

Aplicação capaz de analisar imagens de **diagramas de arquitetura de software**, detectar automaticamente os componentes arquiteturais presentes, inferir seus relacionamentos e relacioná-los às ameaças da metodologia **STRIDE**, gerando um relatório em PDF com ameaças e contramedidas.

> Projeto de Tech Challenge — Pós-Graduação em Inteligência Artificial para Desenvolvedores (FIAP).

## Objetivo

Unir **Visão Computacional supervisionada** (detecção de componentes com YOLO) a uma **engine de regras determinística** (modelagem de ameaças STRIDE a partir de uma base de conhecimento), entregando uma ferramenta de apoio à análise de segurança na fase de projeto (*security by design*).

A documentação de arquitetura completa está em [`docs/architecture.md`](docs/architecture.md).

## Funcionalidades

- **Upload de diagrama**: envio de uma imagem (`png`, `jpg`, `jpeg`) pela interface web.
- **Detecção de componentes**: identificação automática dos componentes arquiteturais com modelo YOLO treinado, exibindo nome e confiança de cada detecção.
- **Inferência de relacionamentos**: extração geométrica de relacionamentos entre componentes (`contains` para trust boundaries e `connected_to` para componentes vizinhos), sem OCR ou IA adicional.
- **Análise STRIDE**: mapeamento de cada componente e relacionamento às ameaças STRIDE, com descrição e contramedidas, a partir de uma base de conhecimento em JSON.
- **Imagem anotada**: visualização do diagrama com as *bounding boxes* dos componentes detectados.
- **Relatório em PDF**: geração e download de um relatório completo (componentes, relacionamentos, ameaças e contramedidas).

## Pipeline de Análise

```
preprocess_image → Detector.detect → extract_relationships → StrideEngine.analyze → generate_report
```

## Estrutura de Diretórios

```
hackathon-stride/
├── app.py                          # Aplicação Streamlit (ponto de entrada)
├── requirements.txt                # Dependências do projeto
├── README.md                       # Este arquivo
├── RELATORIO.md                    # Relatório do projeto
├── .gitignore
│
├── docs/                           # Documentação
│   ├── architecture.md             # Arquitetura da solução
│   ├── dataset-collection-plan.md  # Plano de coleta do dataset
│   └── dataset-planning.md         # Planejamento do dataset
│
├── src/                            # Código-fonte da aplicação
│   ├── preprocessing.py            # Pré-processamento de imagem (OpenCV / Pillow)
│   ├── detector.py                 # Carregamento do modelo e inferência YOLO
│   ├── relationship_extractor.py   # Extração geométrica de relacionamentos
│   ├── stride_engine.py            # Engine de regras que consulta a base JSON
│   ├── report_generator.py         # Geração do relatório em PDF (ReportLab)
│   └── utils.py                    # Funções auxiliares (ex.: imagem anotada)
│
├── datasets/                       # Dados para o treinamento supervisionado
│   └── stride-architecture-components-v1/
│       ├── data.yaml               # Configuração do dataset (classes e splits)
│       ├── train/                  # Imagens e labels de treino
│       ├── val/                    # Imagens e labels de validação
│       └── test/                   # Imagens e labels de teste
│
├── training/                       # Pipeline de treinamento
│   ├── train.py                    # Treinamento do modelo YOLO
│   └── evaluate.py                 # Avaliação do modelo treinado
│
├── runs/                           # Saídas do treinamento (métricas, pesos, plots)
│
├── models/                         # Pesos do modelo treinado (best.pt)
│
├── data/                           # Base de conhecimento
│   └── stride_knowledge_base.json
│
├── results/                        # Artefatos finais de entrega
│
└── assets/
    ├── samples/                    # Imagens de exemplo para testes/demonstração
    └── reports/                    # Relatórios gerados
```

## Componentes Detectados

O modelo reconhece 32 classes de componentes arquiteturais, organizadas em categorias como atores (`actor_user`, `actor_admin`), borda (`edge_waf`, `edge_gateway`, `edge_cdn`), computação (`compute_service`, `compute_load_balancer`), dados (`data_database`, `data_cache`, `data_storage`), segurança (`security_identity_provider`, `security_key_management`), observabilidade (`obs_monitoring`, `obs_audit`) e trust boundaries (`boundary_vpc_or_vnet`, `boundary_subnet_public`, etc.). A lista completa está em [`datasets/stride-architecture-components-v1/data.yaml`](datasets/stride-architecture-components-v1/data.yaml).

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

A aplicação abrirá no navegador. Basta enviar a imagem de um diagrama de arquitetura para:

1. Visualizar os componentes detectados (imagem anotada + lista com confiança).
2. Consultar as ameaças STRIDE identificadas, agrupadas por componente, com contramedidas.
3. Baixar o relatório completo em PDF.

> A aplicação carrega os pesos do modelo a partir de `models/best.pt`. Certifique-se de que o arquivo esteja presente (gerado pelo pipeline de treinamento).

## Treinamento do Modelo (opcional)

O modelo já treinado é fornecido em `models/best.pt`. Para retreinar a partir do dataset anotado:

```bash
python training/train.py       # treina o modelo YOLO
python training/evaluate.py    # avalia o modelo treinado
```

As saídas (métricas, gráficos e pesos) são gravadas em `runs/`.

## Organização do Projeto

- **`src/`** concentra o código da aplicação, com um módulo por responsabilidade (pré-processamento, detecção, extração de relacionamentos, engine STRIDE, geração de relatório e utilidades).
- **`datasets/`** e **`training/`** isolam o ciclo de vida do modelo de IA (dados, anotação, treino e avaliação) do ciclo de vida da aplicação.
- **`data/`** guarda a base de conhecimento STRIDE, desacoplada do código.
- **`models/`** armazena os pesos do modelo treinado.
- **`docs/`** contém a documentação de arquitetura e o planejamento do dataset.

## Stack Principal

- **Streamlit** — interface web.
- **Ultralytics YOLO** — detecção supervisionada de componentes.
- **OpenCV / Pillow / NumPy** — processamento de imagem.
- **ReportLab** — geração do relatório em PDF.
- **PyYAML** — leitura da configuração do dataset.
