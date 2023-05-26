## Getting Started

Os pré requisitos abaixo são necessários apenas para a criação do .exe, após isso o .exe é independente.
Uma versão do executável com as dependências necessárias estará disponível no diretório *example*.

### Prerequisites

* [Python](https://www.python.org/)
* [virtualenv](https://virtualenv.pypa.io/en/latest/installation.html)
```pip install virtualenv```

### Installing

Passo a passo para a geração de um novo executável, caso venham a ser feita modificações no código.

Criar ambiente virtual:
```python -m venv venv```

Ativar ambiente virtual:
```.\venv\Scripts\activate```

(Desativar quando necessário)
```deactivate```

Instalar dependências
Se o projeto já tem o arquivo de requirements:
```pip install -r .\requirements.txt```

Do contrário, usar:
```pip install ...```
para cada pacote utilizado no projeto

A criação do arquivo requirements.txt pode ser feita com o comando:
```pip freeze > requirements.txt```

### Executável
Criar executável
```python setup.py build```

Após isso será criado um repositório *build*, onde ficará o executável e as suas dependências.
Os arquivos necessários para o funcionamento do programa são todos os que estão dentro da pasta *build* e também:
* config.ini
