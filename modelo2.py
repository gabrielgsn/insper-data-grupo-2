from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import json

# Configurações do Selenium com Chrome DevTools Protocol
chrome_options = Options()
chrome_options.add_argument("--headless")  # Executar em modo headless (sem abrir a janela do navegador)
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")

# Iniciar o navegador com Selenium
driver = webdriver.Chrome(options=chrome_options)

# Ativar o Network em DevTools
driver.execute_cdp_cmd("Network.enable", {})

# Função para interceptar e capturar as requisições de rede
def capture_network_traffic():
    network_log = []

    def log_request(request):
        # Filtro para capturar requisições da API específica
        if 'https://apigw.prod.quintoandar.com.br/cached/house-listing-search/v1/search/' in request['request']['url']:
            network_log.append({
                'url': request['request']['url'],
                'method': request['request']['method'],
                'headers': request['request']['headers'],
                'postData': request.get('request', {}).get('postData', None)
            })

    # Registrar callback para monitorar requisições de rede
    driver.request_interceptor = log_request
    driver.execute_cdp_cmd('Network.requestWillBeSent', {
        'listener': log_request
    })

    return network_log

# Navegar para o site do QuintoAndar
driver.get('https://www.quintoandar.com.br/comprar/imovel/planalto-paulista-sao-paulo-sp-brasil')

# Esperar o site carregar e capturar o tráfego de rede
network_data = capture_network_traffic()

# Imprimir as requisições capturadas
for entry in network_data:
    print(f"URL: {entry['url']}")
    print(f"Método: {entry['method']}")
    print(f"Headers: {json.dumps(entry['headers'], indent=2)}")
    print(f"Post Data: {entry['postData']}")
    print("="*50)

# Fechar o navegador
driver.quit()