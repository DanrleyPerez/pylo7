import pandas as pd
import requests
import re
import ast
import matplotlib.pyplot as plt
import numpy as np


def indice_palavra_string(arquivo, palavra):                #encontra o índice de uma plavra dentro da página
    indice = re.search(str(palavra), arquivo)
    indice = indice.start()
    return indice


def quantidade_de_produtos(termo_de_interesse):
    req = requests.request('GET', """https://www.elo7.com.br/lista/""" + termo_de_interesse + """?pageNum=1""")
    conteudo = str(req.content)
    n = 0
    qte_produtos = ""
    index = indice_palavra_string(conteudo, "produtos")
    for letra in conteudo:
        n += 1
        if index - 15 < n <= index:
            try:
                int(letra)
                qte_produtos = qte_produtos + letra
            except:
                pass
    print("quantidade de produtos: listados ", qte_produtos)
    return int(qte_produtos)


def numero_de_paginas(produto):
    concate = quantidade_de_produtos(produto)
    numero_paginas = int(concate)/39
    if int(concate) % 39 == 0:
        numero_paginas = int(numero_paginas)
    elif int(concate) < 39:
        numero_paginas = 1
    else:
        numero_paginas = int(numero_paginas + 1)
    return numero_paginas


def captura_pagina(termo_interesse, n_pagina):
    req = requests.request('GET', """https://www.elo7.com.br/lista/"""+termo_interesse+"""?pageNum="""+str(n_pagina)+"""""")
    conteudo = str(req.content)
    return conteudo


def produtos_da_pagina(pagina):                 # função que que determina onde começa e onde termina a lista de produtos da página
    indice = indice_palavra_string(pagina, "products") + len("products") + 2
    fim = len(pagina)
    conc = ""
    cont = 0
    for e in range(indice, fim):
        cont += 1
        if pagina[e-1] == ']' and pagina[e-7] != 'I' and pagina[e-6] != 'm' and pagina[e-5] != 'a' and pagina[e-4] != 'g':
            break
        else:
            conc = conc + pagina[e]
    return conc


def todos_produtos(produto_interesse, espaco_amostral):
    todos_produtos = []
    numero_paginas = numero_de_paginas(produto_interesse)
    if numero_paginas > 51:                                  # o máximo de paginas do elo 7 é 51.
        numero_paginas = 51
    for i in range(0, numero_paginas):
        print("página:", i)
        conteudo_pagina = captura_pagina(produto_interesse, i)
        produtos_pagina = produtos_da_pagina(conteudo_pagina)
        todos_produtos.append(produtos_pagina)
    produtos_em_lista = tratamento_string(str(todos_produtos), espaco_amostral)
    print(len(produtos_em_lista), " produtos analizados")
    return produtos_em_lista


def tratamento_string(produtos, espaco_amostral):
    """
    Trata a string para uma lista de produtos
    :param produtos: string com a lista de todos os produtos
    :param espaco_amostral: numero de produtos para analize
    :return: lista formatada dos produtos
    """
    prod = produtos.strip("[]")
    prod = prod.split("}")
    list_produtos_organizada = []
    n = 0
    for a in prod:
        n += 1
        if n == len(prod):
            pass
        else:
            a = str(a).strip("'").strip("[") + "}".replace("'", "").replace("]", "").replace("[", "")
            if a[0] == ",":
                a = a.replace(",", "", 1)
            a = a.replace("]", "", len(a)).replace("'[", "", 1)
            qte_aspas = a.count('"')
            if qte_aspas > 10:
                a = a.replace('"', "", 8)
                qte_aspas = a.find('"')
                if qte_aspas > 10:
                    a = a.replace('"', "", 8)
            try:
                if espaco_amostral != 0:
                    if n <= espaco_amostral:
                        a = ast.literal_eval(a)
                        list_produtos_organizada.append(a)
                else:
                    a = ast.literal_eval(a)
                    list_produtos_organizada.append(a)
            except:
                pass
    return list_produtos_organizada


class VendasDeSucesso:
    def __init__(self, termo, espaco_amostral=0):
        """

        :param termo: O termo do produto ao qual deseja encontrar as informações.
        :param espaco_amostral: numero de produtos que deseja, default = 0 : trás
        todos os produtos encontrados.

        """
        self.termo = termo
        self.espaco_amostral = espaco_amostral
        self.todos_os_produtos = pd.DataFrame(todos_produtos(self.termo, espaco_amostral))

    def produtos(self):
        return self.todos_os_produtos

    def qte_palavras(self):
        """
        :return: lista da quantidade de palavras por anuncio em ordem de relevancia, do mais relevante para o menos
        relevante.

        """
        qtd_palavras = []
        for name in self.todos_os_produtos['name']:
            palavras = name.split(" ")
            qtd_palavras.append(len(palavras))
        return qtd_palavras

    def tags_de_sucesso(self):
        pass

    def preco_mediano(self):
        return self.todos_os_produtos['price'].median()

    def preco_medio(self):
        return self.todos_os_produtos['price'].mean()

    def info_gerais(self):
        return self.todos_os_produtos['price'].describe()

    def plots(self):
        preco_maximo = self.todos_os_produtos['price'].max()
        graph = self.todos_os_produtos.plot.bar(title="Valor dos principais produtos por ordem de relevancia", xticks=self.todos_os_produtos.index, yticks=self.todos_os_produtos['price'])
        graph.set_xlabel("Mais relevantes < -------- Relevância --------- > Menos relevantes")
        graph.set_ylabel("Preço")
        plt.yticks(np.arange(0, preco_maximo, 10))
        if len(self.todos_os_produtos) > 50:
            plt.xticks(np.arange(0, len(self.todos_os_produtos), len(self.todos_os_produtos)/10))
        else:
            plt.xticks(np.arange(0, self.espaco_amostral))
        plt.show()


def run():
    termo = input(" Digite o Produto que busca ")
    qte_produtos = input(" Digite a quantidade de Produtos que deseja analizar")
    if qte_produtos == "":
        qte_produtos = 0
    else:
        qte_produtos = int(qte_produtos)
    prod = VendasDeSucesso(termo, qte_produtos)
    prod.plots()
    produtos =prod.produtos()
    informacoes_gerais = prod.info_gerais()
    print(produtos)
    print(informacoes_gerais)


if __name__ == '__main__':
    run()


