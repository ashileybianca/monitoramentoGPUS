import csv

def remover_linhas_nulas(caminho_arquivo_entrada, caminho_arquivo_saida):
    linhas = []
    with open(caminho_arquivo_entrada, 'r') as arquivo:
        leitor = csv.reader(arquivo)
        cabecalhos = next(leitor)  
        linhas.append(cabecalhos)
        for linha in leitor:
            if not any(campo.lower() == 'null' for campo in linha):
                linhas.append(linha)
    
    with open(caminho_arquivo_saida, 'w', newline='') as arquivo:
        escritor = csv.writer(arquivo)
        escritor.writerows(linhas)

remover_linhas_nulas('spreadthesign.csv', 'links_videos_spreadthesign.csv')
