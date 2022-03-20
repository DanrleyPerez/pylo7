import pandas as pd
from pytrends.request import TrendReq
import requests
import re
import ast


def indice_palavra_string(arquivo, palavra):
    indice = re.search(str(palavra), arquivo)
    indice = indice.start()
    return indice


def quantidadeDeProdutos(termo_de_interesse):
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
    print("quantidade de produtos: ", qte_produtos)
    return int(qte_produtos)


def numeroDePaginas(produto):

    concate = quantidadeDeProdutos(produto)

    numero_paginas = int(int(concate)/39)
    return numero_paginas


def captura_pagina(termo_interesse, n_pagina):

    req = requests.request('GET', """https://www.elo7.com.br/lista/"""+termo_interesse+"""?pageNum="""+str(n_pagina)+"""""")
    conteudo = str(req.content)
    return conteudo


def produtosDaPagina(pagina):
    indice = indice_palavra_string(pagina, "products") + len("products") + 2
    fim = len(pagina)
    print("caracteres pagina:",fim)
    conc = ""
    numero_aspas = 0
    armazenamento = 0
    cont = 0
    terceira_aspas =[]
    for e in range(indice, fim):
        cont += 1


        if pagina[e-1] == ']' and pagina[e-7] != 'I' and pagina[e-6] != 'm' and pagina[e-5] != 'a' and pagina[e-4] != 'g':
            break

        else:
            if numero_aspas == 2 and pagina[e] != ":" and pagina[e] != ",":
                conc = conc + pagina[e]
                armazenamento = len(conc) - 2
                numero_aspas = 0
                terceira_aspas = True

            elif terceira_aspas == True and pagina[e] == '"':
                conc = conc + pagina[e]
                armazenamento = len(conc) - 1
                numero_aspas = 0
                terceira_aspas = False

            elif numero_aspas == 2 and pagina[e] == ":" or pagina[e] == ",":
                conc = conc + pagina[e]
                numero_aspas = 0
            else:
                conc = conc + pagina[e]
            if pagina[e] == '"':
                numero_aspas += 1

        if armazenamento != 0:
            conc = conc[:armazenamento] + "'" + conc[armazenamento: +1]


    return conc


def todosProdutos():
    todos_produtos = []
    produto_interesse = input()
    numero_paginas = numeroDePaginas(produto_interesse)
    print("numero de paginas", numero_paginas)
    for i in range(1, 50):
        print("pagina = ", i)
        conteudo_pagina = captura_pagina(produto_interesse, i)
        produtos_pagina = produtosDaPagina(conteudo_pagina)

        todos_produtos.append(produtos_pagina)


    return todos_produtos


class vendasDeSucesso():

    def produtosDeSucesso(self):
        produtos = todosProdutos()
        return produtos
        # for i in range(self.quantidade_produtos):
        #     primeirosProd = self.todos_produtos[0][i]

    def tags_de_sucesso(self):
        pass


def run():
    venda_interesse1 = vendasDeSucesso()
    produtos_relevantes = venda_interesse1.produtosDeSucesso()

run()
"""
pytrends = TrendReq(hl='en-US', tz=360)

kw_list = ["love", "hate"]
pytrends.build_payload(kw_list, cat=0, timeframe='today 5-y', geo='', gprop='')

df = pytrends.interest_over_time()
print(df[df.love > 50])"""

