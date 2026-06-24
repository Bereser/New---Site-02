# ResumosAI - Plataforma de Resumos de Vídeos com IA

Um site completo para resumir vídeos do YouTube usando inteligência artificial. Planos gratuito (3 resumos/dia) e premium (ilimitado).

## 🚀 Características

- ✅ **Resumos com IA** - Use Google Generative AI para criar resumos precisos
- ✅ **Autenticação** - Sistema completo de registro e login
- ✅ **Planos** - Free (3 resumos/dia) e Premium (ilimitado)
- ✅ **Pagamentos** - Integração com Stripe
- ✅ **Design Responsivo** - Funciona em desktop, tablet e mobile
- ✅ **Histórico** - Acesso a todos os seus resumos anteriores
- ✅ **Download** - Baixe seus resumos em formato texto

## 📋 Pré-requisitos

- Python 3.8+
- pip (gerenciador de pacotes Python)
- Uma chave da API Google Generative AI
- (Opcional) Chaves do Stripe para pagamentos

## 🔧 Instalação

### 1. Clone ou baixe o projeto

```bash
cd c:\Users\arthu\OneDrive\Desktop\Projeto
```

### 2. Crie um ambiente virtual

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente

Edite o arquivo `.env` com suas chaves:

```env
GOOGLE_API_KEY=sua-chave-google-aqui
STRIPE_PUBLIC_KEY=sua-chave-publica
STRIPE_SECRET_KEY=sua-chave-secreta
SECRET_KEY=sua-chave-secreta-flask
```

### 5. Inicie o aplicativo

```bash
python app.py
```

O aplicativo estará disponível em: **http://localhost:5000**

## 🔑 Como Obter as Chaves

### Google Generative AI

1. Acesse [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Clique em "Create API Key"
3. Copie a chave e cole em `.env`

### Stripe (Opcional para pagamentos)

1. Crie uma conta em [Stripe](https://stripe.com)
2. Acesse o dashboard
3. Copie suas chaves (Public Key e Secret Key)
4. Cole em `.env`

## 📁 Estrutura do Projeto

```
Projeto/
├── app.py                 # Aplicação Flask principal
├── config.py             # Configurações
├── models.py             # Modelos do banco de dados
├── routes.py             # Rotas da aplicação
├── utils.py              # Funções utilitárias
├── requirements.txt      # Dependências Python
├── .env                  # Variáveis de ambiente
├── static/
│   ├── css/
│   │   └── style.css     # Estilos CSS
│   └── js/
│       ├── main.js       # JavaScript global
│       └── dashboard.js  # JavaScript do dashboard
└── templates/
    ├── base.html         # Template base
    ├── index.html        # Página inicial
    ├── login.html        # Página de login
    ├── register.html     # Página de registro
    ├── dashboard.html    # Dashboard
    ├── pricing.html      # Página de preços
    ├── payment_*.html    # Páginas de pagamento
    ├── 404.html          # Página de erro 404
    └── 500.html          # Página de erro 500
```

## 🎯 Como Usar

### 1. Criar Conta

- Clique em "Cadastro"
- Preencha os dados
- Pronto! Você terá 3 resumos gratuitos por dia

### 2. Resumir Vídeo

- Faça login
- Cole a URL de um vídeo do YouTube
- Clique em "Gerar Resumo"
- Aguarde alguns segundos
- Receba seu resumo em português

### 3. Fazer Upgrade

- Clique em "Upgrade Premium"
- Complete o pagamento via Stripe
- Pronto! Acesso ilimitado a resumos

## 💰 Preços

### Plano Gratuito
- 3 resumos por dia
- Vídeos até 3 horas
- Grátis para sempre

### Plano Premium
- Resumos ilimitados
- Vídeos até 6 horas
- Download de resumos
- Suporte prioritário
- **R$ 19,99/mês** (ou US$ 2,00)

## 🛠️ Tecnologias Utilizadas

- **Backend**: Python, Flask, SQLAlchemy
- **Frontend**: HTML, CSS, JavaScript vanilla
- **Banco de Dados**: SQLite
- **IA**: Google Generative AI
- **Pagamentos**: Stripe
- **Extração de Transcrição**: YouTube Transcript API

## 📝 Anotações Importantes

1. **YouTube Transcripts**: O vídeo deve ter legendas disponíveis (automáticas ou adicionadas pelo criador)
2. **API Quotas**: A API Google Generative AI tem limites de requisições
3. **Stripe Testing**: Use cartões de teste do Stripe no ambiente de desenvolvimento
4. **CORS**: Se usar em produção, configure CORS adequadamente

## 🚀 Deploy em Produção

### Heroku

```bash
# 1. Instale o Heroku CLI
# 2. Login
heroku login

# 3. Crie um app
heroku create seu-app-name

# 4. Defina variáveis
heroku config:set GOOGLE_API_KEY=sua-chave
heroku config:set STRIPE_SECRET_KEY=sua-chave

# 5. Deploy
git push heroku main
```

### Railway/Render/DigitalOcean

Similar ao Heroku - defina as variáveis de ambiente e faça deploy do repositório Git.

## 🐛 Troubleshooting

### Erro: "ModuleNotFoundError"
- Certifique-se de ativar o virtual environment
- Reinstale as dependências: `pip install -r requirements.txt`

### Erro: "API Key inválida"
- Verifique a chave da API Google no arquivo `.env`
- Certifique-se de que a API está habilitada

### Erro: "Sem transcrição disponível"
- O vídeo pode não ter legendas
- Tente outro vídeo com legendas automáticas ativadas

## 📞 Suporte

Para dúvidas ou problemas:
- Verifique o arquivo de erro do servidor
- Consulte a documentação das APIs utilizadas
- Crie uma issue no repositório

## 📄 Licença

Este projeto é fornecido como está para fins educacionais e comerciais.

## 🙌 Créditos

Desenvolvido com ❤️ usando Flask, Google AI e Stripe.

---

**Versão**: 1.0.0  
**Última atualização**: Junho 2024
