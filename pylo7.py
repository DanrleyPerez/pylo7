import pandas as pd
import requests
import re
import ast
import matplotlib.pyplot as plt
import numpy as np


def indice_palavra_string(arquivo, palavra):                #encontra o índice de uma plavra dentro da página
    indice = re.search(palavra, arquivo)
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


def numero_de_paginas(produto, qte_produtos):

    if qte_produtos == 0:
        qte_produtos = quantidade_de_produtos(produto)
        if qte_produtos > 2000:
            qte_produtos = 2000

    else:
        pass

    if int(qte_produtos) % 39 == 0:
        numero_paginas = int(qte_produtos / 39)

    elif int(qte_produtos) < 39:
        numero_paginas = 1
    else:
        numero_paginas = int(qte_produtos / 39) + 1
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
    todas_paginas = []
    numero_paginas = numero_de_paginas(produto_interesse, espaco_amostral)
    if numero_paginas > 50:
        numero_paginas = 50
    for i in range(1, numero_paginas + 1):
        print("página:", i)
        conteudo_pagina = captura_pagina(produto_interesse, i)
        produtos_pagina = produtos_da_pagina(conteudo_pagina)
        todos_produtos.append(produtos_pagina)
        todas_paginas.append(conteudo_pagina)
    produtos_em_lista = tratamento_string(str(todos_produtos), espaco_amostral)
    print(len(produtos_em_lista), " produtos analizados")

    return produtos_em_lista, numero_paginas, todas_paginas[0]


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


def trechos_pagina(lista_trechos_inicio, trecho_parada, pagina):
    lista_trechos = []

    for trecho in lista_trechos_inicio:
        indice_inicio_trecho = pagina.find(trecho)

        trecho_total = ""
        if indice_inicio_trecho == -1:
            pass
        else:
            indice_href_fim = pagina.find(trecho_parada, indice_inicio_trecho + 10)
            if indice_href_fim == -1:
                pass
            else:
                for l in range(indice_inicio_trecho + 1, indice_href_fim):

                    trecho_total = trecho_total + str(pagina[l])

                lista_trechos.append(trecho_total)
    return lista_trechos


class VendasDeSucesso:
    def __init__(self, termo, espaco_amostral=0):
        """

        :param termo: O termo do produto ao qual deseja encontrar as informações.
        :param espaco_amostral: numero de produtos que deseja, default = 0 : trás
        todos os produtos encontrados.

        """
        self.termo = termo
        self.espaco_amostral = espaco_amostral
        produtos, self.numero_de_paginas, self.primeira_pagina = todos_produtos(self.termo, espaco_amostral)
        self.todos_os_produtos = pd.DataFrame(produtos)

    def numero_paginas(self):
        return self.numero_de_paginas

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

    def links_cada_produto(self):
        """

        :return: Lista com os links das páginas dos 20 primeiros produtos encontrados.
        """
        produtos = []
        hrefs_todos_produtos = []
        links_produtos = []

        for i in range(20):
            produtos.append(self.todos_os_produtos['name'][i])
        pagina = self.primeira_pagina

        for produto in produtos:
            produto_formatado = produto.replace(" - ", "-").replace(" ", "-").lower()
            if produto_formatado.find("\\x") == -1:
                href_na_pagina = "'/" + produto_formatado
                hrefs_todos_produtos.append(href_na_pagina)
            else:
                produto_formatado = produto_formatado.split("\\x", 1)[0]
                href_na_pagina = "'/"+produto_formatado
                hrefs_todos_produtos.append(href_na_pagina)
        links_produtos = trechos_pagina(hrefs_todos_produtos, "'", pagina)

        for i in range(len(links_produtos)):
            links_produtos[i] = "https://www.elo7.com.br" + links_produtos[i].strip("\\")
        return links_produtos

    def tags_de_sucesso(self):
        links_por_produto = self.links_cada_produto()
        n=0
        lista_trechos_com_tags =[]

        for pagina in links_por_produto:
            n+=1
            req = requests.request('GET', pagina)
            pagina = req.content.decode('UTF-8')

            trecho_com_tags = trechos_pagina('<h2>Tag', "</a></li></ol>", pagina)

            lista_trechos_com_tags.append(trecho_com_tags)


    def media_primeiros_10(self):

        media_primeiros10 =self.todos_os_produtos[:10].median()
        print(media_primeiros10)
        return round(media_primeiros10, 3)

    def preco_mediano(self):
        return round(self.todos_os_produtos['price'].median(), 1)

    def preco_medio(self):
        return round(self.todos_os_produtos['price'].mean(), 1)

    def info_gerais(self):
        return round(self.todos_os_produtos['price'].describe(), 1)

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

    prod = VendasDeSucesso(termo, qte_produtos)
    print(prod.numero_paginas())

if __name__ == '__main__':
    run()


