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

def obter_videos_site():
        
        urls_categoria = gerar_vetor_urls_cada_categoria(arquivo_csv)
        
        options = Options()
        options.headless = True #Ativado para que o navegador não seja aberto.

        driver = webdriver.Chrome(options=options)

        lista_videos = []

        for url in urls_categoria:
            driver.get(url)
            time.sleep(5)  # delay para carregar a página

            html = driver.page_source  # pega o html
            soup = BeautifulSoup(html, 'html.parser')  # organiza

            # Encontrar todas as divs com a classe search-result-title (onde estão as palavras)
            divs = soup.find_all('div', class_='search-result-title')

            for div in divs:
                atags = div.find_all('a')  # atags = todos os "a"

                for a in atags:
                    # Excluir a tag <small> do conteúdo de cada "a", pois não queremos "Substantivo", "verbo", etc.
                    small_tag = a.find('small')
                    if small_tag:
                        small_tag.decompose()

                    # Extrair o texto do elemento 'a'
                    text = a.get_text(strip=True) 
                    # strip=True remove espaços em branco extras no início e no final do texto.

                    # Remover caracteres de controle e normalizar os caracteres Unidecode
                    text = "".join(ch for ch in text if unicodedata.category(ch)[0] != "C")
                    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')

                    # Obter o link do elemento 'a'
                    href = a['href']

                    # Abrir o link em uma nova aba
                    driver.execute_script("window.open(arguments[0], '_blank');", href)
                    time.sleep(1)  # Aguardar um segundo após o clique

                    # Alternar para a nova aba
                    driver.switch_to.window(driver.window_handles[-1])

                    # Obter o HTML da nova página
                    video_html = driver.page_source
                    video_soup = BeautifulSoup(video_html, 'html.parser')

                    # Encontrar a div que contém o vídeo
                    video_div = video_soup.find('div', class_='col-md-7')

                    if video_div:
                        # Verificar se há um elemento de vídeo presente
                        video_tag = video_div.find('video')
                        if video_tag:
                            # Obter o valor do atributo 'src' do vídeo
                            video_src = video_tag.get('src')
                            lista_videos.append((text, video_src))
                            print(text, video_src)
                        else:
                            lista_videos.append((text, 'null'))
                    else:
                        lista_videos.append((text, 'null'))

                    # Fechar a nova aba e voltar para a aba anterior
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])

        driver.quit()
        print(lista_videos)
        df_videos = pd.DataFrame(lista_videos, columns=['Palavra', 'Link'])
        df_videos['Instituicao'] = 'Spread the Sign' 

        return df_videos

arquivo_csv = 'links_categorias_spreadthesign.csv'
df_videos = obter_videos_site()

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', None)
print(df_videos)

# Salvar DataFrame em um arquivo CSV
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
