"""
GERADOR DE NOTAS FISCAIS FICTÍCIAS (NF-e) - Hogwarts 🧙
=======================================================

Este script PREPARA o exercício do vigia de notas:

  1. Apaga os resultados anteriores (entradas.csv, estoque.csv e as notas em entrada/ e processadas/)
  2. Cria 5 notas fiscais FICTÍCIAS (XML) na pasta notas_para_processar/

As notas seguem a estrutura de uma NF-e real (layout 4.00 da Receita Federal),
mas TODOS os dados são inventados: empresas, CNPJs, produtos e valores.

Como usar (no terminal, dentro desta pasta):
    python gerar_notas_fake.py

Pode rodar quantas vezes quiser: ele sempre recomeça do zero.
"""

import xml.etree.ElementTree as ET
from pathlib import Path

# ------------------------------------------------------------------
# PASTAS (todas ficam ao lado deste arquivo)
# ------------------------------------------------------------------
PASTA_BASE = Path(__file__).parent
PASTA_NOTAS = PASTA_BASE / "notas_para_processar"
PASTA_ENTRADA = PASTA_BASE / "entrada"
PASTA_PROCESSADAS = PASTA_BASE / "processadas"
ARQUIVO_ENTRADAS = PASTA_BASE / "entradas.csv"
ARQUIVO_ESTOQUE = PASTA_BASE / "estoque.csv"

# "Endereço" (namespace) oficial das tags da NF-e
NAMESPACE = "http://www.portalfiscal.inf.br/nfe"

# ------------------------------------------------------------------
# CATÁLOGO DE PRODUTOS: código -> (descrição, unidade, NCM)
# ------------------------------------------------------------------
PRODUTOS = {
    "ING-001": ("Raiz de Mandrágora", "UN", "12119090"),
    "ING-002": ("Bezoar", "UN", "05100010"),
    "ING-003": ("Raiz de Asfódelo em Pó", "G", "12119090"),
    "ING-004": ("Losna (Artemísia)", "G", "12119090"),
    "ING-005": ("Moscas Crisopídeas (cozidas 21 dias)", "G", "05119999"),
    "ING-006": ("Sanguessugas", "UN", "01069000"),
    "ING-007": ("Chifre de Bicórnio em Pó", "G", "05079000"),
    "ING-008": ("Sangue de Salamandra", "FR", "05119999"),
    "ING-009": ("Raiz de Valeriana", "G", "12119090"),
    "ING-010": ("Olho de Tritão", "UN", "05119999"),
    "EQP-001": ("Caldeirão de Estanho Tam. 2", "UN", "73239900"),
    "EQP-002": ("Frasco de Cristal 100 ml", "UN", "70139900"),
}

# ------------------------------------------------------------------
# FORNECEDORES FICTÍCIOS
# ------------------------------------------------------------------
FORNECEDORES = {
    "slug": {
        "CNPJ": "11222333000181",
        "xNome": "Botica Slug & Jiggers Ingredientes Mágicos Ltda",
        "xFant": "Slug & Jiggers",
        "xLgr": "Beco Diagonal", "nro": "93", "xBairro": "Centro Bruxo", "xMun": "Londres", "UF": "EX",
    },
    "floresta": {
        "CNPJ": "44555666000172",
        "xNome": "Ervas e Raízes da Floresta Proibida ME",
        "xFant": "Ervas da Floresta",
        "xLgr": "Trilha do Hagrid", "nro": "7", "xBairro": "Orla da Floresta", "xMun": "Hogsmeade", "UF": "EX",
    },
    "potage": {
        "CNPJ": "77888999000163",
        "xNome": "Caldeiraria Potage Equipamentos para Poções Ltda",
        "xFant": "Caldeirões Potage",
        "xLgr": "Beco Diagonal", "nro": "12", "xBairro": "Centro Bruxo", "xMun": "Londres", "UF": "EX",
    },
}

DESTINATARIO = {
    "CNPJ": "99000111000150",
    "xNome": "Escola de Magia e Bruxaria de Hogwarts - Depto. de Poções",
}

