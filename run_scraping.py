import utils as u

u.create_table()
#Inserir CEP desejado na linha abaixo
ceps_moema_passaros = [
    "04521000", "04521001", "04521002", "04521003", "04521004",
    "04521005", "04521010", "04521020", "04521021", "04521022",
    "04521030", "04522000", "04522001", "04522010", "04522020",
    "04522030", "04522031", "04522032", "04522033", "04522034"
]

for cep in ceps_moema_passaros:
    try:
        u.extract_data(cep)
    except:
        print("Erro ao extrair dados do CEP")
        pass
