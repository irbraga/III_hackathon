# Desafio Hackathon 2018

## Tecnologias Utilizadas

1. Python 3.6
    1. Wheel
    1. Flask
    1. PyMongo
    1. Numpy
    1. Pandas

## Instruções de Desenvolvimento

### MongoDB

Instruções completas no link do MongoDB  
https://docs.mongodb.com/manual/tutorial/install-mongodb-on-ubuntu/

#### Linux: 
```
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 9DA31620334BD75D9DCB49F368818C72E52529D4
```
```
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu xenial/mongodb-org/4.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-4.0.list
```
```
sudo apt-get update
```
```
sudo apt-get install -y mongodb-org
```
```
sudo service mongod start
```

### Virtual Env
```
python3 -m venv venv
. venv/bin/activate
```

```
pip install -r requirements.txt
```

### Flask
```
export FLASK_APP=app
flask run
```

> A aplicação estará rodando na url http://localhost:5000

### Unit Test

```
pip install pytest nose
```

## Procedimentos para Deploy e Implantação

> Listar os procedimentos necessários para deploy e implantação do produto em ambiente produtivo 

### Empacotamento
```
python setup.py bdist_wheel
```

### Deploy em ambiente de produção

#### Instalando a aplicação

```
pip install dist/app-1.0.0-py3-none-any.whl
```

#### Waitress
```
pip install waitress
waitress-serve --call 'app:create_app'
```

> A aplicação estará rodando na url http://localhost:8080

### Comandos da API
#### Listar todas as operações válidas
```
/operacoes
```

#### Listar todas as transações de um determinado tipo de transação
 <tipo_transacao> Informar tipo da transação  
```
/operacoes/por_tipo/<tipo_transacao>
```

#### Listar todas as transações dentro de um intervalo de valores
<valor_inicial> Informar primeiro valor do intervalo  
<valor_final> Informar segundo valor do intervalo. Este atributo é opcional, caso ele não seja informado, o serviço retornará uma lista com todas as transações com valores inferiores ao valor_inicial  
```
/operacoes/por_valor/<valor_inicial>/<valor_final>?
```

#### Listar todas as transações de um determinado departamento remetente
<remetente> Informar departamento remetente  
```
/operacoes/por_remetente/<remetente>
```

#### Listar todas as transações onde o nome destinatário contenha um determinado texto
<destinatario> Informar texto completo ou parcial correspondente ao destinatário da transação  
```
/operacoes/por_destinatario/<destinatario>
```

#### Listar todos os registros inválidos
```
/erros
```

#### Listar todos os registros inválidos por tipo de erro

<tipo_erro> corresponde a um dos erros seguintes:  
- ERRO1: "Pagamento" com remetente diferente de "Financeiro"   
- ERRO2: "Retirada" com remetente diferente de "Comercial"  
- ERRO3: "Retirada" com valor maior que 10.000,00  
- ERRO4: Transação do tipo "Depósito"  
- ERRO5: "Pagamento" sem "Fatura" correspondente. Considera-se fatura correspondente aquela que atende os seguintes requisitos:  
				- Destinatários iguais  
				- Valores iguais  
				- data fatura é igual a data anterior do pagamento  
				- Remetente da Fatura é um dos seguintes departamentos: "TI", "Operações" ou "Administrativo"  

```
/erros/por_tipo_erro/<tipo_erro>
```