# ------------------------------------------------------------------
# AS 5 NOTAS: produtos se REPETEM entre notas (com preços diferentes)
# itens = lista de (código do produto, quantidade, valor unitário)
# ------------------------------------------------------------------
NOTAS = [
    {
        "numero": 1001, "data": "2026-11-02T09:15:00-03:00", "fornecedor": "slug",
        "itens": [
            ("ING-001", 20, 18.50),
            ("ING-002", 10, 45.00),
            ("ING-003", 500, 0.32),
            ("ING-008", 6, 27.90),
        ],
    },
    {
        "numero": 2087, "data": "2026-11-05T14:40:00-03:00", "fornecedor": "floresta",
        "itens": [
            ("ING-001", 15, 16.90),
            ("ING-004", 300, 0.45),
            ("ING-009", 400, 0.28),
            ("ING-005", 200, 0.75),
        ],
    },
    {
        "numero": 3350, "data": "2026-11-10T11:05:00-03:00", "fornecedor": "potage",
        "itens": [
            ("EQP-001", 12, 89.90),
            ("EQP-002", 60, 6.50),
        ],
    },
    {
        "numero": 1002, "data": "2026-11-17T10:20:00-03:00", "fornecedor": "slug",
        "itens": [
            ("ING-002", 8, 47.50),
            ("ING-006", 50, 3.20),
            ("ING-007", 150, 1.10),
            ("ING-010", 40, 2.40),
            ("ING-003", 300, 0.30),
        ],
    },
    {
        "numero": 2093, "data": "2026-11-24T16:55:00-03:00", "fornecedor": "floresta",
        "itens": [
            ("ING-001", 25, 17.40),
            ("ING-009", 300, 0.26),
            ("ING-005", 100, 0.80),
        ],
    },
]

# Alíquotas (%) usadas para calcular os impostos fictícios
ALIQ_ICMS = 18.00
ALIQ_IPI = 5.00      # só para equipamentos (EQP)
ALIQ_PIS = 1.65
ALIQ_COFINS = 7.60


def tag(pai, nome, texto=None):
    """Cria uma tag filha (com o namespace da NF-e) e, se informado, o texto dela."""
    elemento = ET.SubElement(pai, f"{{{NAMESPACE}}}{nome}")
    if texto is not None:
        elemento.text = str(texto)
    return elemento


def dinheiro(valor):
    """Formata como a NF-e: ponto decimal e 2 casas (ex.: 125.00)."""
    return f"{valor:.2f}"


