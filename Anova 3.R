library(readr)
library(dplyr)
library(stringr)
library(afex)

setwd("Documents/Laurita/")
# sensitive wit IMPORTANTE
data_mvpa <- read_delim("ANOVA object-sensitive_WIT.csv", 
                        delim = ",", 
                        col_names = TRUE)


data_limpiamvpa <- data_mvpa %>%
  mutate(
    value = str_replace_all(value, "\\s+", ""),       
    value = str_replace(value, "\\.(?=.*\\.)", ""),      
    value = as.numeric(value)                           
  )
# Asegurar factores
data_mvpa$id <- as.factor(data_mvpa$id)
data_mvpa$prime <- as.factor(data_mvpa$prime)
data_mvpa$target <- as.factor(data_mvpa$target)

# ANOVA 2Ã—2 de medidas repetidas (Prime Ã— Target)

anova_mvpa <- aov_ez(
  id = "id",
  dv = "value",  # o el nombre de la variable dependiente en tu archivo
  data = data_limpiamvpa,
  within = c("prime", "target"),
  type = 3
)
options(digits = 10)
print(anova_mvpa)

write.csv2(data_limpiamvpa, "ANOVA_sensitivewit.csv", row.names = FALSE)

getwd()

### Residuos

# 1. Asegurar que las variables están como deben
data_limpiamvpa$id     <- as.factor(data_limpiamvpa$id)
data_limpiamvpa$prime  <- as.factor(data_limpiamvpa$prime)
data_limpiamvpa$target <- as.factor(data_limpiamvpa$target)

# 2. Calcular medias necesarias
# Media total
y_bar_total_mvpa <- mean(data_limpiamvpa$value, na.rm = TRUE)

# Medias por sujeto
mean_sujeto_mvpa <- aggregate(value ~ id, data = data_limpiamvpa, FUN = mean)
names(mean_sujeto_mvpa)[2] <- "y_bar_sujeto_mvpa"

# Medias por celda (prime x target)
mean_celda_mvpa <- aggregate(value ~ prime + target, data = data_limpiamvpa, FUN = mean)
names(mean_celda_mvpa)[3] <- "y_bar_celda_mvpa"

# 3. Unir todo al dataset original
data_resid_mvpa <- data_limpiamvpa %>%
  left_join(mean_sujeto_mvpa, by = "id") %>%
  left_join(mean_celda_mvpa, by = c("prime", "target"))

# 4. Calcular residuos del modelo de medidas repetidas
data_resid_mvpa$residual_mvpa <- with(data_resid_mvpa, value - y_bar_celda_mvpa - y_bar_sujeto_mvpa + y_bar_total_mvpa)

# 5. Extraer el vector de residuos
residuos_mvpa <- data_resid_mvpa$residual_mvpa

# 6. PRUEBA DE NORMALIDAD (Shapiro-Wilk)
shapiro_result_mvpa <- shapiro.test(residuos_mvpa)
print(shapiro_result_mvpa)

# 7. HOMOCEDASTICIDAD: prueba de Levene sobre residuos por celda
library(car)
?leveneTest
leveneTest(residuos_mvpa ~ interaction(data_resid_mvpa$prime, data_resid_mvpa$target))

# 8. INDEPENDENCIA: en medidas repetidas, se asume por diseño (aleatorización de ensayos).
#    Sin información de orden, no se prueba formalmente.


#searchlight wit  IMPORTANTE

data_search <- read_delim("ANOVA searchlight_WIT.csv", delim = ",", col_names = TRUE)


data_limpiasearch <- data_search %>%
  mutate(
    value = str_replace_all(value, "\\s+", ""),       
    value = str_replace(value, "\\.(?=.*\\.)", ""),      
    value = as.numeric(value)                           
  )
# Asegurar factores
data_search$id <- as.factor(data_search$id)
data_search$prime <- as.factor(data_search$prime)
data_search$target <- as.factor(data_search$target)

# ANOVA 2Ã—2 de medidas repetidas (Prime Ã— Target)
anova_search <- aov_ez(
  id = "id",
  dv = "value",  # o el nombre de la variable dependiente en tu archivo
  data = data_limpiasearch,
  within = c("prime", "target"),
  type = 3
)

print(anova_search)

write.csv2(data_limpiasearch, "ANOVA_searchwit.csv", row.names = FALSE)

getwd()

### Residuos

# 1. Asegurar que las variables están como deben
data_search$id     <- as.factor(data_search$id)
data_search$prime  <- as.factor(data_search$prime)
data_search$target <- as.factor(data_search$target)

# 2. Calcular medias necesarias
# Media total
y_bar_total_search <- mean(data_search$value, na.rm = TRUE)

# Medias por sujeto
mean_sujeto_search <- aggregate(value ~ id, data = data_search, FUN = mean)
names(mean_sujeto_search)[2] <- "y_bar_sujeto_search"

# Medias por celda (prime x target)
mean_celda_search <- aggregate(value ~ prime + target, data = data_search, FUN = mean)
names(mean_celda_search)[3] <- "y_bar_celda_search"

# 3. Unir todo al dataset original
data_resid_search <- data_search %>%
  left_join(mean_sujeto_search, by = "id") %>%
  left_join(mean_celda_search, by = c("prime", "target"))

# 4. Calcular residuos del modelo de medidas repetidas
data_resid_search$residual_search <- with(data_resid_search, value - y_bar_celda_search - y_bar_sujeto_search + y_bar_total_search)

# 5. Extraer el vector de residuos
residuos_search <- data_resid_search$residual_search

# 6. PRUEBA DE NORMALIDAD (Shapiro-Wilk)
shapiro_result_search <- shapiro.test(residuos_search)
print(shapiro_result_search)

# 7. HOMOCEDASTICIDAD: prueba de Levene sobre residuos por celda
library(car)
leveneTest(residuos_search ~ interaction(data_resid_search$prime, data_resid_search$target))

