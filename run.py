import utils as u

u.create_table()
#Inserir CEP desejado na linha abaixo
u.extract_data("04078012")

#Exibir os preços médios dos imóveis por bairro
for bairro, preco_medio_m2 in u.precos_medios():
    print(f"Bairro: {bairro}  | Preço médio por m²: R${preco_medio_m2:.2f}")