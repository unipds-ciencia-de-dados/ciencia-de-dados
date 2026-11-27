"""
🧙 AUTOMAÇÃO: VIGIA DE NOTAS FISCAIS DO ESTOQUE DE POÇÕES DE HOGWARTS
=====================================================================

O que este programa faz:
  1. Fica VIGIANDO a pasta "entrada/".
  2. Quando uma nota fiscal (arquivo .xml) chega nela, o programa:
       - lê a nota e extrai os produtos, quantidades, valores e impostos;
       - acrescenta esses produtos no HISTÓRICO "entradas.csv" (uma linha por item de cada nota);
       - mostra na tela os produtos que entraram;
       - soma todas as notas e grava o ESTOQUE ATUAL em "estoque.csv" (uma linha por produto);
       - mostra o estoque atual na tela;
       - move a nota para a pasta "processadas/".
  3. Continua vigiando até você apertar Ctrl + C.

Como rodar (no terminal, dentro desta pasta):
    python vigia_notas.py

Depois, arraste (ou copie) as notas de "notas_para_processar/" para "entrada/".

Pacote necessário (instalar uma vez):
    pip install watchdog pandas

🏷️ LEGENDA DOS COMENTÁRIOS
  [MÓDULO]       caixa de ferramentas pronta, trazida com import
  [VARIÁVEL]     "caixinha" com nome que guarda um valor
  [LISTA]        coleção ordenada de itens:            [item1, item2]
  [DICIONÁRIO]   coleção de pares chave -> valor:      {"chave": valor}
  [FUNÇÃO]       bloco de código com nome:             def nome():   /   nome()
  [MÉTODO]       função que pertence a um objeto:      objeto.metodo()   (COM parênteses)
  [ATRIBUTO]     informação guardada em um objeto:     objeto.atributo   (SEM parênteses)
  [CLASSE]       molde para criar objetos:             class Nome:
  [HERANÇA]      classe que "herda" de outra:          class Filha(Mae):
  [OBJETO]       algo criado a partir de uma classe:   variavel = Classe()
  [LOOP]         repetição:                            for ... in ...:   /   while ...:
  [CONDICIONAL]  decisão:                              if ... else ...
"""

# =====================================================================
# PASSO 1 - IMPORTAR OS MÓDULOS
# =====================================================================

# [MÓDULO] time -> funções de tempo (vamos usar para "esperar" alguns segundos)
import time

# [MÓDULO] shutil -> operações com arquivos, como MOVER de uma pasta para outra
import shutil

# [MÓDULO] xml.etree.ElementTree -> lê arquivos XML (já vem com o Python). Apelido: ET
import xml.etree.ElementTree as ET

# [MÓDULO] pathlib -> trabalha com caminhos de pastas e arquivos.
# Path é uma [CLASSE] que representa um caminho (ex.: "entrada/NFe_1001.xml")
from pathlib import Path

# [MÓDULO] pandas -> tabelas (DataFrames). Apelido: pd
import pandas as pd

# [MÓDULO] watchdog -> o "vigia" de pastas (pip install watchdog)
#   Observer               -> [CLASSE] que fica observando a pasta
#   FileSystemEventHandler -> [CLASSE] que diz O QUE FAZER quando algo acontece na pasta
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


# =====================================================================
# PASSO 2 - CONFIGURAÇÕES
# =====================================================================

# [ATRIBUTO] __file__ é o caminho deste arquivo .py, e .parent é a pasta onde ele está.
# Assim, o programa funciona de qualquer lugar de onde for rodado.
PASTA_BASE = Path(__file__).parent

# [VARIÁVEL] o operador "/" junta pedaços de caminho: PASTA_BASE / "entrada"
PASTA_ENTRADA = PASTA_BASE / "entrada"
PASTA_PROCESSADAS = PASTA_BASE / "processadas"
# entradas.csv -> HISTÓRICO: cada item de cada nota, uma linha (só cresce, nunca soma)
# estoque.csv  -> ESTOQUE ATUAL: uma linha por produto, com tudo somado (reescrito a cada nota)
ARQUIVO_ENTRADAS = PASTA_BASE / "entradas.csv"
ARQUIVO_ESTOQUE = PASTA_BASE / "estoque.csv"

# [DICIONÁRIO] "sobrenome" das tags da NF-e (namespace).
# Toda tag da nota fiscal pertence a este endereço oficial da Receita Federal,
# então precisamos informá-lo para o Python encontrar as tags.
NS = {"nfe": "http://www.portalfiscal.inf.br/nfe"}

