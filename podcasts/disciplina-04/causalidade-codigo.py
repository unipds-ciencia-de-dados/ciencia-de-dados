# Podcast: Shorts não vendem sorvete: correlação, causalidade e confundimento
# Versão em Python
#
# - Shorts e sorvete: lê os mesmos 200 dias usados na aula (sorvete.csv,
#   gerado no R), então os números são idênticos aos do PDF.
# - Tela grande: simula com o gerador do numpy. Os números não são idênticos
#   aos do PDF (que foram gerados no R), mas ficam muito próximos, porque a
#   população é grande (100 mil pessoas).

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


# =============================================================================
# Uso de shorts vs. compra de sorvetes (slides 13 a 24)
# Correlação espúria: shorts NÃO afeta sorvete; os dois dependem da temperatura
#
#          temperatura
#          /         \
#     uso_shorts   compra_sorvetes
# =============================================================================

# Os dados foram simulados assim (200 dias):
#
#   temperatura     = uniforme entre 10 e 35 graus
#   uso_shorts      = % de pessoas de shorts no dia: ~0% abaixo de 15 graus,
#                     cresce até ~100% em 35 graus (+ ruído normal, desvio 5)
#   compra_sorvetes = 5 + 0,5·temperatura (+ ruído normal, desvio 1)
#
# Repare: uso_shorts NÃO entra na fórmula de compra_sorvetes.
#
# Em Python, a mesma simulação seria:
#
#   rng = np.random.default_rng(123)
#   n = 200
#   temperatura = rng.uniform(10, 35, size=n)
#   uso_shorts = np.clip((temperatura - 15) / 20, 0, 1) * 100 + rng.normal(0, 5, size=n)
#   uso_shorts = np.clip(uso_shorts, 0, 100)
#   compra_sorvetes = 5 + 0.5 * temperatura + rng.normal(0, 1, size=n)
#
# Mas, para os números baterem com a aula, lemos os dados gerados no R:

dados = pd.read_csv("sorvete.csv")
n = len(dados)

# [Slide 13] Primeiros dias: 7,39 / 12,88 ; 74,82 / 19,10 ; 24,89 / 14,17
# (no slide, 7,395 aparece truncado como 7,39)
print(dados[["dia", "uso_shorts", "compra_sorvetes"]].head(3).round({"uso_shorts": 3, "compra_sorvetes": 2}))

# [Slide 14] Correlação entre shorts e sorvete
correlacao = dados["uso_shorts"].corr(dados["compra_sorvetes"])
print("\nCorrelação:", round(correlacao, 2))

plt.scatter(dados["uso_shorts"], dados["compra_sorvetes"], color="black", s=12)
plt.title("Uso de shorts vs. compra de sorvetes")
plt.xlabel("uso_shorts")
plt.ylabel("compra_sorvetes")
plt.show()

# [Slides 15 e 16] Regressão sem ajuste: compra_sorvetes = a·uso_shorts + b
# np.polyfit com grau 1 ajusta uma reta e devolve [a, b]
a, b = np.polyfit(dados["uso_shorts"], dados["compra_sorvetes"], 1)
print(f"\nSem ajuste: compra_sorvetes = {a:.3f}·uso_shorts + {b:.2f}")

# [Slides 21 e 22] Regressão ajustada:
# compra_sorvetes = a1·uso_shorts + a2·temperatura + b
# Montamos a matriz X (uma coluna de 1 para o intercepto b) e resolvemos
# por mínimos quadrados
X = np.column_stack([dados["uso_shorts"], dados["temperatura"], np.ones(n)])
y = dados["compra_sorvetes"]
a1, a2, b = np.linalg.lstsq(X, y, rcond=None)[0]
print(f"Ajustado:   compra_sorvetes = {a1:.3f}·uso_shorts + {a2:.3f}·temperatura + {b:.2f}")

# O coeficiente de shorts é estatisticamente diferente de zero?
# Estatística t = coeficiente / erro padrão. Regra prática: |t| < 2 -> não significativo
residuos = y - X @ np.array([a1, a2, b])
variancia_residuos = (residuos ** 2).sum() / (n - 3)
erros_padrao = np.sqrt(np.diag(variancia_residuos * np.linalg.inv(X.T @ X)))
print(f"t do uso_shorts no modelo ajustado: {a1 / erros_padrao[0]:.2f}")


