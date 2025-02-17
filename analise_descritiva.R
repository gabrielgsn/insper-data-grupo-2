library(modelsummary)
library(tidyverse)
library(gt)
library(ggplot2)
library(dplyr)
library(svglite)

distrito <- read.csv("insper-data-grupo-2/dados/base_distritos.csv") %>% 
  select(cod_ibge, distrito, regioes)
base <- read.csv("insper-data-grupo-2/dados/base_final.csv") %>% 
  select(Distrito, preco_m2_itbi, preco_m2_iptu)

medias_precos_por_regiao_distrito <- base %>% 
  right_join(distrito, by=c("Distrito" = "cod_ibge")) %>% 
  group_by(distrito, regioes) %>% 
  # Tirando a média dos precos do m2 de todos os subdistritos por região e distrito
  summarize(
    mean_preco_m2_iptu = mean(preco_m2_iptu, na.rm = TRUE),
    mean_preco_m2_itbi = mean(preco_m2_itbi, na.rm = TRUE)
  )

# Preço médio

gera_plot_por_regiao <- function(regiao, titulo) {
  medias_precos_long <- medias_precos_por_regiao_distrito %>%
    filter(regioes %in% regiao) %>%
    pivot_longer(cols = c(mean_preco_m2_iptu, mean_preco_m2_itbi), 
                 names_to = "tipo_preco", 
                 values_to = "preco_m2") %>%
    mutate(tipo_preco = recode(tipo_preco, 
                               "mean_preco_m2_iptu" = "IPTU", 
                               "mean_preco_m2_itbi" = "ITBI"))
  
  ggplot(medias_precos_long, aes(
    x = reorder(distrito, preco_m2), 
    y = preco_m2, fill = tipo_preco)) +
    geom_bar(stat = "identity", position = "dodge") +
    coord_flip() +
    facet_wrap(~regioes, scales = "free") + 
    labs(title = titulo,
         x = "Distrito", y = "Preço Médio do m² (R$)", fill = "Referência de Preço") +
    scale_fill_manual(values = c("IPTU" = "blue", "ITBI" = "red")) +
    theme_minimal() +
    theme(legend.position = ifelse(length(regiao) > 1, "bottom", "right"), 
          axis.text.y = element_text(size = 9, hjust = 1, face = "bold"),
          strip.text = element_text(size = 10, face = "bold"),
          plot.title = element_text(hjust = 0.5, size = 11, face = "bold"), 
          legend.title = element_text(size=9),
          legend.text = element_text(size=9))
}

plot_leste_oeste <- gera_plot_por_regiao(c("Leste", "Oeste"), "Preço Médio do m² por Distrito e Região (Leste e Oeste)")
plot_norte_sul <- gera_plot_por_regiao(c("Norte", "Sul"), "Preço Médio do m² por Distrito e Região (Norte e Sul)")
plot_centro <- gera_plot_por_regiao(c("Centro"), "Preço Médio do m² por Distrito (Centro)")

# Display
plot_leste_oeste
plot_norte_sul
plot_centro

ggsave(filename = "graficos/plot_leste_oeste_medias.svg", plot_leste_oeste)
ggsave(filename = "graficos/plot_norte_sul_medias.svg", plot_norte_sul)
ggsave(filename = "graficos/plot_centro_medias.svg", plot_centro)

# Desvio padrão

gera_plot_por_regiao2 <- function(regiao, titulo) {
  sd_precos_long <- base %>%
    right_join(distrito, by = c("Distrito" = "cod_ibge")) %>% 
    group_by(distrito, regioes) %>% 
    summarize(
      sd_preco_m2_iptu = sd(preco_m2_iptu, na.rm = TRUE),
      sd_preco_m2_itbi = sd(preco_m2_itbi, na.rm = TRUE)
    ) %>%
    pivot_longer(cols = c(sd_preco_m2_iptu, sd_preco_m2_itbi), 
                 names_to = "tipo_preco", 
                 values_to = "sd_preco_m2") %>%
    filter(regioes %in% regiao) %>%
    mutate(tipo_preco = recode(tipo_preco, 
                               "sd_preco_m2_iptu" = "IPTU", 
                               "sd_preco_m2_itbi" = "ITBI"))
  
  ggplot(sd_precos_long, aes(x = reorder(distrito, sd_preco_m2), 
                             y = sd_preco_m2, 
                             fill = tipo_preco)) +
    geom_bar(stat = "identity", position = "dodge") +
    coord_flip() + 
    facet_wrap(~regioes, scales = "free") +
    labs(title = "Desvio Padrão do preço médio do m² por Distrito e Região",
         x = "Distrito", y = "Desvio Padrão do Preço Médio do m² (R$)", fill = "Referência de Preço") +
    scale_fill_manual(values = c("IPTU" = "blue", "ITBI" = "red")) +
    theme_minimal() +
    theme(legend.position = "bottom",
          axis.text.y = element_text(size = 7.5, hjust = 1),
          strip.text = element_text(size = 10, face = "bold"),
          plot.title = element_text(hjust = 0.5, size = 11, face = "bold"))
}

plot_leste_oeste <- gera_plot_por_regiao2(c("Leste", "Oeste"), "Preço Médio do m² por Distrito e Região (Leste e Oeste)")
plot_norte_sul <- gera_plot_por_regiao2(c("Norte", "Sul"), "Preço Médio do m² por Distrito e Região (Norte e Sul)")
plot_centro <- gera_plot_por_regiao2(c("Centro"), "Preço Médio do m² por Distrito (Centro)")

# Display
plot_leste_oeste
plot_norte_sul
plot_centro

ggsave(filename = "graficos/plot_leste_oeste_desvios.svg", plot_leste_oeste)
ggsave(filename = "graficos/plot_norte_sul_desvios.svg", plot_norte_sul)
ggsave(filename = "graficos/plot_centro_desvios.svg", plot_centro)
