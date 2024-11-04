import utils as u


u.create_table()
#Inserir CEP desejado na linha abaixo

ceps_vila_andrade = [
    "04105063"
]

for cep in ceps_vila_andrade:
    try:
        u.extract_data(cep)
    except:
        print("Erro ao extrair dados do CEP (run)")
        continue
