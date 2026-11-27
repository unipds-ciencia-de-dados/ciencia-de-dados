# Live 26/11/2026: Automações em Python

**Disciplina de Python | Pós em Data Science e IA**

Três automações simples, escritas para quem está aprendendo Python. O código é quase todo **sequencial** (de cima para baixo), com um pouco de **função** e **classe**. Todos os comentários trazem **etiquetas** que mostram cada conceito: `[MÓDULO]`, `[FUNÇÃO]`, `[MÉTODO]`, `[ATRIBUTO]`, `[CLASSE]`, `[OBJETO]`, `[LOOP]`, `[CONDICIONAL]`...

## Estrutura

```
26-11-2026/
├── buscando-dados/
│   ├── 001-live-automacao-cotacao-dolar.ipynb          # 1ª automação
│   ├── 002-live-automacao-indicadores-economicos.ipynb # 2ª automação
│   └── fontes-de-dados-para-estudo.md                  # sugestões de APIs e bases para os alunos
│
└── notas-fiscais/
    ├── vigia_notas.py           # 3ª automação (roda no terminal)
    └── gerar_notas_fake.py      # gera as 5 NF-e fictícias e recomeça do zero
```

> As pastas `notas_para_processar/`, `entrada/` e `processadas/` e os arquivos `entradas.csv` e `estoque.csv` são **criados pelos scripts** e não ficam no Git.

## Preparação do ambiente

```bash
pip install requests pandas matplotlib jupyter watchdog
```

## As automações

### 1. Cotação do dólar: `buscando-dados/001-...ipynb`
Busca a cotação atual do dólar, do euro, da libra e do bitcoin na [AwesomeAPI](https://docs.awesomeapi.com.br/) (gratuita, sem cadastro). Depois monta o histórico dos últimos 15 dias (quase sempre úteis), desenha um gráfico e salva CSV e PNG.

**Conceitos:** módulos, dicionário, lista, f-string, **classe `Cotacao`** (só guarda dados), **função `buscar_cotacao()`**, loop.

### 2. Indicadores econômicos: `buscando-dados/002-...ipynb`
Consulta no [SGS do Banco Central](https://www3.bcb.gov.br/sgspub) a Selic, o CDI, o IPCA, o IGP-M e o dólar PTAX. Monta um painel, calcula o juro real e desenha o gráfico de **juros × inflação** dos últimos 2 anos.

**Conceitos:** **classe `Indicador`** (guarda dados **e** busca: a busca virou método), lista de objetos, `timedelta`, `strptime`, tratamento de falhas da API (`range(3)` + `break`).

### 3. Vigia de notas fiscais: `notas-fiscais/vigia_notas.py`
Usa a biblioteca `watchdog` para **vigiar a pasta `entrada/`**. Quando chega uma NF-e (XML), o programa extrai os produtos, as quantidades, os valores e os impostos, acrescenta os itens no histórico `entradas.csv` (uma linha por item de cada nota) e grava o **estoque atual** somado em `estoque.csv` (uma linha por produto), que também aparece na tela. O tema é a compra de ingredientes para as aulas de Poções de Hogwarts. 🧙

**Conceitos:** **herança** (`class VigiaDeNotas(FileSystemEventHandler)`), leitura de XML com namespace, `pathlib`, `shutil`, `while True` + `try/except`, `groupby` no pandas.

> ⚠️ As notas fiscais **não estão no repositório**. Rode sempre o `gerar_notas_fake.py` primeiro: ele cria as pastas e as 5 notas.

```bash
cd notas-fiscais
python gerar_notas_fake.py   # 1) gera as notas e zera entradas.csv, estoque.csv, entrada/ e processadas/
python vigia_notas.py        # 2) liga o vigia (Ctrl + C para parar)
                             # 3) arraste as notas de notas_para_processar/ para entrada/
```

## Sugestão de estudo

1. **Dólar:** rode célula por célula e leia a legenda das etiquetas no começo do notebook.
2. **Indicadores:** compare as duas classes (`Cotacao` × `Indicador`) e veja como o código lida com as falhas da API.
3. **Notas fiscais:** deixe o terminal e a pasta `notas-fiscais/` abertos lado a lado. Arraste as notas para `entrada/` nesta ordem: `1001 → 2087 → 3350 → 1002 → 2093`. Repare que a Raiz de Mandrágora vai de 20 → 35 → 60 unidades.
   - Arraste **uma nota por vez** primeiro e depois **várias de uma vez**.
   - Teste: copie de novo uma nota já processada para `entrada/`. A automação avisa que **a nota já foi lançada** e não soma em dobro.
4. **Próximos passos:** o `fontes-de-dados-para-estudo.md` traz sugestões de fontes de dados e de projetos.

## ⚠️ Atenção

- **API do Banco Central:** às vezes responde com o código **304** (resposta vazia). A classe `Indicador` tenta de novo sozinha, mas o **Passo 2** do notebook 002 (o pedido simples, sem classe) não tenta. Se acontecer, espere um pouco e rode a célula de novo, ou siga para o Passo 4.
- **Cotações** ficam paradas fora do horário de mercado.
- **O `gerar_notas_fake.py` apaga** o histórico (`entradas.csv`), o estoque (`estoque.csv`) e as notas já processadas. Rode quando quiser recomeçar do zero.
- Os arquivos gerados (CSV, PNG, `entradas.csv`, `estoque.csv`, `notas_para_processar/`, `entrada/` e `processadas/`) estão no `.gitignore`.