# [MÉTODO] .set_option() deixa o pandas mostrar todas as colunas no terminal, sem cortar
pd.set_option("display.width", 200)
pd.set_option("display.max_columns", None)


# =====================================================================
# PASSO 3 - FUNÇÕES QUE LEEM A NOTA FISCAL
# =====================================================================

# [FUNÇÃO] procura uma tag e devolve o TEXTO dela.
# Parâmetros: "elemento" (onde procurar) e "caminho" (qual tag procurar)
def ler_texto(elemento, caminho):
    # [MÉTODO] .find() procura a tag. ".//" quer dizer "em qualquer nível abaixo"
    tag = elemento.find(caminho, NS)

    # [CONDICIONAL] se a tag não existir (ex.: produto sem IPI), devolve texto vazio
    if tag is None:
        return ""
    # [ATRIBUTO] .text é o conteúdo da tag. Ex.: <xProd>Bezoar</xProd> -> "Bezoar"
    return tag.text


# [FUNÇÃO] igual à anterior, mas devolve um NÚMERO (float). Se não existir, devolve 0
def ler_numero(elemento, caminho):
    texto = ler_texto(elemento, caminho)
    if texto == "":
        return 0.0
    return float(texto)   # [FUNÇÃO] float() converte texto em número decimal


# [FUNÇÃO] lê UMA nota fiscal e devolve uma [LISTA] de [DICIONÁRIOS], um por produto
def extrair_itens(caminho_xml):

    # [FUNÇÃO] ET.parse() abre e lê o arquivo XML
    # [MÉTODO] .getroot() pega a tag "raiz", a primeira de todas (<nfeProc>)
    arvore = ET.parse(caminho_xml)
    raiz = arvore.getroot()

    # Dados do CABEÇALHO da nota (valem para todos os produtos)
    numero_nota = ler_texto(raiz, ".//nfe:ide/nfe:nNF")
    data_emissao = ler_texto(raiz, ".//nfe:ide/nfe:dhEmi")[:10]   # [:10] pega só "2026-11-02"
    fornecedor = ler_texto(raiz, ".//nfe:emit/nfe:xFant")

    itens = []   # [LISTA] vazia; vamos enchendo no loop

    # [LOOP] cada <det> da nota é UM produto.
    # [MÉTODO] .findall() encontra TODAS as tags <det> (já o .find() pegava só a primeira)
    for det in raiz.findall(".//nfe:det", NS):

        # [DICIONÁRIO] cada chave vai virar uma COLUNA do CSV
        item = {
            "numero_nota": numero_nota,
            "data_emissao": data_emissao,
            "fornecedor": fornecedor,
            "codigo": ler_texto(det, ".//nfe:cProd"),
            "produto": ler_texto(det, ".//nfe:xProd"),
            "unidade": ler_texto(det, ".//nfe:uCom"),
            "quantidade": ler_numero(det, ".//nfe:qCom"),
            "valor_unitario": ler_numero(det, ".//nfe:vUnCom"),
            "valor_total": ler_numero(det, ".//nfe:vProd"),
            "icms": ler_numero(det, ".//nfe:vICMS"),
            "ipi": ler_numero(det, ".//nfe:vIPI"),
            "pis": ler_numero(det, ".//nfe:vPIS"),
            "cofins": ler_numero(det, ".//nfe:vCOFINS"),
        }

        # [MÉTODO] .append() adiciona o dicionário no fim da lista
        itens.append(item)

    return itens


# =====================================================================
# PASSO 4 - FUNÇÕES QUE GRAVAM E MOSTRAM O ESTOQUE
# =====================================================================

# [FUNÇÃO] verifica se uma nota já foi lançada no histórico (para não somar em dobro!)
# ⚠️ LIMITAÇÃO: comparamos só o NÚMERO da nota. Na vida real, dois fornecedores
# diferentes podem emitir notas com o mesmo número, e a segunda seria ignorada
# por engano. Um sistema de verdade compararia número + fornecedor (CNPJ)
# ou a chave de acesso da NF-e, que é única. Para este exemplo, basta o número.
def nota_ja_lancada(numero_nota):
    # [MÉTODO] .exists() -> True se o arquivo existe, False se não existe
    if not ARQUIVO_ENTRADAS.exists():
        return False

    # dtype=str lê tudo como texto, para comparar "1001" com "1001"
    tabela = pd.read_csv(ARQUIVO_ENTRADAS, dtype=str)

    # [ATRIBUTO] .values são os valores da coluna. "in" pergunta: está lá dentro?
    return numero_nota in tabela["numero_nota"].values


