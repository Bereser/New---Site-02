# 🔌 Documentação da API - ResumosAI

## Endpoints Disponíveis

### 🔐 Autenticação

#### POST `/auth/register`
Criar novo usuário

**Parâmetros:**
- `username` (string, obrigatório) - Entre 3 e 80 caracteres
- `email` (string, obrigatório) - Email válido
- `password` (string, obrigatório) - Mínimo 6 caracteres
- `confirm_password` (string, obrigatório) - Deve coincidir com password
- `full_name` (string, opcional) - Nome completo

**Exemplo:**
```bash
curl -X POST http://localhost:5000/auth/register \
  -d "username=joao&email=joao@example.com&password=senha123&confirm_password=senha123&full_name=João Silva"
```

#### POST `/auth/login`
Fazer login

**Parâmetros:**
- `username` (string, obrigatório)
- `password` (string, obrigatório)
- `remember` (checkbox, opcional)

#### GET `/auth/logout`
Fazer logout (requer autenticação)

---

### 📺 Resumos

#### POST `/api/summarize`
Criar resumo de um vídeo

**Headers:**
- `Content-Type: application/json`

**Parâmetros (JSON):**
- `url` (string, obrigatório) - URL do YouTube

**Exemplo:**
```bash
curl -X POST http://localhost:5000/api/summarize \
  -H "Content-Type: application/json" \
  -d '{"url":"https://www.youtube.com/watch?v=jNQXAC9IVRw"}'
```

**Response (200 OK):**
```json
{
  "success": true,
  "summary_id": 1,
  "title": "Big Buck Bunny Official Trailer",
  "summary": "Este é um resumo em português do vídeo...",
  "duration": 600
}
```

**Response (400 Bad Request):**
```json
{
  "error": "URL do vídeo é obrigatória"
}
```

#### GET `/api/summaries`
Listar todos os resumos do usuário (requer autenticação)

**Exemplo:**
```bash
curl http://localhost:5000/api/summaries
```

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "title": "Big Buck Bunny",
    "url": "https://www.youtube.com/watch?v=jNQXAC9IVRw",
    "summary": "Resumo do vídeo...",
    "status": "completed",
    "created_at": "21/06/2024 14:30",
    "duration": 600
  }
]
```

#### GET `/api/summary/<id>`
Obter detalhes completos de um resumo (requer autenticação)

**Exemplo:**
```bash
curl http://localhost:5000/api/summary/1
```

**Response (200 OK):**
```json
{
  "id": 1,
  "title": "Big Buck Bunny",
  "url": "https://www.youtube.com/watch?v=jNQXAC9IVRw",
  "summary": "Resumo completo...",
  "transcript": "Transcrição original do vídeo...",
  "status": "completed",
  "created_at": "21/06/2024 14:30",
  "duration": 600
}
```

#### DELETE `/api/delete/<id>`
Deletar um resumo (requer autenticação)

**Exemplo:**
```bash
curl -X DELETE http://localhost:5000/api/delete/1
```

**Response (200 OK):**
```json
{
  "success": true
}
```

---

### 💳 Pagamentos

#### GET `/payment/upgrade`
Iniciar processo de upgrade para Premium

Redireciona para Stripe Checkout

#### GET `/payment/success`
Confirmação de pagamento bem-sucedido

Atualiza plano do usuário para Premium

#### GET `/payment/cancel`
Cancelamento de pagamento

---

### 📄 Páginas Públicas

#### GET `/`
Página inicial

#### GET `/pricing`
Página de preços

#### GET `/auth/login`
Página de login

#### GET `/auth/register`
Página de cadastro

---

### 🔒 Páginas Autenticadas

#### GET `/dashboard`
Dashboard principal (requer login)

---

## 🔄 Status Codes

| Código | Significado |
|--------|-------------|
| 200 | OK - Requisição bem-sucedida |
| 201 | Created - Recurso criado |
| 204 | No Content - Sem conteúdo |
| 400 | Bad Request - Dados inválidos |
| 401 | Unauthorized - Não autenticado |
| 403 | Forbidden - Sem permissão |
| 404 | Not Found - Não encontrado |
| 429 | Too Many Requests - Limite atingido |
| 500 | Internal Server Error - Erro no servidor |

---

## 📊 Status de Resumo

Cada resumo tem um status:

| Status | Significado |
|--------|------------|
| `processing` | Processando o vídeo |
| `completed` | Resumo pronto |
| `failed` | Erro ao processar |

---

## 🔐 Autenticação

A aplicação usa sessões Flask:

1. Faça login via `/auth/login`
2. Uma cookie de sessão é criada
3. Use essa sessão para acessar endpoints autenticados
4. Logout em `/auth/logout`

---

## ⚠️ Rate Limiting

**Plano Free:**
- 3 resumos por dia
- Status: HTTP 429 se limite atingido

**Plano Premium:**
- Ilimitado

---

## 🧪 Testando a API

### Com cURL

```bash
# Teste de URL inválida
curl -X POST http://localhost:5000/api/summarize \
  -H "Content-Type: application/json" \
  -d '{"url":"https://exemplo.com"}'

# Resposta esperada:
# {"error": "URL do YouTube inválida"}
```

### Com Python

```python
import requests

# Login
session = requests.Session()
session.post('http://localhost:5000/auth/login', data={
    'username': 'teste',
    'password': 'senha123'
})

# Resumir vídeo
response = session.post('http://localhost:5000/api/summarize', json={
    'url': 'https://www.youtube.com/watch?v=jNQXAC9IVRw'
})

print(response.json())
```

### Com JavaScript

```javascript
// Login (via formulário HTML)
// Depois fazer requisição

const response = await fetch('/api/summarize', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        url: 'https://www.youtube.com/watch?v=jNQXAC9IVRw'
    })
});

const data = await response.json();
console.log(data);
```

---

## 🛠️ Variáveis de Configuração

Em `config.py`:

```python
FREE_PLAN_LIMIT = 3  # Resumos por dia (Free)
MAX_VIDEO_LENGTH = 180  # Duração máxima em minutos
MAX_SUMMARY_LENGTH = 2000  # Tamanho máximo do resumo
PAID_PLAN_PRICE = 1999  # Preço em centavos
```

---

## 📝 Mensagens de Erro Comuns

```json
{
    "error": "URL do vídeo é obrigatória"
}

{
    "error": "URL do YouTube inválida"
}

{
    "error": "Limite de 3 resumos por dia atingido"
}

{
    "error": "Não foi possível obter informações do vídeo"
}

{
    "error": "Não foi possível extrair a transcrição do vídeo"
}

{
    "error": "Erro ao gerar resumo com IA"
}
```

---

## 🔮 Extensões Futuras

Você pode adicionar endpoints para:

- `POST /api/share` - Compartilhar resumo
- `GET /api/stats` - Estatísticas do usuário
- `POST /api/export` - Exportar em diferentes formatos
- `GET /api/search` - Buscar em resumos anteriores
- `PATCH /api/settings` - Atualizar configurações do usuário

---

## 📚 Mais Informações

Para mais detalhes sobre as dependências e como funcionam:

- Flask: https://flask.palletsprojects.com/
- SQLAlchemy: https://www.sqlalchemy.org/
- Google AI: https://ai.google.dev/
- Stripe: https://stripe.com/docs

---

**Versão da API**: 1.0  
**Última atualização**: Junho 2024

