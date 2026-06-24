# GUIA DE INSTALAÇÃO COMPLETO - ResumosAI

## 🚀 COMEÇAR RÁPIDO

### Windows
```bash
# 1. Abra o PowerShell em c:\Users\arthu\OneDrive\Desktop\Projeto
# 2. Execute:
.\setup.bat
# 3. Pronto! Siga as instruções na tela
```

### Linux / Mac
```bash
# 1. Abra o terminal em ~/Desktop/Projeto
# 2. Execute:
chmod +x setup.sh
./setup.sh
# 3. Pronto! Siga as instruções na tela
```

## 📋 INSTALAÇÃO MANUAL (Se o script não funcionar)

### Passo 1: Instalar Python
- Baixe de: https://www.python.org/downloads/
- Certifique-se de marcar "Add Python to PATH"
- Versão mínima: **3.8**

### Passo 2: Verificar Python
```bash
python --version
pip --version
```

### Passo 3: Criar Ambiente Virtual

**Windows:**
```bash
cd c:\Users\arthu\OneDrive\Desktop\Projeto
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
cd ~/Desktop/Projeto
python3 -m venv venv
source venv/bin/activate
```

### Passo 4: Instalar Dependências
```bash
pip install -r requirements.txt
```

Isso instalará:
- Flask (framework web)
- SQLAlchemy (ORM do banco de dados)
- Google Generative AI (para resumos com IA)
- youtube-transcript-api (extração de transcrições)
- stripe (processamento de pagamentos)
- E outras dependências

### Passo 5: Configurar Variáveis de Ambiente

1. **Abra o arquivo `.env`** em um editor de texto
2. **Substitua os valores** pelas suas chaves reais:

```env
# Seu SECRET_KEY (pode deixar como está para desenvolvimento)
SECRET_KEY=sua-chave-secreta-super-segura-aqui-2024

# OBRIGATÓRIO: Google API Key
GOOGLE_API_KEY=AIzaSyDxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# OPCIONAL: Stripe (apenas se quiser pagamentos)
STRIPE_PUBLIC_KEY=pk_test_51HJ4lLxxxxxxxxxxxxxxxxxxxxxxx
STRIPE_SECRET_KEY=sk_test_51HJ4lLxxxxxxxxxxxxxxxxxxxxxxx
```

### Passo 6: Inicializar Banco de Dados

```bash
# Criar tabelas
python init_db.py

# Criar usuário de teste (opcional)
python create_test_user.py
```

### Passo 7: Iniciar o Servidor

```bash
python app.py
```

Você deve ver algo como:
```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
 * WARNING: Do not use the development server in production!
```

### Passo 8: Acessar o Site

Abra seu navegador e vá para: **http://localhost:5000**

---

## 🔑 COMO OBTER AS CHAVES

### Google Generative AI (OBRIGATÓRIO)

1. Acesse: https://makersuite.google.com/app/apikey
2. Clique em **"Create API Key"**
3. Selecione **"Create API key in new project"**
4. Copie a chave gerada
5. Cole em `.env` na linha `GOOGLE_API_KEY=`

### Stripe (OPCIONAL - Apenas para pagamentos)

1. Acesse: https://stripe.com
2. Crie uma conta (teste ou produção)
3. Vá para **Dashboard → API Keys**
4. Copie **Publishable Key** e **Secret Key**
5. Cole em `.env`:
   - `STRIPE_PUBLIC_KEY=` (Publishable Key)
   - `STRIPE_SECRET_KEY=` (Secret Key)

---

## 📝 DADOS DE TESTE

Ao executar `python create_test_user.py`, será criado um usuário:

- **Username:** teste
- **Email:** teste@resumosai.com
- **Senha:** senha123
- **Plano:** Free (3 resumos/dia)

Use essas credenciais para testar a plataforma.

---

## 🎯 TESTANDO A APLICAÇÃO

### 1. Teste sem autenticação
- Acesse http://localhost:5000
- Veja a página inicial
- Clique em "Preços" para ver os planos

### 2. Teste de registro
- Clique em "Cadastro"
- Preencha os dados
- Será criado um novo usuário com plano Free

### 3. Teste de resumo de vídeo
- Faça login
- Copie a URL de qualquer vídeo do YouTube com legendas
- Cole em "Resumir Novo Vídeo"
- Clique em "Gerar Resumo"
- Aguarde alguns segundos

**URLs de teste recomendadas:**
```
https://www.youtube.com/watch?v=dQw4w9WgXcQ (musicale, mas funciona)
https://www.youtube.com/watch?v=jNQXAC9IVRw (Big Buck Bunny)
Busque por "tutorial python" ou "how to" no YouTube
```

### 4. Teste do plano Premium
- No dashboard, clique em "Upgrade Premium"
- Use cartão de teste do Stripe: **4242 4242 4242 4242**
- Data: qualquer data futura
- CVC: qualquer 3 dígitos
- Seu plano mudará para Premium

---

## 🐛 PROBLEMAS COMUNS

### Erro: "ModuleNotFoundError: No module named 'flask'"
**Solução:**
```bash
# Certifique-se de que o venv está ativado
# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate

# Depois reinstale:
pip install -r requirements.txt
```

### Erro: "Port 5000 already in use"
**Solução:**
```bash
# Mude a porta em app.py, na última linha:
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)  # Mude 5000 para 5001
```

### Erro: "API Key inválida"
**Solução:**
- Verifique se a chave da Google está correta em `.env`
- Certifique-se de que a API está ativada em https://console.cloud.google.com
- Teste a chave diretamente em https://makersuite.google.com/app/

### Erro: "No transcript available for this video"
**Solução:**
- Nem todo vídeo do YouTube tem legendas/transcrição
- O vídeo precisa ter legendas automáticas ou adicionadas
- Tente outro vídeo

### Erro: "Database is locked"
**Solução:**
- Delete o arquivo `videos_ai.db`
- Reexecute `python init_db.py`
- Reinicie o servidor

---

## 🚀 PRÓXIMOS PASSOS

### 1. Personalize o Site
- Edite cores e logos em `static/css/style.css`
- Mude textos em `templates/`
- Adicione sua logo

### 2. Configure Email (Opcional)
- Para enviar confirmações de pagamento
- Configure SMTP em `.env` (veja variáveis comentadas)

### 3. Deploy em Produção
- Veja o README.md para instruções de Heroku/Railway/DigitalOcean

### 4. Adicione Mais Recursos
- Limite de duração de vídeo
- Múltiplos idiomas
- Compartilhamento de resumos
- API pública

---

## 📞 SUPORTE

Se encontrar problemas:

1. **Verifique os logs** do terminal onde você executou `python app.py`
2. **Google o erro** - muitas pessoas encontraram o mesmo problema
3. **Consulte a documentação:**
   - Flask: https://flask.palletsprojects.com/
   - SQLAlchemy: https://www.sqlalchemy.org/
   - Google AI: https://ai.google.dev/

---

## ✅ CHECKLIST DE INSTALAÇÃO

- [ ] Python 3.8+ instalado
- [ ] Ambiente virtual criado e ativado
- [ ] Dependências instaladas (`pip install -r requirements.txt`)
- [ ] `.env` configurado com Google API Key
- [ ] Banco de dados inicializado (`python init_db.py`)
- [ ] Servidor rodando (`python app.py`)
- [ ] Acesso a http://localhost:5000 funcionando
- [ ] Login funcionando
- [ ] Resumo de vídeo funcionando

---

**Pronto! Você agora tem um site completo de resumos de vídeos com IA em execução local!**

Para mais informações, consulte o [README.md](README.md)
