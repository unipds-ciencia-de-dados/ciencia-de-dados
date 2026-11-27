# 📚 Onde buscar dados: sugestões de estudo

**Live da Pós | Disciplina de Python | 26/11/2026**

Na live, buscamos dados de duas fontes: a **AwesomeAPI** (cotação do dólar) e o **Banco Central** (indicadores econômicos).
Mas existem **muitas outras** fontes públicas, várias delas ótimas para os **projetos da pós**.

Esta é uma lista para você explorar, praticar automações e encontrar dados para os seus projetos de Data Science.

---

## 🏷️ Legenda

| Símbolo | Significado |
|---|---|
| 🟢 | **Sem cadastro**: é só fazer o pedido e pronto |
| 🟡 | Precisa criar uma **conta ou chave (key) gratuita** |
| 🔵 | Existe um **pacote Python** que facilita o acesso |

---

## 🇧🇷 Economia e finanças (Brasil)

| Fonte | O que tem | Acesso |
|---|---|---|
| [**Banco Central: Dados Abertos**](https://dadosabertos.bcb.gov.br) | Além do que vimos na live: **Boletim Focus** (expectativas do mercado), PTAX, crédito, inadimplência | 🟢 🔵 `python-bcb` |
| [**IBGE SIDRA**](https://sidra.ibge.gov.br) | PIB, desemprego (PNAD), inflação por região, produção industrial | 🟢 🔵 `sidrapy` |
| [**Ipeadata**](http://www.ipeadata.gov.br) | Milhares de séries históricas de economia e sociedade | 🟢 🔵 `ipeadatapy` |
| [**CVM: Dados Abertos**](https://dados.cvm.gov.br) | Balanços das empresas da bolsa e dados diários de fundos de investimento | 🟢 (arquivos CSV) |
| [**Tesouro Transparente**](https://www.tesourotransparente.gov.br) | Histórico de preços e taxas do Tesouro Direto | 🟢 (CSV) |
| [**Yahoo Finance**](https://pypi.org/project/yfinance/) | Ações da B3 (ex.: `PETR4.SA`), índices e moedas | 🟢 🔵 `yfinance` ⚠️ não é oficial e às vezes quebra |

---

## 🏛️ Governo e sociedade (Brasil)

| Fonte | O que tem | Acesso |
|---|---|---|
| [**Base dos Dados**](https://basedosdados.org) | ⭐ Centenas de bases públicas brasileiras **já limpas e padronizadas** (RAIS, eleições, saúde, educação...) | 🟡 conta Google 🔵 `basedosdados` |
| [**BrasilAPI**](https://brasilapi.com.br) | CEP, CNPJ, feriados, bancos, taxas. Ótima para **treinar automações** | 🟢 |
| [**Câmara dos Deputados**](https://dadosabertos.camara.leg.br) | Votações, despesas dos deputados, proposições | 🟢 |
| [**TSE: Dados Abertos**](https://dadosabertos.tse.jus.br) | Resultados de eleições, candidatos, prestação de contas | 🟢 (CSV) |
| [**INEP: Microdados**](https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados) | ENEM, Censo Escolar, Censo da Educação Superior | 🟢 ⚠️ arquivos grandes |
| [**OpenDataSUS**](https://opendatasus.saude.gov.br) | Internações, vacinação, mortalidade | 🟢 🔵 `pysus` |
| [**Portal da Transparência**](https://api.portaldatransparencia.gov.br) | Gastos do governo federal, servidores, contratos | 🟡 |
| [**ANP: Dados Abertos**](https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos) | Preço semanal dos combustíveis por posto e cidade | 🟢 (CSV) |
| [**IBGE: API de serviços**](https://servicodados.ibge.gov.br/api/docs) | Localidades, malhas (mapas) e a divertida **API de Nomes** (frequência de nomes por década e estado) | 🟢 |
| [**dados.gov.br**](https://dados.gov.br) | Portal que reúne os dados abertos do governo federal | 🟢 |

---

## 🌍 Internacionais

| Fonte | O que tem | Acesso |
|---|---|---|
| [**Banco Mundial**](https://data.worldbank.org) | Indicadores de todos os países: PIB, educação, saúde, população | 🟢 🔵 `wbgapi` |
| [**FRED (Fed de St. Louis)**](https://fred.stlouisfed.org) | A maior base de séries econômicas dos EUA | 🟡 🔵 `fredapi` |
| [**Our World in Data**](https://ourworldindata.org) | Clima, energia, saúde, população, em CSVs prontos | 🟢 |
| [**Open-Meteo**](https://open-meteo.com) | Previsão e histórico do tempo para qualquer coordenada | 🟢 |
| [**USGS Earthquakes**](https://earthquake.usgs.gov/earthquakes/feed/) | Terremotos no mundo **em tempo real** (ótimo para mapas) | 🟢 |
| [**OpenAQ**](https://openaq.org) | Qualidade do ar no mundo | 🟡 |
| [**CoinGecko**](https://www.coingecko.com/en/api) | Criptomoedas: preços, volume, histórico | 🟢 |

---

## 🤖 Bases prontas para Machine Learning

| Fonte | Destaque | Acesso |
|---|---|---|
| [**Kaggle Datasets**](https://www.kaggle.com/datasets) | Milhares de datasets e competições | 🟡 (para baixar pela API) |
| [**UCI ML Repository**](https://archive.ics.uci.edu) | Bases clássicas de Machine Learning | 🟢 🔵 `ucimlrepo` |
| [**Hugging Face Datasets**](https://huggingface.co/datasets) | Textos, imagens e áudio | 🟢 🔵 `datasets` |

---

## 💡 Ideias de projetos

Algumas perguntas para começar:

- **Economia:** a expectativa do mercado (Boletim Focus) acerta a inflação de verdade? *(Banco Central)*
- **Investimentos:** quais fundos tiveram o melhor retorno ajustado ao risco nos últimos 5 anos? *(CVM)*
- **Educação:** quais fatores mais influenciam a nota do ENEM? *(INEP / Base dos Dados)*
- **Saúde:** dá para prever picos de internação por doenças respiratórias? *(OpenDataSUS + Open-Meteo)*
- **Combustíveis:** o preço da gasolina acompanha o dólar? Com quanto tempo de atraso? *(ANP + Banco Central)*
- **Política:** como os gastos dos deputados variam por partido e por estado? *(Câmara dos Deputados)*
- **Clima:** como evoluíram a temperatura e as chuvas na sua cidade nos últimos 30 anos? *(Open-Meteo)*

> 🔗 **Projetos mais ricos cruzam fontes diferentes!** Por exemplo: combustível (ANP) × dólar (Banco Central) × inflação (IBGE).

---

## 🚀 Primeiro passo: um exemplo para copiar e adaptar

Mesmo esquema da live: `requests` busca os dados → `pandas` organiza em tabela.
Aqui, os **feriados nacionais de 2027** pela BrasilAPI:

```python
# [MÓDULO] importamos as "caixas de ferramentas"
import requests
import pandas as pd

# [VARIÁVEL] endereço da API (troque o ano para testar)
url = "https://brasilapi.com.br/api/feriados/v1/2027"

# [FUNÇÃO] requests.get() faz o pedido à API (com argumentos nomeados, como na live)
resposta = requests.get(url=url, timeout=30)

# [ATRIBUTO] status_code -> 200 = deu certo
print("Código da resposta:", resposta.status_code)

# [MÉTODO] .json() converte a resposta em uma lista de dicionários
dados = resposta.json()

# [OBJETO] DataFrame do pandas criado a partir da lista
feriados = pd.DataFrame(data=dados)
feriados
```

**Desafio:** use um **loop** para buscar os feriados de 2020 a 2030 e descubra em qual ano caíram **mais feriados em dia útil**. 😉

---

## ✅ Boas práticas ao buscar dados

1. **Comece por fontes 🟢.** Sem chave e sem login, o seu primeiro projeto tem menos chance de travar.
2. **Salve os dados num arquivo local** (`.csv` ou `.parquet`) e trabalhe em cima dele.
   Não dependa da API toda vez que rodar o projeto: a do Banco Central, por exemplo, às vezes falha e devolve o **código 304** (resposta vazia).
3. **Leia a documentação da API:** quantos registros ela devolve, quantos pedidos por minuto aceita e qual é a licença de uso.
4. **Use `timeout`** em todo `requests.get()`, para o código não ficar "pendurado" para sempre.
5. **Nunca coloque chaves (keys) direto no código** que vai para o GitHub. Guarde em variáveis de ambiente ou em um arquivo `.env`.
6. **Pacotes prontos ajudam** (`python-bcb`, `sidrapy`, `basedosdados`...), mas fazer o pedido "na mão" com `requests` pelo menos uma vez ensina **muito** sobre como as APIs funcionam.

> ⚠️ APIs mudam com o tempo: endereços, limites e regras podem ser alterados. Se algo não funcionar, consulte a documentação oficial da fonte.
