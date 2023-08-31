import csv

def remover_linhas_nulas(caminho_arquivo):
    linhas = []
    with open(caminho_arquivo, 'r') as arquivo:
        leitor = csv.reader(arquivo)
        cabecalhos = next(leitor)  # Lê os cabeçalhos do arquivo CSV
        linhas.append(cabecalhos)
        for linha in leitor:
            if not any(campo.lower() == 'null' for campo in linha):
                linhas.append(linha)
    
    with open(caminho_arquivo, 'w', newline='') as arquivo:
        escritor = csv.writer(arquivo)
        escritor.writerows(linhas)

# Exemplo de uso:
remover_linhas_nulas('spreadthesign.csv')

print("Dados salvos em arquivo CSV:", nome_arquivo)

arquivo_csv = 'links_categorias_spreadthesign.csv'
nome_arquivo = 'spreadthesign.csv'
obter_videos_site(arquivo_csv, nome_arquivo)
