#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Classe que realiza as validações
"""

from app.util import DownloadInput
import numpy as np
import pandas as pd
import logging

from ..database import MongoConnect

LOGGER = logging.getLogger('api-backend')

def persistir_erros(data,codigo):
    data.loc[:,'ERRO'] = codigo
    MongoConnect.insert_many(data)

def apenas_financeiro_emite_pagamentos(data):

    erros = data[data.TIPOTRANSACAO.isin(['PAGAMENTO']) & ~data.REMETENTE.isin(['FINANCEIRO'])]
    LOGGER.info('Pagamentos não feitos pelo Financeiro (ERRO1): ')
    LOGGER.info(len(erros.index))

    persistir_erros(erros.copy(),'ERRO1')

    return erros

def retiradas_indevidas_alto_valor(data):

    retiradas = data.TIPOTRANSACAO.isin(['RETIRADA'])
    comercial = data.REMETENTE.isin(['COMERCIAL'])
    valor_indevido = data['VALOR'] > 10000

    erros = data[retiradas & ~comercial & valor_indevido]
    LOGGER.info('Retiradas que não foram feitas pelo comercial e que o valor foi superior a R$ 10.000 (ERRO6):')
    LOGGER.info(len(erros.index))

    persistir_erros(erros.copy(), 'ERRO6')

    return erros

def retiradas_indevidas(data):

    retiradas = data.TIPOTRANSACAO.isin(['RETIRADA'])
    comercial = data.REMETENTE.isin(['COMERCIAL'])

    erros = data[retiradas & ~comercial]
    LOGGER.info('Retiradas que não foram feitas pelo comercial (ERRO2):')
    LOGGER.info(len(erros.index))

    persistir_erros(erros.copy(), 'ERRO2')

    return erros

def retiradas_valor_indevido(data):

    retiradas = data.TIPOTRANSACAO.isin(['RETIRADA'])
    valor_indevido = data['VALOR'] > 10000

    erros = data[retiradas & valor_indevido]
    LOGGER.info('Retiradas com valores superiores a R$ 10.000 (ERRO3):')
    LOGGER.info(len(erros.index))

    persistir_erros(erros.copy(),'ERRO3')

    return erros

def depositos_indevidos(data):

    depositos = data.TIPOTRANSACAO.isin(['DEPOSITO'])

    erros = data[depositos]

    LOGGER.info('Depósitos indevidos (ERRO4):')
    LOGGER.info(len(erros.index))

    persistir_erros(erros.copy(),'ERRO4')

    return erros

def pagamentos_nao_associados_faturas(data):

    # Todos os pagamentos realizados devem estar associados a uma fatura emitida pelos departamentos de 
    # TI, Operações e Administrativo;
    faturas = data[data.TIPOTRANSACAO.isin(['FATURA']) & data.REMETENTE.isin(['TI','OPERAÇÕES','ADMINISTRATIVO'])]
    
    LOGGER.info('Faturas pertencentes aos remetentes TI, OPERAÇÕES E ADMINISTRATIVO:')
    LOGGER.info(len(faturas.index))

    pagamentos = data[data.TIPOTRANSACAO.isin(['PAGAMENTO'])]

    # Os pagamentos oriundos de uma fatura devem possuir os mesmos dados nos campos valor e destinatário. 
    merge = pd.merge(pagamentos,faturas, on=['DESTINATARIO','VALOR'])

    erros = pagamentos[~pagamentos['ID'].isin(merge['ID_x'])]

    LOGGER.info('Qtd pagamentos não associados a faturas com mesmo destinatário e valor (ERRO5):')
    LOGGER.info(len(erros.index))

    persistir_erros(erros.copy(),'ERRO5')
    
    erros_dias = pagamentos_associados_diff_dias(merge)
    erros_complemento = pagamentos[pagamentos['ID'].isin(erros_dias['ID_x'])]

    persistir_erros(erros_complemento.copy(),'ERRO5')

    return pd.concat([erros,erros_complemento])

def pagamentos_associados_diff_dias(faturas):

    # Adicionalmente, a data do pagamento será equivalente ao dia seguinte da fatura original.
    erros = faturas[faturas['TIMESTAMP_x'].dt.normalize() - faturas['TIMESTAMP_y'].dt.normalize() != np.timedelta64(1, 'D')]
    LOGGER.info('Associações que não possuem 1 dia de diferença entre a fatura e o pagamento (ERRO5):')
    LOGGER.info(len(erros.index))

    return erros

def valida(data):

    LOGGER.info('Dataframe size: ')
    LOGGER.info(len(data.index))

    # Coluna com erros
    data['ERRO'] = ''

    # Erro - 1
    erros_financeiro = apenas_financeiro_emite_pagamentos(data)
    data_valida = data[~data['ID'].isin(erros_financeiro['ID'])]

    # Erro - 6
    erros_alto_valor = retiradas_indevidas_alto_valor(data_valida)
    data_valida = data_valida[~data_valida['ID'].isin(erros_alto_valor['ID'])]

    # Erro - 2
    erros_retiradas = retiradas_indevidas(data_valida)
    data_valida = data_valida[~data_valida['ID'].isin(erros_retiradas['ID'])]

    # Erros - 3
    erros_comercial = retiradas_valor_indevido(data_valida)
    data_valida = data_valida[~data_valida['ID'].isin(erros_comercial['ID'])]

    # Erro - 4
    erros_depositos = depositos_indevidos(data_valida)
    data_valida = data_valida[~data_valida['ID'].isin(erros_depositos['ID'])]

    # Erro - 5
    erros_associacoes = pagamentos_nao_associados_faturas(data_valida)
    data_valida = data_valida[~data_valida['ID'].isin(erros_associacoes['ID'])]

    # Insere os válidos
    MongoConnect.insert_many(data_valida)