#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Classe que realiza o download e chama as validações
"""

import zipfile
import os
import shutil
import logging
import requests
import numpy as np
import pandas as pd

from ..business import ValidadorTransacoes

LOGGER = logging.getLogger('api-backend')

URL = 'https://hackathon.dtplabs.in/uploads/-/system/personal_snippet/1/323ab37b362fbca737b2197edca6645a/transacoes.zip'
PASTA_TEMP = 'temp'
ZIP_FILE_NAME = 'transacoes.zip'
FILE_NAME = 'transacoes.csv'

def init():
    """Inicializa a aplicação
    """

    download()
    data = read()
    valida(data)

def valida(data):
    """Valida as transações
    """

    ValidadorTransacoes.valida(data)

def download():
    """
        Faz o download do aquivo, se a pasta já existir, apaga...
    """
    return download_and_extract(URL, PASTA_TEMP, ZIP_FILE_NAME)

def download_and_extract(url, pasta_temporaria, file_name):
    """
        Faz o download do arquivo:
    """
    if os.path.exists(pasta_temporaria):
        shutil.rmtree(pasta_temporaria)

    LOGGER.info('Iniciando download do arquivo.')
    # faz o dowload do arquivo em formato binario
    req = requests.get(url)
    LOGGER.info('Finalizado!')

    # abre o arquivo e escreve o conteudo
    with open(file_name, "wb") as code:
        code.write(req.content)

    LOGGER.info('Descompactando o arquivo zip.')
    # descompacta e grava na <pasta>
    try:
        with zipfile.ZipFile(file_name) as zip_file:
            zip_file.extractall(pasta_temporaria)
            zip_file.close()
        arquivo_corrompido = False
    except zipfile.BadZipfile as ex:
        print(ex)
        arquivo_corrompido = True

    if arquivo_corrompido:
        return False

    LOGGER.info('Arquivo descompatado.')
    return True

def read():
    """Lê os dados do arquivo
    """
    conversor_timestamp = lambda x: pd.to_datetime(x)

    LOGGER.info('Iniciando a leitura dos registros do arquivo CSV')
    data = pd.read_csv(PASTA_TEMP + '/' + FILE_NAME, delimiter=";", dtype={'VALOR' : np.float32}, parse_dates=['TIMESTAMP'], date_parser=conversor_timestamp)
    LOGGER.info('Finalizado!')
    return data
