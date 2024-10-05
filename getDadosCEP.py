import requests
from bs4 import BeautifulSoup
import json
import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from pprint import pprint
import sqlite3


def getDadosCEP(cep):
		url = (f'http://www.viacep.com.br/ws/{cep}/json')
		
		req = requests.get(url)
		if req.status_code == 200:
			dados_json = json.loads(req.text)
			return dados_json
		else:
			print('Erro ao buscar CEP')

teste = getDadosCEP("04119010")

print(teste)