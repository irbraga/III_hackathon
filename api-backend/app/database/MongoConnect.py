#!/usr/bin/python
# -*- coding: utf-8 -*-
from pymongo import MongoClient
from bson.json_util import loads
import logging

logger = logging.getLogger('api-backend')

# Connecta com o servidor do banco local
client = MongoClient('mongodb://localhost:27017/')
# Testa o client
db = client.test_database
# Se conecta com o banco
db = client['db-api-backend']
# Instancia a coleção
transacoes = db['transacoes']
# Zera todos os registros ao iniciar a aplicação
transacoes.drop()
 
def populate(data):
    logger.info('Removendo os dados da coleção e inserindo os novos dados das transações.')
    transacoes.drop()
    insert_many(data)

def insert_many(data):
    if not data.empty:
        transacoes.insert_many(loads(data.to_json(orient='records')))

def insert(registro):
    """
        Insere uma transacao.
    """
    transacoes.insert_one(registro)

def find(query):
    """
        Obtém transações usando uma query.
    """
    return transacoes.find(query)