# -*- coding: utf-8 -*-
# aluno: Eric Inohira Uchimuar
# Email: euchimura@gmail.com

import xml.etree.cElementTree as ET
import pprint
import json
import pprint
import re
import codecs
from unicodedata import normalize
##regiao da grande Vitoria mais redondezas, Espirito Santo
##(node(-20.3264, -40.3602, -20.2399,-40.2081);<;);out meta; - 21/09/2017
lower = re.compile(r'^([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
CREATED = ["version", "changeset", "timestamp", "user", "uid","id","lat","lon","k","v", "ref"]
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
SECUNDARIO = ["k","v","changeset","uid","generator","timestamp","lon","version","user","lat","osm_base","id"]

# Inicialmente verificamos as Tags existentes no OSM e imprimimos em um arquivo
# saida.json
# também gravamos a quantidade de cada Tags.
# esses dados utilizamos para verificarmos quais tags realmente vale a pena
# explorar
# baseado no exericio 1 do módulo do Openstreet Maps
def count_tags(filenameEntrada):
    varOutput = {}
    saidaSecundario = {}
    varArquivoEntrada = ET.iterparse(filenameEntrada,events=("start",))
#    print ("arquivo", filenameEntrada)
    contador = 0
    k = []
    v = []
    for event,elem in varArquivoEntrada:
        contador = contador + 1
        if elem.tag in varOutput.keys():
            varOutput[elem.tag]=varOutput[elem.tag] + 1
            a = elem.keys()
            bp = varOutput[elem.tag + "_primario"]
            varOutput[elem.tag + "_primario"] = list(set(a)|set(b))
        else:
            varOutput[elem.tag] = 1
            varOutput[elem.tag + "_primario"] = elem.keys()
        #

        for secundario in elem.iter():
            if "k" in secundario.keys():
#                print("secundario k : ", secundario.attrib['k'])
                k = list(set(k)|set([remover_acentos(secundario.attrib['k'])]))
#                print ("k: ", secundario.attrib['k'])
#
            if "v" in secundario.keys():
#                print("secundario v: ", secundario.attrib['v'])
                v = list(set(v)|set([remover_acentos(secundario.attrib['v'])]))
#                print ("v: ", secundario.attrib['v'])
            pos = elem.tag +"_secundario"
#
            if pos in varOutput.keys():
                a = secundario.keys()
                b = varOutput[pos]
                varOutput[pos] = list(set(a)|set(b))
            else:
                 varOutput[pos] = secundario.keys()
#    print ("k: ", k)
#    print ("v: ", v)
    varOutput['valoresk'] = {}
    varOutput['valoresk'] = k
    varOutput['valoresv'] = {}
    varOutput['valoresv'] = v

    return varOutput

## Função que acha os possíveis dados que precisam limpar.
## como entrada recebe o arquivo a ser auditado e um dicionário de caracteres
caract = {".",":",";", "!","@","$","%","&","*","?","/","\\","|","#"}
def verificaDados(filenameEntrada, caracteres):
    varOutput = {}
    saidaSecundario = {}
    varArquivoEntrada = ET.iterparse(filenameEntrada,events=("start",))
#    print ("arquivo", filenameEntrada)
    contador = 0
    k = []
    v = []
    for event,elem in varArquivoEntrada:

        for secundario in elem.iter():
            if "k" in secundario.keys():
#                print("secundario k : ", secundario.attrib['k'])
                valorK = remover_acentos(secundario.attrib['k'])
                for especial in caracteres:
                    if valorK.find(especial)>=0:
                       k = list(set(k)|set([remover_acentos(secundario.attrib['k'])]))
                       break

#                print ("k: ", secundario.attrib['k'])
#
            if "v" in secundario.keys():
#                print("secundario v: ", secundario.attrib['v'])
                valorV = remover_acentos(secundario.attrib['v'])
                for especial in caracteres:
                    if valorV.find(especial) >=0:
                        v = list(set(v)|set([remover_acentos(secundario.attrib['v'])]))
                        break
#                print ("v: ", secundario.attrib['v'])
            pos = elem.tag +"_secundario"
#
            if pos in varOutput.keys():
                a = secundario.keys()
                b = varOutput[pos]
                varOutput[pos] = list(set(a)|set(b))
            else:
                 varOutput[pos] = secundario.keys()
#    print ("k: ", k)
#    print ("v: ", v)
    varOutput['valoresk'] = {}
    varOutput['valoresk'] = k
    varOutput['valoresv'] = {}
    varOutput['valoresv'] = v

    return varOutput





# funçao que retorna o primeiro levantamento de tags e tipos
def primeiroLevantamento():

    tags = count_tags('Vitoria.txt')
    with open('saida4.json', 'w') as f: f.write(
    json.dumps(tags,indent=4, sort_keys=True))

## segundo levantamento para verificar os valores que deverão ser limpos
def segundoLevantamento():
    tags = verificaDados("Vitoria.osm",caract)
    with open('saida5.json', 'w') as f: f.write(json.dumps(tags,indent=4, sort_keys=True))

#Função que trata cada TAG e retorna um dicionário com as tags e seus respectivos
#valores. Baseado no exercicio do módulo de Exploração do OSM
def shape_element(element,mapaInicio, mapaFim):
#    print("entrou shape")
    node = {}
    node["created"] = {}
    posicao = []
    contadorProblemas = 0
    contadorPontos = 0
    if element.tag == "node" or element.tag == "way":
        # YOUR CODE HERE
        for chave in element.keys():
            valor = element.attrib[chave]
            node["type"] = element.tag
            if chave in CREATED:
                node["created"][chave] = valor
            else:
                if chave =="lat" or chave =="lon":
                #verifica se já existe a posicao e cria
                    if 'pos' not in node.keys():
                        node["pos"] = [0.0,0.0]
                    if chave =="lat":
                        node["pos"][0] = float(valor)
                    else:
                        node["pos"][1] = float(valor)
                else: node[chave] = valor

            for secundario in element.iter("tag"):
#            for secundario in element.iter:
                if "k" in secundario.keys() or "v" in secundario.keys():
                    chaveSecundaria = secundario.attrib['k']
                    valSecundaria = secundario.attrib['v']
                    ## remove os acentos e cedilhas
                    valSecundaria = remover_acentos(valSecundaria)
#                    valSecundaria = CorrigeLogradouro(valSecundaria,mapaInicio,mapaFim)

                if not(problemchars.match(valSecundaria)):
                    if chaveSecundaria.count(":")<2:
                        if chaveSecundaria.startswith("addr:"):
                            if is_street_name(chaveSecundaria):
                                valSecundaria = CorrigeLogradouro(valSecundaria,mapaInicio,mapaFim)

                            if "address" not in node:
                                node["address"] = {}
                #            print("entrou",chaveSecundaria[len("addr:"):])
                            node["address"][chaveSecundaria[len("addr:"):]] = valSecundaria
                        else:##incluido após segunda revisao do projeto
                            if chaveSecundaria.startswith ("pt:"):
                                if "pontoReferencia" not in node:
                                    node["pontoReferencia"] = {}
                                node["pontoReferencia"][chaveSecundaria[len("pt:"):]] = valSecundaria
                            ## fim da inclusão  após segunda revisao
                            else:
                                if chaveSecundaria.count(":")==0:
                                    node[chaveSecundaria] = valSecundaria
                                else:
                                    node[chaveSecundaria] = {}
                                    ponteiro = chaveSecundaria.find(":")
                                    node[chaveSecundaria][chaveSecundaria[0:ponteiro]] = valSecundaria
                    else:
                        contadorPontos = contadorPontos + 1
                        node['contPontos'] = contadorPontos
                else:
                    contadorProblemas = contadorProblemas + 1
                    node['contProblemas'] = contadorProblemas
        return node
    else:
        return None
#    node["contProblemas"] = contadorProblemas
#    node["contPontos"] = contadorPontos
    return node
# Mofidificado, 05/10/2017 após revisão.
# funçao que percorre todos os dados e imprime na tela os tipos de rua que não estao no vetor "expected"
expected = ["Rua", "Avenida", "Alameda", "Edificio","Rodovia","Ladeira","Praca","Beco","Escadaria",
            "Travessa","Rampa","Estrada","Servidao","Viaduto"]
def auditoria(file_in,expected):

    for _, element in ET.iterparse(file_in):
        for chave in element.keys():
            for secundario in element.iter("tag"):
                if "k" in secundario.keys() or "v" in secundario.keys():
                    chaveSecundaria = secundario.attrib['k']
                    valSecundaria = secundario.attrib['v']
                    valSecundaria = remover_acentos(valSecundaria)
                    if not(problemchars.match(valSecundaria)):
                        if chaveSecundaria.startswith("addr:street"):
#                            print ("valorv: ", valSecundaria)
                            for tipo in expected:
                                flag = valSecundaria.find(tipo)
#                                print ("flag:",flag)
                                if flag>=0:
#                                    print("entrou break")
                                    break
                            if flag < 0:
                               print(valSecundaria)






# fim modificação


# processa o mapa - baseado no exercicio do OSM
# o Processa mapa trava após 1,2 milhao de interações por "falta de memoria"
def process_map(file_in,mapaInicio, mapaFim, pretty = False):
    # You do not need to change this file
    file_out = "{0}.json".format(file_in)
    data = []
    contador = 0
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            contador = contador +1
            el = shape_element(element,mapaInicio,mapaFim)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
#
    return data

# como após 1,2 milhoes de inserções no arquivo json o programa acusa falta de memoria,
# faremos a inserção direto em um BD

def get_db():
    # For local use
    from pymongo import MongoClient
    client = MongoClient('localhost:27017')
    # 'examples' here is the database name. It will be created if it does not exist.
    print(client.examples)
    db = client.osmdata
    return db

def add_dados(db,data):
    # Changes to this function will be reflected in the output.
    # All other functions are for local use only.
    # Try changing the name of the city to be inserted
    db.osmdata.insert(data)

# 2.143.110 interações
# tamanho do bd: 0.066gb com o comando show dbs
#processa os dados do OSM e insere diretamente no BD
# segunda rodada utilizando o python 3
#  3.356.574 interações - erro de memoria no ElementTree.py, line 1268

def process_map_MogoDb(file_in):
    # You do not need to change this file
#    file_out = "{0}.json".format(file_in)
    data = []
    contador = 0
    bd = get_db()

#    with codecs.open(file_out, "w") as fo:
    for _, element in ET.iterparse(file_in):
        contador = contador +1
        print("interacoes:", contador)
        el = shape_element(element)
        if el:
            add_dados(bd,el)
    print("Inserido no BD com sucesso")

## Função de auxilio. remove os acentos e o cedilha
def remover_acentos(txt, codif='utf-8'):
    txt = txt.encode('utf-8')
    return normalize('NFKD', txt.decode(codif)).encode('ASCII','ignore')

## modificado dia 03/10 após a segunda revisão
## funcao auxiliar: Função booleana que Verifica se o elemento é uma rua
# baseado nos exercicios da udacity sobre o OSM
def is_street_name(elem):
    return (elem == "addr:street")


fixed_street_names = []
street_types = re.compile(r'\b\S+\.?$', re.IGNORECASE)

street_mapping = {"Av.": "Avenida",
                   "R.": "Rua",
                   "R:": "Rua",
                   "Al.": "Alameda",
                   "Rod.": "Rodovia",
                   }
# função auxiliar. Audita o tipo as ruas
def audit_street_type(street_name):
    match = street_types.search(street_name)
    if match:
        street_type = match.group()
        if street_type not in expected:
            return update_street_name(street_name, street_mapping)
    return street_name


def update_street_name(name, mapping):
    """Replace and return new name from street name mapping."""
    for key in mapping.iterkeys():
        if re.search(key, name):
            name = re.sub(key, mapping[key], name)
            fixed_street_names.append(name)

    return name

## fim modificação do  dia 03/10 após a segunda revisão

## função de auxilio. Acerta os nomes de ruas, alamedas e avenidas
# os vetores mapeamentoInicio serve para mudar a sigla somente se esta estiver no inicio como por Exemplo:
# Ex: "R. Ludwik Macal"
# em alguns casos o R. pode aparecer como abreviação no meio do nome e não pode ser modificado pela função:
#Ex: "Beco Gumercindo R. de Souza ==> neste caso, o "R." não significa Rua.
mapInicio = { "R.": "Rua",
             "R:": "Rua",
            "Av ": "Avenida",
            "Av.": "Avenida",
            "Al.": "Alameda"
            }

mapFim = {
            "Av.": "Avenida",
            "Av ": "Avenida",
            "Rod.":"Rodovia",
            "Rod" : "Rodovia",
            "Ed." : "Edificio"
            }

def CorrigeLogradouro (nome, mapeamentoInicio, mapeamentoFim):

    for a in mapeamentoInicio.keys():
        if nome.startswith(a):
            nome = nome.replace(a,mapeamentoInicio[a],1)
#
    for a in mapeamentoFim.keys():
        resultado = re.search(a,nome)
        if resultado:
            nome = nome.replace(a,mapeamentoFim[a])
    return nome

##execuçaof
if __name__ == "__main__":

#    primeiroLevantamento()
#    segundoLevantamento()
#     auditoria("Vitoria.osm",expected)
     data = process_map("Vitoria.osm", mapInicio, mapFim, False)
#    process_map_MogoDb("Vitoria.txt")
#"Beco Gumercindo R. de Souza