# =============================================================================
# A causa mascarada: tela grande e tempo de tela (slides 25 a 45)
#
# Em todos os mundos o efeito causal verdadeiro é:
#   - ser GenZ:        +20 minutos no tempo de tela
#   - ter tela grande: +10 minutos no tempo de tela
# =============================================================================

rng = np.random.default_rng(123)  # semente, para reprodutibilidade

pop_size = 100000

# -----------------------------------------------------------------------------
# [Slide 25] Mundo 1: GenZ e tela grande são independentes
#   - tempo de tela ~ normal, média ~50 min (não GenZ, sem tela grande)
#   - 30% da população é GenZ
#   - 20% das pessoas têm celular de tela grande
# -----------------------------------------------------------------------------

population = pd.DataFrame({
    "gen_z": rng.binomial(1, 0.3, size=pop_size),
    "tela_grande": rng.binomial(1, 0.2, size=pop_size),
})
population["tempo_tela"] = (
    rng.normal(50, 2, size=pop_size)
    + 20 * population["gen_z"]
    + 10 * population["tela_grande"]
)

# [Slide 29] Comparação de médias
medias = population.groupby("tela_grande")["tempo_tela"].mean()
print("\nMundo 1 - tempo de tela médio por tipo de tela:")
print(medias.round(1))
print("Diferença:", round(medias[1] - medias[0], 2))

# [Slides 30 e 31] Regressão: tempo_tela = b + a·tela_grande
a, b = np.polyfit(population["tela_grande"], population["tempo_tela"], 1)
print(f"Regressão: tempo_tela = {b:.2f} + {a:.2f}·tela_grande")

# -----------------------------------------------------------------------------
# [Slide 32] Mundo 2: GenZ compra mais tela grande
#   - mesmas premissas do Mundo 1
#   - novo: 50% dos GenZ que não têm celular de tela grande decidem comprar um
# -----------------------------------------------------------------------------

population2 = pd.DataFrame({
    "gen_z": rng.binomial(1, 0.3, size=pop_size),
    "tela_grande_natural": rng.binomial(1, 0.2, size=pop_size),
})

# Só GenZ sem tela grande natural compram uma (50% de chance)
pode_comprar = (population2["gen_z"] == 1) & (population2["tela_grande_natural"] == 0)
comprou = rng.binomial(1, 0.5, size=pop_size) == 1
population2["tela_grande"] = ((population2["tela_grande_natural"] == 1) | (pode_comprar & comprou)).astype(int)

population2["tempo_tela"] = (
    rng.normal(50, 2, size=pop_size)
    + 20 * population2["gen_z"]
    + 10 * population2["tela_grande"]
)

# [Slide 36] Comparação de médias
medias = population2.groupby("tela_grande")["tempo_tela"].mean()
print("\nMundo 2 - tempo de tela médio por tipo de tela:")
print(medias.round(1))
print("Diferença:", round(medias[1] - medias[0], 2))

# [Slides 37 e 38] Regressão ingênua: tempo_tela = b + a·tela_grande
a_sem_ajuste, b = np.polyfit(population2["tela_grande"], population2["tempo_tela"], 1)
print(f"Sem ajuste: tempo_tela = {b:.2f} + {a_sem_ajuste:.2f}·tela_grande")

# [Slides 41 a 44] tempo_tela = a1·tela_grande + a2·gen_z + b
X = np.column_stack([population2["tela_grande"], population2["gen_z"], np.ones(pop_size)])
a1, a2, b = np.linalg.lstsq(X, population2["tempo_tela"], rcond=None)[0]
print(f"Ajustado:   tempo_tela = {a1:.2f}·tela_grande + {a2:.2f}·gen_z + {b:.2f}")

# [Slide 45] Efeito verdadeiro x sem ajuste x ajustado por gen_z
print("\nEfeito de tela_grande:")
print("  verdadeiro:        10")
print(f"  sem ajuste:        {a_sem_ajuste:.2f}")
print(f"  ajustado por gen_z: {a1:.2f}")
