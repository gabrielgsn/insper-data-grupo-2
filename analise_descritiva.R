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
  # Tirando a média dos precos do m2 de todos os subdistritos por regiao e distrito
  summarize(
    mean_preco_m2_iptu = mean(preco_m2_iptu, na.rm = TRUE),
    mean_preco_m2_itbi = mean(preco_m2_itbi, na.rm = TRUE)
  )

plot_preco_iptu <- 
  ggplot(medias_precos_por_regiao_distrito, aes(
         x = reorder(distrito, mean_preco_m2_iptu), 
         y = mean_preco_m2_iptu, fill = regioes)) +
  geom_bar(stat = "identity") +
  coord_flip() +
  facet_wrap(~regioes, scales = "free") + 
  labs(title = "Preço Médio do m² por Distrito e Região (IPTU)",
       x = "Distrito", y = "Preço Médio do m² pelo IPTU (R$)") +
  theme_minimal() +
  theme(legend.position = "none",
        axis.text.y = element_text(size = 7.5, hjust = 1),
        strip.text = element_text(size = 7, face = "bold"),
        plot.title = element_text(hjust = 0.5, size = 8, face = "bold"),
        legend.title = element_text(size=6),
        legend.text = element_text(size=6)) 

plot_preco_itbi <- 
  ggplot(medias_precos_por_regiao_distrito, aes(
         x = reorder(distrito, mean_preco_m2_itbi), 
         y = mean_preco_m2_itbi, fill = regioes)) +
  geom_bar(stat = "identity") +
  coord_flip() +
  facet_wrap(~regioes, scales = "free") + 
  labs(title = "Preço Médio do m² por Distrito e Região (ITBI)",
       x = "Distrito", y = "Preço Médio do m² pelo ITBI (R$)") +
  theme_minimal() +
  theme(legend.position = "none",
        axis.text.y = element_text(size = 7.5, hjust = 1),
        strip.text = element_text(size = 7, face = "bold"),
        plot.title = element_text(hjust = 0.5, size = 8, face = "bold"),
        legend.title = element_text(size=6),
        legend.text = element_text(size=6)) 

medias_precos_long <- medias_precos_por_regiao_distrito %>%
  pivot_longer(cols = c(mean_preco_m2_iptu, mean_preco_m2_itbi), 
               names_to = "tipo_preco", 
               values_to = "preco_m2") %>%
  mutate(tipo_preco = recode(tipo_preco, 
                             "mean_preco_m2_iptu" = "IPTU", 
                             "mean_preco_m2_itbi" = "ITBI"))

plot_preco_iptu_itbi <- 
  ggplot(medias_precos_long, aes(x = reorder(distrito, preco_m2), 
                               y = preco_m2, 
                               fill = tipo_preco)) +
  geom_bar(stat = "identity", position = "dodge") + 
  coord_flip() + 
  facet_wrap(~regioes, scales = "free") + 
  labs(title = "Preço Médio do m² por Distrito e Região",
       x = "Distrito", y = "Preço Médio do m² (R$)", fill = "Referência de Preço") +
  scale_fill_manual(values = c("IPTU" = "blue", "ITBI" = "red")) +
  theme_minimal() +
  theme(legend.position = "bottom",
        axis.text.y = element_text(size = 7, hjust = 1),
        strip.text = element_text(size = 7, face = "bold"),
        plot.title = element_text(hjust = 0.5, size = 8, face = "bold"),
        legend.title = element_text(size=6),
        legend.text = element_text(size=6))

ggsave(filename = "graficos/plot_preco_itbi.svg", plot_preco_itbi)
ggsave(filename = "graficos/plot_preco_iptu.svg", plot_preco_iptu)
ggsave(filename = "graficos/plot_preco_iptu_itbi.svg", plot_preco_iptu_itbi)