# [FUNÇÃO] acrescenta os itens no final do HISTÓRICO (entradas.csv)
def gravar_entradas(itens):
    tabela_nova = pd.DataFrame(itens)   # [OBJETO] DataFrame criado a partir da lista

    # mode="a" -> "append": ACRESCENTA no fim do arquivo, sem apagar o que já existe.
    # header -> só escreve o cabeçalho (nomes das colunas) se o arquivo ainda NÃO existe.
    tabela_nova.to_csv(
        ARQUIVO_ENTRADAS,
        mode="a",
        header=not ARQUIVO_ENTRADAS.exists(),
        index=False,
    )
    return tabela_nova


# [FUNÇÃO] lê o HISTÓRICO inteiro, SOMA as quantidades de cada produto,
# grava o resultado em estoque.csv e mostra na tela
def atualizar_estoque():
    tabela = pd.read_csv(ARQUIVO_ENTRADAS)

    # Custo de cada item = valor dos produtos + IPI.
    # Hogwarts compra para USAR (não para revender), então o IPI pago também é custo.
    # Nova coluna: o pandas faz a conta linha por linha, de uma vez só.
    tabela["custo_total"] = tabela["valor_total"] + tabela["ipi"]

    # [MÉTODO] .groupby() agrupa as linhas do mesmo produto
    # e .sum() soma a quantidade e o custo de todas as notas
    estoque = tabela.groupby(["codigo", "produto", "unidade"], as_index=False)[
        ["quantidade", "custo_total"]
    ].sum()

    # Custo médio = quanto pagamos, em média, por unidade (considerando todas as compras)
    estoque["custo_medio"] = (estoque["custo_total"] / estoque["quantidade"]).round(2)

    # Sem mode="a": o arquivo é REESCRITO do zero, sempre com o estoque somado e atualizado
    estoque.to_csv(ARQUIVO_ESTOQUE, index=False)

    # [FUNÇÃO] len() conta as linhas; [MÉTODO] .nunique() conta quantas notas diferentes existem
    print(f"📦 ESTOQUE ATUAL | {len(estoque)} produtos | {tabela['numero_nota'].nunique()} notas lançadas")
    # [MÉTODO] .to_string() transforma a tabela em texto bonito para o terminal
    print(estoque.to_string(index=False))
    print(f"💰 Valor total em estoque: R$ {estoque['custo_total'].sum():.2f}")


# =====================================================================
# PASSO 5 - A FUNÇÃO PRINCIPAL: PROCESSAR UMA NOTA
# =====================================================================

# [FUNÇÃO] junta tudo: ler a nota -> gravar no histórico -> atualizar o estoque -> mover para processadas
def processar_nota(caminho_xml):

    # Espera 1 segundo: às vezes o arquivo "chega" antes de terminar de ser copiado
    time.sleep(1)

    # [CONDICIONAL] se o arquivo não existe mais (já foi processado), não faz nada.
    # "return False" avisa a quem chamou que NENHUMA nota foi tratada.
    if not caminho_xml.exists():
        return False

    print()
    print("=" * 100)
    # [ATRIBUTO] .name é só o nome do arquivo, sem as pastas
    print(f"🦉 CORUJA CHEGOU! Nova nota fiscal: {caminho_xml.name}")
    print("=" * 100)

    itens = extrair_itens(caminho_xml)
    numero_nota = itens[0]["numero_nota"]   # [LISTA] posição 0 + [DICIONÁRIO] chave
    destino = PASTA_PROCESSADAS / caminho_xml.name

    # [CONDICIONAL] nota repetida? Avisa e NÃO soma de novo no estoque
    if nota_ja_lancada(numero_nota):
        print(f"⚠️  A nota {numero_nota} JÁ FOI LANÇADA antes. Ignorando para não duplicar o estoque.")
        shutil.move(caminho_xml, destino)   # [FUNÇÃO] move o arquivo mesmo assim
        return True

    tabela_nova = gravar_entradas(itens)

    print(f"Fornecedor: {itens[0]['fornecedor']}  |  Nota nº {numero_nota}  |  Emissão: {itens[0]['data_emissao']}")
    print()
    print("🧪 PRODUTOS QUE ENTRARAM (gravados em entradas.csv):")
    print(tabela_nova.drop(columns=["numero_nota", "data_emissao", "fornecedor"]).to_string(index=False))
    print()

    # Totais desta nota
    # Total da nota = produtos + IPI (o IPI é cobrado "por fora", somado ao preço).
    # ICMS, PIS e COFINS já estão DENTRO do preço dos produtos, por isso não somam de novo.
    total_produtos = tabela_nova["valor_total"].sum()
    total_nota = total_produtos + tabela_nova["ipi"].sum()
    impostos = tabela_nova[["icms", "ipi", "pis", "cofins"]].sum().sum()
    print(f"🧾 Total dos produtos: R$ {total_produtos:.2f}  |  Total da nota: R$ {total_nota:.2f}  |  Impostos: R$ {impostos:.2f}")
    print()

    atualizar_estoque()

    # [FUNÇÃO] shutil.move() move a nota para a pasta "processadas"
    shutil.move(caminho_xml, destino)
    print()
    print(f"📁 Nota movida para: processadas/{caminho_xml.name}")
    return True   # avisa a quem chamou que a nota foi tratada


