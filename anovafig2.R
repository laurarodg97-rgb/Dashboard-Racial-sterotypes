

library(readr)
library(dplyr)
library(stringr)
library(afex)


data_raw <- read_delim("ANOVA beh RT.csv", delim = ",", col_names = TRUE)

setwd("C:/Users/jaime/OneDrive/Documents/Universidad Laura/Sexto semestre/Diseño de experimentos/Artículo/Main")

data_limpia <- data_raw %>%
  mutate(
    rt_log = str_replace_all(rt_log, "\\s+", ""),       
    rt_log = str_replace(rt_log, "\\.(?=.*\\.)", ""),      
    rt_log = as.numeric(rt_log)                           
  )

data_limpia$id     <- as.factor(data_limpia$id)
data_limpia$prime  <- as.factor(data_limpia$prime)
data_limpia$target <- as.factor(data_limpia$target)

cat("Número de participantes únicos:\n")
print(length(unique(data_limpia$id)))  #30


data_limpia <- data_limpia %>% filter(rt_raw > 200 & rt_raw < 2000)

#promedios
resumen_rt <- data_limpia %>%
  group_by(prime, target) %>%
  summarise(
    mean_rt_raw = mean(rt_raw, na.rm = TRUE),
    mean_rt_log = mean(rt_log, na.rm = TRUE),
    sd_rt = sd(rt_raw, na.rm = TRUE),
    n = n()
  )

cat("\nPromedios por condición:\n")
print(resumen_rt)

#ANOVA (Prime × Target)
anova_rt <- aov_ez(
  id = "id",
  dv = "rt_log",
  data = data_limpia,
  within = c("prime", "target"),
  type = 3
)

cat("\nResultados del ANOVA (rt_log):\n")
print(anova_rt)
write.csv2(data_limpia, "ANOVA_beh_RT_limpia_excel.csv", row.names = FALSE)

getwd()

# Resultados esperados:
# Target:      F(1,29) = 20.64, p < .001
# Prime:       F(1,29) = 2.42,  p = .133
# Interacción: F(1,29) = 6.54,  p = .016

##Análisis exploratorio

##Objetivo de la base de datos
#Se busca encontrar un efecto de interacción significativo entre las variables
#prime y target, es decir si el color de la persona (blanco o negro) influye 
#en la identificación del objeto (arma o herramienta)


View(data_limpia)

library(dplyr)


table(data_limpia$prime, data_limpia$target) #Mismo número de ensayos en cada condición 

library(ggplot2)

ggplot(data_limpia, aes(sample = rt_raw)) +
  geom_qq(color = "#1f77b4", size = 2, alpha = 0.7) + 
  geom_qq_line(color = "black", linewidth = 1.2, linetype = "solid") +
  labs(
    title = "QQ-Plot de rt_raw",
    x = "Cuantiles Teóricos (Normal)",
    y = "Cuantiles Muestrales"
  ) +
  theme_minimal(base_size = 14) +
  theme(
    plot.title = element_text(face = "bold", hjust = 0.5),
    panel.grid.minor = element_blank()
  )

#Como los tiempos de reacción suelen tener una distribución
#sesgada (muchos valores bajos y unos pocos muy altos), aplicamos
#una transformación logarítmica para ayudar a 
#normalizarlos para poder aplicar análisis estadísticos paramétricos.

ggplot(data_limpia, aes(sample = rt_log)) +
  geom_qq(color = "#1f77b4", size = 2, alpha = 0.7) + 
  geom_qq_line(color = "black", linewidth = 1.2, linetype = "solid") +
  labs(
    title = "QQ-Plot de rt_log",
    x = "Cuantiles Teóricos (Normal)",
    y = "Cuantiles Muestrales"
  ) +
  theme_minimal(base_size = 14) +
  theme(
    plot.title = element_text(face = "bold", hjust = 0.5),
    panel.grid.minor = element_blank()
  )



data_gun <- data_limpia %>% filter(target == "gun")
data_tool <- data_limpia %>% filter(target == "tool")

# Histogramas y Q-Q plots separados
ggplot(data_gun, aes(x = rt_log)) + geom_histogram(bins = 25) + facet_wrap(~prime)
ggplot(data_tool, aes(x = rt_log)) + geom_histogram(bins = 25) + facet_wrap(~prime)


library(ggplot2)

ggplot(data_limpia, aes(x = prime, y = rt_log, fill = target)) +
  geom_boxplot(alpha = 0.7, position = position_dodge(0.8)) +
  labs(
    title = "Diagrama de cajas de tiempo de respuesta (log)",
    x = "Prime",
    y = "Tiempo de respuesta (log)",
    fill = "Target"
  ) +
  theme_minimal() +
  theme(
    plot.title = element_text(hjust = 0.5),
    legend.position = "top"
  )


#Los participantes tardan más en identificar herramientas cuando siguen a 
#una cara negra, pero no hay diferencia con las armas. Esto muestra que los 
#estereotipos raciales distorsionan la percepción visual: el cerebro empieza a 
#ver una herramienta como si fuera un arma. 

#Antes de ver si hay una diferencia significativa vamos a verificar supuesto


summary(data_gun$rt_log)

summary(data_tool$rt_log)

ad.test(data_gun$rt_log)
jarque.bera.test(data_gun$rt_log) #Rechazamos normalidad
jarque.bera.test(data_tool$rt_log) #Normal


jarque.bera.test(data_limpia$rt_log)


library(ggplot2)

data_agg <- data_limpia %>%
  group_by(id, prime, target) %>%
  summarise(rt_mean = mean(rt_log, na.rm = TRUE), .groups = "drop")


library(car)

# Crear una variable combinada de condición
data_agg$condition <- interaction(data_agg$prime, data_agg$target)

# Test de Levene
levene_test <- leveneTest(rt_mean ~ condition, data = data_agg)
print(levene_test)

library(gridExtra)

# --- Histogramas ---
ggplot(data_limpia, aes(x = rt_raw)) +
  geom_histogram(bins = 30, fill = "skyblue", color = "black") +
  labs(title = "Histograma: rt_raw", x = "Tiempo de reacción (ms)", y = "Frecuencia")

ggplot(data_limpia, aes(x = rt_log)) +
  geom_histogram(bins = 30, fill = "lightgreen", color = "black") +
  labs(title = "Histograma: rt_log", x = "log(Tiempo de reacción)", y = "Frecuencia")


# Combinar en una sola figura (2x2)
#grid.arrange(p1, p2, p3, p4, ncol = 2)
