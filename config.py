# config.py

SEARCH_TERMS = ['Feiticeiro', 'umbanda', 'candomble']
OUTPUT_FILE = 'Output20240728.csv'

# This dictionnary was constructed by finding the ID of each
# newspaper that is needed. To add a new newspaper, please find 
# the appropriate ID in the URL after making a search here:
# https://memoria.bn.gov.br/hdb/periodico.aspx in the newspaper.
NEWSPAPER_ID_DICT = {'030015' : 'Jornal do Brasil',
                    '103730' : 'Gazeta de Notícias',
                    '029033' : 'Diário de Pernambuco',
                    '221961' : 'Diário da Noite',
                    '749664' : 'Gazeta do Rio de Janeiro'}

# Please input the ID of the newspaper you would like to search from
# NOTE: the code can search from one newspaper at a time
NEWSPAPER_ID = '030015'
print("config.py loaded")