# =====================================================================
# PASSO 6 - A CLASSE QUE "REAGE" QUANDO UM ARQUIVO CHEGA
# =====================================================================

# [CLASSE] + [HERANÇA]: a nossa classe HERDA de FileSystemEventHandler.
# Ou seja, ela ganha "de presente" tudo que a classe do watchdog já sabe fazer,
# e nós só escrevemos o que queremos de DIFERENTE.
class VigiaDeNotas(FileSystemEventHandler):

    # [MÉTODO] on_created é chamado AUTOMATICAMENTE pelo watchdog
    # sempre que um arquivo novo aparece na pasta (copiado OU arrastado).
    # "evento" é um [OBJETO] com as informações do que aconteceu.
    def on_created(self, evento):

        # [ATRIBUTO] evento.src_path é o caminho do arquivo que chegou
        caminho = Path(evento.src_path)

        # [CONDICIONAL] só nos interessam ARQUIVOS (não pastas) terminados em .xml
        # [ATRIBUTO] evento.is_directory -> True se for uma pasta
        # [ATRIBUTO] caminho.suffix -> a extensão do arquivo (ex.: ".xml")
        # [MÉTODO] .lower() deixa em minúsculas (assim ".XML" também funciona)
        if evento.is_directory or caminho.suffix.lower() != ".xml":
            return

        # processar_nota() devolve True se tratou uma nota, ou False se não havia nada
        # (às vezes o watchdog avisa de novo sobre um arquivo que já foi movido).
        tratou = processar_nota(caminho)

        # Avisa que voltou a vigiar. Fica AQUI (e não dentro de processar_nota)
        # porque as notas processadas antes de ligar o vigia (Passo 7) não devem dizer isso.
        if tratou:
            print()
            print("👀 Vigiando a pasta... (Ctrl + C para parar)")


# =====================================================================
# PASSO 7 - LIGAR O VIGIA (o programa começa a rodar aqui)
# =====================================================================

# [MÉTODO] .mkdir() cria as pastas. exist_ok=True -> não dá erro se já existirem
PASTA_ENTRADA.mkdir(exist_ok=True)
PASTA_PROCESSADAS.mkdir(exist_ok=True)

print("🏰 Vigia de Notas Fiscais | Estoque de Poções de Hogwarts")
print(f"📂 Vigiando a pasta: {PASTA_ENTRADA}")
print()

# [LOOP] antes de começar a vigiar, processa notas que já estavam esperando na pasta
# [MÉTODO] .glob("*.xml") lista os arquivos que terminam em .xml
# [FUNÇÃO] sorted() coloca em ordem alfabética
for nota in sorted(PASTA_ENTRADA.glob("*.xml")):
    processar_nota(nota)

# [OBJETO] criamos o vigia (Observer) e o "reator" (a nossa classe VigiaDeNotas)
observador = Observer()
reator = VigiaDeNotas()

# [MÉTODO] .schedule() diz ao observador: "vigie ESTA pasta e avise ESTE reator"
observador.schedule(reator, str(PASTA_ENTRADA), recursive=False)

# [MÉTODO] .start() liga o vigia (ele roda "em paralelo", em segundo plano)
observador.start()
print("👀 Vigiando a pasta... arraste uma nota fiscal para 'entrada/' (Ctrl + C para parar)")

# [LOOP] while True = repete PARA SEMPRE, mantendo o programa vivo.
# try/except: quando você aperta Ctrl + C, o Python gera um "KeyboardInterrupt",
# que nós capturamos para desligar o vigia com educação.
try:
    while True:
        time.sleep(1)   # [FUNÇÃO] espera 1 segundo e repete
except KeyboardInterrupt:
    print()
    print("🛑 Desligando o vigia... Malfeito feito! ✨")
    observador.stop()   # [MÉTODO] desliga o vigia

observador.join()   # [MÉTODO] espera o vigia terminar direitinho antes de fechar o programa
