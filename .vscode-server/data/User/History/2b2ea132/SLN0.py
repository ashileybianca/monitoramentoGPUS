import csv

def remover_linhas_nulas(caminho_arquivo_entrada, caminho_arquivo_saida):
    linhas = []
    with open(caminho_arquivo_entrada, 'r') as arquivo:
        leitor = csv.reader(arquivo)
        cabecalhos = next(leitor)  # Lê os cabeçalhos do arquivo CSV
        linhas.append(cabecalhos)
        for linha in leitor:
            if not any(campo.lower() == 'null' for campo in linha):
                linhas.append(linha)
    
    with open(caminho_arquivo_saida, 'w', newline='') as arquivo:
        escritor = csv.writer(arquivo)
        escritor.writerows(linhas)

# Exemplo de uso:
remover_linhas_nulas('dados.csv', 'dados_sem_nulos.csv')
