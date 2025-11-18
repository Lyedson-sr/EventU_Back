# EventU_Back

## Passo a passo para rodar o sistema:

### Com Docker:
#### 1. Clone o repositório
```bash
git clone git@github.com:Lyedson-sr/EventU_Back.git
```

#### 2. Configure as variáveis de ambiente
```bash
cp .env.example .env.docker
```

Em seguida, edite o arquivo .env.docker:
```env
SECRET_KEY=sua_secret_key_super_segura_aqui
ALLOWED_HOSTS=hosts_permitidos


POSTGRES_DB=seu_banco
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_USER=seu_user
POSTGRES_PASSWORD=sua_senha
```

#### 3. Rode o docker compose
```bash
docker compose -f docker-compose.dev.yaml up --build
```

### Localmente:

#### 1. Clone o repositório
```bash
git clone git@github.com:Lyedson-sr/EventU_Back.git
```

#### 2. Instalar o gerenciador de pacotes uv
##### No Linux/Mac
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

##### No Windows
```bash
irm https://astral.sh/uv/install.ps1 | iex
```

##### Verifique a instalação
```bash
uv --version
```

#### 3. Instalar as dependências e ativar ambiente virtual
```bash
uv sync
```

##### No Windows:
```bash
.venv\Scripts\activate
```

##### No Linux/Mac:
```bash
source .venv/bin/activate
```

#### 4. Configure as variáveis de ambiente
```bash
cp .env.example .env
```

Em seguida, edite o arquivo .env:
```env
SECRET_KEY=sua_secret_key_super_segura_aqui
ALLOWED_HOSTS=hosts_permitidos


POSTGRES_DB=seu_banco
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=seu_user
POSTGRES_PASSWORD=sua_senha
```

#### 5. Suba apenas o banco com docker compose
```bash
docker compose -f docker-compose.dev.yaml postgres up
```

#### 6. Faça as migrações
```bash
python3 manage.py makemigrations
```

E então:
```bash
python3 manage.py migrate
```

#### 7. Rode o servidor
```bash
python3 manage.py runserver
```