def criar_nota(nota):
    """Monta a árvore XML de uma NF-e fictícia e devolve o elemento raiz."""
    fornecedor = FORNECEDORES[nota["fornecedor"]]

    raiz = ET.Element(f"{{{NAMESPACE}}}nfeProc", {"versao": "4.00"})
    nfe = tag(raiz, "NFe")
    chave = f"NFe99{nota['numero']:0>42}"[:47]
    inf = ET.SubElement(nfe, f"{{{NAMESPACE}}}infNFe", {"Id": chave, "versao": "4.00"})

    # --- identificação da nota ---
    ide = tag(inf, "ide")
    tag(ide, "natOp", "Venda de mercadoria")
    tag(ide, "mod", "55")
    tag(ide, "serie", "1")
    tag(ide, "nNF", nota["numero"])
    tag(ide, "dhEmi", nota["data"])
    tag(ide, "tpNF", "1")

    # --- emitente (quem vendeu) ---
    emit = tag(inf, "emit")
    tag(emit, "CNPJ", fornecedor["CNPJ"])
    tag(emit, "xNome", fornecedor["xNome"])
    tag(emit, "xFant", fornecedor["xFant"])
    ender = tag(emit, "enderEmit")
    for campo in ["xLgr", "nro", "xBairro", "xMun", "UF"]:
        tag(ender, campo, fornecedor[campo])

    # --- destinatário (quem comprou) ---
    dest = tag(inf, "dest")
    tag(dest, "CNPJ", DESTINATARIO["CNPJ"])
    tag(dest, "xNome", DESTINATARIO["xNome"])

    # --- itens (det) ---
    totais = {"vProd": 0, "vICMS": 0, "vIPI": 0, "vPIS": 0, "vCOFINS": 0}

    for numero_item, (codigo, quantidade, valor_unitario) in enumerate(nota["itens"], start=1):
        descricao, unidade, ncm = PRODUTOS[codigo]
        valor_total = round(quantidade * valor_unitario, 2)

        v_icms = round(valor_total * ALIQ_ICMS / 100, 2)
        v_ipi = round(valor_total * ALIQ_IPI / 100, 2) if codigo.startswith("EQP") else 0.0
        v_pis = round(valor_total * ALIQ_PIS / 100, 2)
        v_cofins = round(valor_total * ALIQ_COFINS / 100, 2)

        det = ET.SubElement(inf, f"{{{NAMESPACE}}}det", {"nItem": str(numero_item)})
        prod = tag(det, "prod")
        tag(prod, "cProd", codigo)
        tag(prod, "xProd", descricao)
        tag(prod, "NCM", ncm)
        tag(prod, "CFOP", "5102")
        tag(prod, "uCom", unidade)
        tag(prod, "qCom", f"{quantidade:.4f}")
        tag(prod, "vUnCom", f"{valor_unitario:.4f}")
        tag(prod, "vProd", dinheiro(valor_total))

        imposto = tag(det, "imposto")

        icms = tag(tag(imposto, "ICMS"), "ICMS00")
        tag(icms, "orig", "0")
        tag(icms, "CST", "00")
        tag(icms, "vBC", dinheiro(valor_total))
        tag(icms, "pICMS", dinheiro(ALIQ_ICMS))
        tag(icms, "vICMS", dinheiro(v_icms))

        if v_ipi > 0:
            ipi = tag(imposto, "IPI")
            tag(ipi, "cEnq", "999")
            ipi_trib = tag(ipi, "IPITrib")
            tag(ipi_trib, "CST", "50")
            tag(ipi_trib, "vBC", dinheiro(valor_total))
            tag(ipi_trib, "pIPI", dinheiro(ALIQ_IPI))
            tag(ipi_trib, "vIPI", dinheiro(v_ipi))

        pis = tag(tag(imposto, "PIS"), "PISAliq")
        tag(pis, "CST", "01")
        tag(pis, "vBC", dinheiro(valor_total))
        tag(pis, "pPIS", dinheiro(ALIQ_PIS))
        tag(pis, "vPIS", dinheiro(v_pis))

        cofins = tag(tag(imposto, "COFINS"), "COFINSAliq")
        tag(cofins, "CST", "01")
        tag(cofins, "vBC", dinheiro(valor_total))
        tag(cofins, "pCOFINS", dinheiro(ALIQ_COFINS))
        tag(cofins, "vCOFINS", dinheiro(v_cofins))

        totais["vProd"] += valor_total
        totais["vICMS"] += v_icms
        totais["vIPI"] += v_ipi
        totais["vPIS"] += v_pis
        totais["vCOFINS"] += v_cofins

    # --- totais da nota ---
    icms_tot = tag(tag(inf, "total"), "ICMSTot")
    tag(icms_tot, "vBC", dinheiro(totais["vProd"]))
    tag(icms_tot, "vICMS", dinheiro(totais["vICMS"]))
    tag(icms_tot, "vProd", dinheiro(totais["vProd"]))
    tag(icms_tot, "vIPI", dinheiro(totais["vIPI"]))
    tag(icms_tot, "vPIS", dinheiro(totais["vPIS"]))
    tag(icms_tot, "vCOFINS", dinheiro(totais["vCOFINS"]))
    tag(icms_tot, "vNF", dinheiro(totais["vProd"] + totais["vIPI"]))

    tag(tag(inf, "infAdic"), "infCpl", "NOTA FISCAL FICTICIA - MATERIAL DIDATICO - SEM VALOR FISCAL")

    return raiz


# ------------------------------------------------------------------
# EXECUÇÃO
# ------------------------------------------------------------------
ET.register_namespace("", NAMESPACE)   # grava as tags sem prefixo, como numa NF-e real

# 1) Cria as pastas (se ainda não existirem)
for pasta in [PASTA_NOTAS, PASTA_ENTRADA, PASTA_PROCESSADAS]:
    pasta.mkdir(exist_ok=True)

# 2) Apaga os resultados anteriores (recomeça do zero)
for pasta in [PASTA_NOTAS, PASTA_ENTRADA, PASTA_PROCESSADAS]:
    for arquivo in pasta.glob("*.xml"):
        arquivo.unlink()
for arquivo in [ARQUIVO_ENTRADAS, ARQUIVO_ESTOQUE]:
    if arquivo.exists():
        arquivo.unlink()

# 3) Gera as notas
for nota in NOTAS:
    raiz = criar_nota(nota)
    ET.indent(raiz, space="  ")
    nome_arquivo = f"NFe_{nota['numero']}_{nota['fornecedor']}.xml"
    ET.ElementTree(raiz).write(PASTA_NOTAS / nome_arquivo, encoding="UTF-8", xml_declaration=True)
    print(f"🧾 Nota criada: notas_para_processar/{nome_arquivo}")

print()
print("✅ Tudo pronto! (entradas.csv, estoque.csv, entrada/ e processadas/ foram zerados)")
print("   Agora rode:  python vigia_notas.py")
