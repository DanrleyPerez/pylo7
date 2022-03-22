import pandas as pd
from pytrends.request import TrendReq
import requests
import re
import ast


def indice_palavra_string(arquivo, palavra):
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


def produtos_da_pagina(pagina):
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


def todos_produtos(produto_interesse):
    todos_produtos = []

    numero_paginas = numero_de_paginas(produto_interesse)
    if numero_paginas > 51:
        numero_paginas = 51

    for i in range(0, numero_paginas):
        print("página, ", i)
        conteudo_pagina = captura_pagina(produto_interesse, i)
        produtos_pagina = produtos_da_pagina(conteudo_pagina)

        todos_produtos.append(produtos_pagina)

    produtos_em_lista = tratamento_string(str(todos_produtos))
    print(len(produtos_em_lista), " produtos encontrados")
    return produtos_em_lista


def tratamento_string(produtos):
    prod = produtos.strip("[]")
    prod = prod.split("}")
    list_produtos_organizada = []
    n = 0
    conc = ""
    dict_produtos_organizada = {}
    for a in prod:
        n += 1

        if n == len(prod):
            pass
        else:
            a = str(a).strip("'")
            a = a.strip("[") + "}"
            a = a.replace("'", "")
            a = a.replace("]", "")
            a = a.replace("[", "")
            if a[0] == ",":
                a = a.replace(",", "", 1)
            a = a.replace("]", "", len(a))
            a = a.replace("'[", "", 1)
            qte_aspas = a.count('"')
            if qte_aspas > 10:
                a = a.replace('"', "", 8)
                qte_aspas = a.find('"')
                if qte_aspas > 10:
                    a = a.replace('"', "", 8)

            try:
                a = ast.literal_eval(a)
                list_produtos_organizada.append(a)
            except:
                pass
    return list_produtos_organizada


class VendasDeSucesso:
    def __init__(self, termo):
        self.termo = termo
        self.todos_os_produtos = todos_produtos(self.termo)

    def produtos_de_sucesso(self):
        return self.todos_os_produtos

    def tags_de_sucesso(self):
        pass

    def preco_mediano(self):
        pd_produtos = pd.DataFrame(self.todos_os_produtos)
        preco_mediano = pd_produtos['price'].median()
        return preco_mediano

    def preco_medio(self):
        pd_produtos = pd.DataFrame(self.todos_os_produtos)
        preco_medio = pd_produtos['price'].mean()
        return preco_medio

    def info_gerais(self):
        pd_produtos = pd.DataFrame(self.todos_os_produtos)
        info_gerais = pd_produtos['price'].describe()
        return info_gerais



def run():
    termo = input(" Digite o Produto que busca ")
    prod = VendasDeSucesso(termo)
    informacoes_gerais = prod.info_gerais()
    print(informacoes_gerais)



if __name__ == '__main__':
    run()

"""
pytrends = TrendReq(hl='en-US', tz=360)

kw_list = ["love", "hate"]
pytrends.build_payload(kw_list, cat=0, timeframe='today 5-y', geo='', gprop='')

df = pytrends.interest_over_time()
print(df[df.love > 50])"""

