import time
import unicodedata
import pandas as pd
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from urllib.parse import urljoin
import csv

def gerar_vetor_urls_cada_categoria(arquivo_csv):
    df = pd.read_csv(arquivo_csv, encoding='latin-1')
    urls_categoria = []

    for _, row in df.iterrows():
        url = row['Link']
        num_paginas = row['Quantidade de Paginas']

        for pagina in range(1, num_paginas + 1):
            url_pagina = url + '?q=&p='+ str(pagina)
            urls_categoria.append(url_pagina)

    return urls_categoria

def obter_videos_site(arquivo_csv):
    urls_categoria = gerar_vetor_urls_cada_categoria(arquivo_csv)

    options = Options()
    options.headless = True

    driver = webdriver.Chrome(options=options)

    lista_videos = []

    for url in urls_categoria:
        driver.get(url)
        time.sleep(5)

        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        divs = soup.find_all('div', class_='search-result-title')

        for div in divs:
            atags = div.find_all('a')

            for a in atags:
                small_tag = a.find('small')
                if small_tag:
                    small_tag.decompose()

                text = a.get_text(strip=True)
                text = "".join(ch for ch in text if unicodedata.category(ch)[0] != "C")
                text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')

                href = a['href']

                driver.execute_script("window.open(arguments[0], '_blank');", href)
                time.sleep(1)

                driver.switch_to.window(driver.window_handles[-1])

                video_html = driver.page_source
                video_soup = BeautifulSoup(video_html, 'html.parser')

                video_div = video_soup.find('div', class_='col-md-7')

                if video_div:
                    video_tag = video_div.find('video')
                    if video_tag:
                        video_src = video_tag.get('src')
                        lista_videos.append((text, video_src))
                    else:
                        lista_videos.append((text, 'null'))
                else:
                    lista_videos.append((text, 'null'))

                driver.close()
                driver.switch_to.window(driver.window_handles[0])

    driver.quit()

    df_videos = pd.DataFrame(lista_videos, columns=['Palavra', 'Link'])
    df_videos['Instituicao'] = 'Spread the Sign'

    return df_videos

arquivo_csv = 'caminho/do/arquivo.csv'  # Substitua pelo caminho correto do seu arquivo CSV
df_videos = obter_videos_site(arquivo_csv)

nome_arquivo = 'spreadthesign.csv'
formato = {
    'Palavra': str,
    'Link': str,
    'Instituicao': str
}

with open(nome_arquivo, 'w', newline='', encoding='utf-8') as arquivo_csv:
    escritor = csv.DictWriter(arquivo_csv, fieldnames=formato.keys())
    escritor.writeheader()
    for _, linha in df_videos.iterrows():
        escritor.writerow({campo: formato[campo](valor) for campo, valor in linha.items()})

print("Dados salvos em arquivo CSV:", nome_arquivo)
