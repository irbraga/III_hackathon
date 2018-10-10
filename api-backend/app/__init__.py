#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Classe principal da aplicação
"""

import logging

from bson.objectid import ObjectId
from bson.json_util import dumps
from flask import Response, jsonify, request, Flask

from flask_cors import CORS
from .business import ValidadorTransacoes
from .database import MongoConnect
from .util import DownloadInput

logging.basicConfig(filename='api-backend.log', level=logging.INFO, format='%(asctime)s [%(levelname)s] [%(name)s] %(message)s', datefmt='%Y/%m/%d %I:%M:%S %p')
LOGGER = logging.getLogger('api-backend')

def create_app():
    """Método padrão do Flask para criação do app
    """
    LOGGER.info('Inicializando a aplicação.')

    app = Flask(__name__)
    CORS(app, resources={r"/*": {"origins": "*"}})

    LOGGER.info('Iniciando o download do arquivo de transacoes...')
    DownloadInput.init()
    LOGGER.info('Arquivo lido e armazenado no banco.')

    # Informações da API
    @app.route("/", methods=['GET'])
    def _info():
        """
        Informações da API
        Returns:
            json
        """
        return dumps({
            'Developer': 'Departamento de TI da XPTO Inc.',
            'version': '0.0.1'
        })

    @app.route("/db", methods=['POST'])
    def _mongo_post():
        """
        Insere registros no banco
        Returns:
            json
        """
        if request.is_json:
            MongoConnect.insert(request.get_json())
            return Response(status='201')
        return Response(status='400')

    @app.route("/db/<uuid>", methods=['GET'])
    def _mongo_get(uuid):
        """Obtem registro por UUID

        Returns:
            json
        """
        if ObjectId.is_valid(uuid):
            query = {
                '_id' : ObjectId(uuid)
            }
            return dumps(MongoConnect.find(query))

        return Response(status='400')

    @app.route("/db/query", methods=['POST'])
    def _mongo_query_json():
        """Obtem registro por uma query

        Returns:
            json
        """
        if request.is_json:
            query = request.get_json()
            return dumps(MongoConnect.find(query))

        return Response(status='400')

    @app.route("/erros", methods=['GET'])
    def _obter_todos_erros():
        """Obtem registro de todos os erros

        Returns:
            json
        """
        query = {"ERRO": {"$ne": ''}}
        return dumps(MongoConnect.find(query))

    @app.route("/erros/por_tipo_erro/<tipo_erro>", methods=['GET'])
    def _obter_erro_por_tipo_erro(tipo_erro):
        """Obtem registro de erros por tipo

        Returns:
            json
        """
        if tipo_erro == 'ERRO2':
            query = {"$or":[{"ERRO":'ERRO2'}, {"ERRO":'ERRO6'}]}
        elif tipo_erro == 'ERRO3':
            query = {"$or":[{"ERRO":'ERRO3'}, {"ERRO":'ERRO6'}]}
        else:
            query = {"ERRO": tipo_erro}
        return dumps(MongoConnect.find(query))

    @app.route("/operacoes", methods=['GET'])
    def _obter_todas_validas():
        """Obtem todas as operações válidas

        Returns:
            json
        """
        query = {
            'ERRO': ''
        }
        return dumps(MongoConnect.find(query))

    @app.route("/operacoes/por_tipo/<tipo>", methods=['GET'])
    def _obter_por_tipo(tipo):
        """Obtem operações válidas por tipo

        Returns:
            json
        """
        query = {
            'TIPOTRANSACAO' : tipo,
            'ERRO': ''
        }
        return dumps(MongoConnect.find(query))

    @app.route("/operacoes/por_remetente/<remetente>", methods=['GET'])
    def _obter_por_remetente(remetente):
        """Obtem operações válidas por remetente

        Returns:
            json
        """
        query = {
            'REMETENTE' : remetente,
            'ERRO': ''
        }
        return dumps(MongoConnect.find(query))

    @app.route("/operacoes/por_destinatario/<destinatario>", methods=['GET'])
    def _obter_por_destinatario(destinatario):
        """Obtem operações válidas por destinatário

        Returns:
            json
        """
        query = {
            'DESTINATARIO' : {'$regex': destinatario},
            'ERRO': ''
        }
        return dumps(MongoConnect.find(query))

    @app.route("/operacoes/por_valor/<float:valor_minimo>/<float:valor_maximo>", methods=['GET'])
    @app.route("/operacoes/por_valor/<int:valor_minimo>/<int:valor_maximo>", methods=['GET'])
    @app.route("/operacoes/por_valor/<float:valor_maximo>", methods=['GET'])
    @app.route("/operacoes/por_valor/<int:valor_maximo>", methods=['GET'])
    def _obter_por_valor(valor_maximo, valor_minimo=0):
        """Obtem operações válidas por valor

        Returns:
            json
        """
        query = {
            'VALOR' : {'$gt': valor_minimo, '$lt': valor_maximo},
            'ERROS': ''
        }
        return dumps(MongoConnect.find(query))

    return app
