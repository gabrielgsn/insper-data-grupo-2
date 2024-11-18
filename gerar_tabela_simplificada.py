import sqlite3
import geopandas as gpd

def create_simplified_table(setores_gdf):
    # Conectando ao banco de dados original
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    
    # Criar um novo banco de dados para a tabela simplificada
    conn_simplified = sqlite3.connect('dados_final.db')
    cursor_simplified = conn_simplified.cursor()

    # Criar a nova tabela com setores, preço médio por m², quantidade de imóveis, maior e menor preço por m², latitude e longitude
    cursor_simplified.execute('''
    CREATE TABLE IF NOT EXISTS dados_final (
        setor TEXT PRIMARY KEY,
        preco_medio_m2 FLOAT,
        quantidade_imoveis INTEGER,
        maior_preco_m2 FLOAT,
        menor_preco_m2 FLOAT,
        lat FLOAT,
        lon FLOAT
    )
    ''')

    # Selecionar os dados de setor e calcular a média, quantidade, maior e menor preço por m² do banco de dados original
    cursor.execute('''
    SELECT setor, AVG(preco_m2) AS preco_medio_m2, COUNT(preco_m2) AS quantidade_imoveis,
           MAX(preco_m2) AS maior_preco_m2, MIN(preco_m2) AS menor_preco_m2
    FROM data
    GROUP BY setor
    ''')

    setores_precos = cursor.fetchall()

    # Percorrer os setores e calcular as informações necessárias
    for setor, preco_medio_m2, quantidade_imoveis, maior_preco_m2, menor_preco_m2 in setores_precos:
        # Encontrar o setor correspondente no GeoDataFrame (setores_gdf)
        setor_data = setores_gdf[setores_gdf['CD_SETOR'] == setor]
        
        if not setor_data.empty:
            # Pegar o ponto central do polígono do setor
            ponto_central = setor_data.geometry.centroid.iloc[0]
            lat, lon = ponto_central.y, ponto_central.x
            
            # Inserir os dados na tabela simplificada
            cursor_simplified.execute('''
            INSERT OR REPLACE INTO dados_final (setor, preco_medio_m2, quantidade_imoveis, 
                                                maior_preco_m2, menor_preco_m2, lat, lon)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (setor, preco_medio_m2, quantidade_imoveis, maior_preco_m2, menor_preco_m2, lat, lon))
    
    # Fechar as conexões com os bancos de dados
    conn.commit()
    conn.close()
    
    conn_simplified.commit()
    conn_simplified.close()

# Carregue os setores de censitários (GeoDataFrame)
setores_gdf = gpd.read_file('dados\geo\SP_Malha_Preliminar_2022.shp').to_crs(epsg=4326)

# Chame a função para criar o novo banco de dados simplificado
create_simplified_table(setores_gdf)
