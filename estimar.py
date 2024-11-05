import utils as u

if __name__ == "__main__":
    endereco = "Rua Jandiatuba, Sao Paulo, Brasil"
    preco_medio = u.estimate_price(endereco)
    
    if preco_medio:
        print(f"Preço médio estimado por m² na região: R$ {preco_medio:.2f}")
    else:
        print("Não foi possível estimar o preço.")