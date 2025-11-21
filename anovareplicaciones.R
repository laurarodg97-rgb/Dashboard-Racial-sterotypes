#replicación 1
library(readr)
library(dplyr)
library(stringr)
library(afex)

# Cargar datos de la replicación
data_rt1 <- read_delim("beh_replication1.csv", delim = ",", col_names = TRUE)

setwd("C:/Users/jaime/OneDrive/Documents/Universidad Laura/Sexto semestre/Diseño de experimentos/Artículo/Behavioral Replication")

# Limpiar y preparar datos
data_limpia1 <- data_rt1 %>%
  mutate(
    RT = str_replace_all(RT, "\\s+", ""),        # quitar espacios
    RT = str_replace(RT, "\\.(?=.*\\.)", ""),    # eliminar doble punto si existe
    RT = as.numeric(RT)                          # convertir a numérico
  )

# Factores
data_limpia1$subjID<- as.factor(data_limpia1$subjID)
data_limpia1$prime  <- as.factor(data_limpia1$prime)
data_limpia1$target <- as.factor(data_limpia1$target)

# Verificar número de participantes
cat("Número de participantes únicos:\n")
print(length(unique(data_limpia1$subjID)))

# Filtrar tiempos extremos
data_limpia1 <- data_limpia1 %>% filter(RT > 200 & RT < 2000)

# Promedios descriptivos por condición
resumen_rt <- data_limpia1 %>%
  group_by(prime, target) %>%
  summarise(
    mean_rt_log = mean(RT, na.rm = TRUE),
    sd_rt = sd(RT, na.rm = TRUE),
    n = n()
  )

cat("\nPromedios por condición:\n")
print(resumen_rt)

# ANOVA de medidas repetidas (Prime × Target)
anova_rep1 <- aov_ez(
  id = "subjID",
  dv = "RT",
  data = data_limpia1,
  within = c("prime", "target"),
  type = 3
)

cat("\nResultados del ANOVA replicación (rt_log):\n")
print(anova_rep1)

write.csv2(data_limpia1, "ANOVA_replicaciones1.csv", row.names = FALSE)
getwd()

#replicación 2


# Cargar datos de la replicación
data_rt2 <- read_delim("beh_replication2.csv", delim = ",", col_names = TRUE)

# Limpiar y preparar datos
data_limpia2 <- data_rt2 %>%
  mutate(
    RT = str_replace_all(RT, "\\s+", ""),        # quitar espacios
    RT = str_replace(RT, "\\.(?=.*\\.)", ""),    # eliminar doble punto si existe
    RT = as.numeric(RT)                          # convertir a numérico
  )

# Factores
data_limpia2$subjID<- as.factor(data_limpia2$subjID)
data_limpia2$prime  <- as.factor(data_limpia2$prime)
data_limpia2$target <- as.factor(data_limpia2$target)

# Verificar número de participantes
cat("Número de participantes únicos:\n")
print(length(unique(data_limpia2$subjID)))

# Filtrar tiempos extremos
data_limpia2 <- data_limpia2 %>% filter(RT > 200 & RT < 2000)

# Promedios descriptivos por condición
resumen_rt2 <- data_limpia2 %>%
  group_by(prime, target) %>%
  summarise(
    mean_rt_log = mean(RT, na.rm = TRUE),
    sd_rt = sd(RT, na.rm = TRUE),
    n = n()
  )

cat("\nPromedios por condición:\n")
print(resumen_rt2)

# ANOVA de medidas repetidas (Prime × Target)
anova_rep2 <- aov_ez(
  id = "subjID",
  dv = "RT",
  data = data_limpia2,
  within = c("prime", "target"),
  type = 3
)

print(anova_rep2)

write.csv2(data_limpia2, "ANOVA_replicaciones2.csv", row.names = FALSE)
getwd()

#3er ANOVA 

# Cargar datos de la replicación 1

# Limpiar y preparar datos
data_limpia1 <- data_rt1 %>%
  mutate(
    RT = str_replace_all(RT, "\\s+", ""),        # quitar espacios
    RT = str_replace(RT, "\\.(?=.*\\.)", ""),    # eliminar doble punto si existe
    RT = as.numeric(RT)                          # convertir a numérico
  )

# Factores
data_limpia1$subjID<- as.factor(data_limpia1$subjID)
data_limpia1$prime  <- as.factor(data_limpia1$prime)
data_limpia1$target <- as.factor(data_limpia1$target)
data_limpia1$race_participant <- as.factor(data_limpia1$sub_race)  # 👈 nuevo factor entre sujetos


# Filtrar tiempos extremos
data_limpia1 <- data_limpia1 %>% filter(RT > 200 & RT < 2000)


# ANOVA de medidas repetidas (Prime × Target)
anova_mixto1 <- aov_car(
  RT ~ prime * target * sub_race + Error(subjID/(prime*target)),
  data = data_limpia1,
  factorize = FALSE,  # evita volver a factorizar si ya lo hiciste
  type = 3
)

print(anova_mixto1)


# Cargar datos de la replicación 2

# Limpiar y preparar datos
data_limpia2 <- data_rt2 %>%
  mutate(
    RT = str_replace_all(RT, "\\s+", ""),        # quitar espacios
    RT = str_replace(RT, "\\.(?=.*\\.)", ""),    # eliminar doble punto si existe
    RT = as.numeric(RT)                          # convertir a numérico
  )

# Factores
data_limpia2$subjID<- as.factor(data_limpia2$subjID)
data_limpia2$prime  <- as.factor(data_limpia2$prime)
data_limpia2$target <- as.factor(data_limpia2$target)
data_limpia2$race_participant <- as.factor(data_limpia2$sub_race)  # 👈 nuevo factor entre sujetos


# Filtrar tiempos extremos
data_limpia2 <- data_limpia2 %>% filter(RT > 200 & RT < 2000)


# ANOVA de medidas repetidas (Prime × Target)
anova_mixto2 <- aov_car(
  RT ~ prime * target * sub_race + Error(subjID/(prime*target)),
  data = data_limpia2,
  factorize = FALSE,  # evita volver a factorizar si ya lo hiciste
  type = 3
)

print(anova_mixto2)
