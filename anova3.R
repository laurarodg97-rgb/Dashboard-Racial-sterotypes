library(readr)
library(dplyr)
library(stringr)
library(afex)


# sensitive wit
data_mvpa <- read_delim("ANOVA object-sensitive_WIT.csv", delim = ",", col_names = TRUE)



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

# ANOVA 2×2 de medidas repetidas (Prime × Target)
anova_mvpa <- aov_ez(
  id = "id",
  dv = "value",  # o el nombre de la variable dependiente en tu archivo
  data = data_limpiamvpa,
  within = c("prime", "target"),
  type = 3
)

print(anova_mvpa)

write.csv2(data_limpiamvpa, "ANOVA_sensitivewit.csv", row.names = FALSE)

getwd()

#searchlight wit

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

# ANOVA 2×2 de medidas repetidas (Prime × Target)
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

# search control

data_control <- read_delim("ANOVA searchlight_Control.csv", delim = ",", col_names = TRUE)

data_limpiacontrol <- data_control %>%
  mutate(
    value = str_replace_all(value, "\\s+", ""),       
    value = str_replace(value, "\\.(?=.*\\.)", ""),      
    value = as.numeric(value)                           
  )

data_control$id     <- as.factor(data_control$id)
data_control$prime  <- as.factor(data_control$prime)
data_control$target <- as.factor(data_control$target)

# ANOVA 2x2 (Prime × Target)
anova_control <- aov_ez(
  id = "id",
  dv = "value", 
  data = data_control,
  within = c("prime", "target"),
  type = 3
)

print(anova_control)

write.csv2(data_limpiacontrol, "ANOVA_searchcontrol.csv", row.names = FALSE)

getwd()

# sensitive control ****NO REALIZADA EN EL ARTÍCULO****

data_controlsensitive <- read_delim("ANOVA object-sensitive_Control.csv", delim = ",", col_names = TRUE)

data_limpiacontrolsensitive <- data_controlsensitive %>%
  mutate(
    value = str_replace_all(value, "\\s+", ""),       
    value = str_replace(value, "\\.(?=.*\\.)", ""),      
    value = as.numeric(value)                           
  )

data_controlsensitive$id     <- as.factor(data_controlsensitive$id)
data_controlsensitive$prime  <- as.factor(data_controlsensitive$prime)
data_controlsensitive$target <- as.factor(data_controlsensitive$target)

# ANOVA 2x2 (Prime × Target)
anova_controlsensitive <- aov_ez(
  id = "id",
  dv = "value", 
  data = data_controlsensitive,
  within = c("prime", "target"),
  type = 3
)

print(anova_controlsensitive)

write.csv2(data_limpiacontrolsensitive, "ANOVA_sensitivecontrol.csv", row.names = FALSE)

getwd()
