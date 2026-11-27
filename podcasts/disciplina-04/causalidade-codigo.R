# Live: Shorts não vendem sorvete: correlação, causalidade e confundimento
# Código que gera os números da apresentação (causalidade-1.pdf)

library(dplyr)
library(ggplot2)


# =============================================================================
# Uso de shorts vs. compra de sorvetes (slides 13 a 24)
# Correlação espúria: shorts NÃO afeta sorvete; os dois dependem da temperatura
#
#          temperatura
#          /         \
#     uso_shorts   compra_sorvetes
# =============================================================================

set.seed(123)  # para reprodutibilidade

# 200 dias simulados
n <- 200

# Confundidor: temperatura (Celsius), variando de 10 a 35 graus
temperatura <- runif(n, min = 10, max = 35)

# uso_shorts = % de pessoas de shorts no dia (aumenta com a temperatura)
uso_shorts <- pmin(1, pmax(0, (temperatura - 15) / 20)) * 100 + rnorm(n, mean = 0, sd = 5)
uso_shorts <- pmax(0, pmin(100, uso_shorts))  # limita valores entre 0 e 100%

# compra_sorvetes = quantidade de sorvetes comprados no dia (aumenta com a temperatura)
compra_sorvetes <- 5 + 0.5 * temperatura + rnorm(n, mean = 0, sd = 1)

dados <- data.frame(dia = 1:n, temperatura, uso_shorts, compra_sorvetes)

# [Slide 13] Primeiros dias: 7,39 / 12,88 ; 74,82 / 19,10 ; 24,89 / 14,17
# (no slide, 7,395 aparece truncado como 7,39)
dados |>
  select(dia, uso_shorts, compra_sorvetes) |>
  head(3) |>
  print(digits = 4)

# [Slide 14] Correlação: 0,94
cat("Correlação:", round(cor(dados$uso_shorts, dados$compra_sorvetes), 2), "\n")

print(
  ggplot(dados, aes(x = uso_shorts, y = compra_sorvetes)) +
    geom_point() +
    theme_minimal() +
    labs(title = "Uso de shorts vs. compra de sorvetes")
)

# [Slides 15 e 16] compra_sorvetes = 0,1·uso_shorts + 12
modelo_sem_ajuste <- lm(compra_sorvetes ~ uso_shorts, data = dados)
print(summary(modelo_sem_ajuste))

# [Slides 21 e 22] compra_sorvetes = a1·uso_shorts + a2·temperatura + b
# Sem ajuste: shorts 0,104 ***
# Ajustado:   shorts 0,004 (p = 0,72) ; temperatura 0,466 ***
modelo_ajustado <- lm(compra_sorvetes ~ uso_shorts + temperatura, data = dados)
print(summary(modelo_ajustado))


# =============================================================================
# A causa mascarada: tela grande e tempo de tela (slides 25 a 45)
#
# Em todos os mundos o efeito causal verdadeiro é:
#   - ser GenZ:        +20 minutos no tempo de tela
#   - ter tela grande: +10 minutos no tempo de tela
# =============================================================================

set.seed(123)  # para reprodutibilidade

pop_size <- 100000

# -----------------------------------------------------------------------------
# [Slide 25] Mundo 1: GenZ e tela grande são independentes
#   - tempo de tela ~ normal, média ~50 min (não GenZ, sem tela grande)
#   - 30% da população é GenZ
#   - 20% das pessoas têm celular de tela grande
# -----------------------------------------------------------------------------

gen_z <- rbinom(pop_size, size = 1, prob = 0.3)
tela_grande <- rbinom(pop_size, size = 1, prob = 0.2)

population <- tibble(
  id = 1:pop_size,
  gen_z = gen_z,
  tela_grande = tela_grande
) |>
  mutate(
    error_term = rnorm(n = pop_size, mean = 50, sd = 2),
    tempo_tela = error_term + 20 * gen_z + 10 * tela_grande
  )

# [Slide 29] Comparação de médias: ~10 minutos maior
population |>
  summarise(
    mean_tempo_tela = mean(tempo_tela),
    .by = c(tela_grande)
  ) |>
  arrange(tela_grande) |>
  print()

# [Slides 30 e 31] Regressão: tempo_tela = 56.028 + 9.825·tela_grande
print(lm(tempo_tela ~ tela_grande, data = population))

# -----------------------------------------------------------------------------
# [Slide 32] Mundo 2: GenZ compra mais tela grande
#   - mesmas premissas do Mundo 1
#   - novo: 50% dos GenZ que não têm celular de tela grande decidem comprar um
# -----------------------------------------------------------------------------

gen_z <- rbinom(pop_size, size = 1, prob = 0.3)
tela_grande_natural <- rbinom(pop_size, size = 1, prob = 0.2)

population2 <- tibble(
  id = 1:pop_size,
  gen_z = gen_z,
  tela_grande_natural = tela_grande_natural
) |>
  mutate(
    # Só GenZ sem tela grande natural compram uma (50% de chance)
    tela_grande_comprada = if_else(
      gen_z == 1 & tela_grande_natural == 0,
      rbinom(n = pop_size, size = 1, prob = 0.5),
      0L
    ),
    tela_grande = if_else(tela_grande_natural == 1 | tela_grande_comprada == 1, 1, 0),
    error_term = rnorm(n = pop_size, mean = 50, sd = 2),
    tempo_tela = error_term + 20 * gen_z + 10 * tela_grande
  )

# [Slide 36] Comparação de médias: ~17 minutos maior
population2 |>
  summarise(
    mean_tempo_tela = mean(tempo_tela),
    .by = c(tela_grande)
  ) |>
  arrange(tela_grande) |>
  print()

# [Slides 37 e 38] Regressão ingênua: tempo_tela = 53,49 + 17,76·tela_grande
modelo_tela_sem_ajuste <- lm(tempo_tela ~ tela_grande, data = population2)
print(modelo_tela_sem_ajuste)

# [Slides 41 a 44] tempo_tela = a1·tela_grande + a2·gen_z + b
# Regressão: tempo_tela = 10.01·tela_grande + 20·gen_z + 49.99
modelo_tela_ajustado <- lm(tempo_tela ~ tela_grande + gen_z, data = population2)
print(modelo_tela_ajustado)

# [Slide 45] Efeito verdadeiro x sem ajuste x ajustado por gen_z
tibble(
  variavel          = c("tela_grande", "gen_z"),
  efeito_verdadeiro = c(10, 20),
  sem_ajuste        = c(coef(modelo_tela_sem_ajuste)["tela_grande"], NA),
  ajustado_por_gen_z = coef(modelo_tela_ajustado)[c("tela_grande", "gen_z")]
) |>
  mutate(across(c(sem_ajuste, ajustado_por_gen_z), \(x) round(x, 2))) |>
  as.data.frame() |>
  print()


# =============================================================================
# [Slide 46] O que os dois mundos ensinam
# =============================================================================

tibble(
  caso               = c("Shorts x sorvete", "Tela grande x tempo de tela"),
  efeito_causal_real = c(0, 10),
  estimativa_ingenua = c(coef(modelo_sem_ajuste)["uso_shorts"],
                         coef(modelo_tela_sem_ajuste)["tela_grande"]),
  confundidor        = c("temperatura", "ser GenZ"),
  apos_ajuste        = c(coef(modelo_ajustado)["uso_shorts"],
                         coef(modelo_tela_ajustado)["tela_grande"])
) |>
  mutate(across(c(estimativa_ingenua, apos_ajuste), \(x) round(x, 2))) |>
  as.data.frame() |>
  print()
