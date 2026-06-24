# 📚 ÍNDICE DE DOCUMENTAÇÃO - ResumosAI

## 🚀 Comece por aqui!

### 1. **COMECE_AQUI.md** ⭐
   - **O quê:** Guia de 5 minutos para começar
   - **Quando usar:** Na primeira vez
   - **Tempo:** 5 minutos

### 2. **GUIA_INSTALACAO.md** 
   - **O quê:** Instruções completas de instalação
   - **Quando usar:** Quando tiver problemas de instalação
   - **Tempo:** 15-30 minutos

---

## 📖 Documentação Principal

### 3. **README.md**
   - **O quê:** Visão geral do projeto, características, tecnologias
   - **Quando usar:** Para entender o que é o ResumosAI
   - **Comprimento:** Médio

### 4. **PROJETO_COMPLETO.md**
   - **O quê:** Análise completa do projeto, estrutura, funcionamento
   - **Quando usar:** Para entender como tudo funciona
   - **Comprimento:** Grande (recomendado ler)

### 5. **API_DOCUMENTACAO.md**
   - **O quê:** Documentação de todos os endpoints da API
   - **Quando usar:** Para usar ou estender a API
   - **Comprimento:** Médio

---

## 🛠️ Arquivos de Setup

### setup.bat (Windows)
```bash
duplo-clique em setup.bat
```
- Instala automaticamente
- Cria ambiente virtual
- Instala dependências
- Inicializa banco de dados

### setup.sh (Linux/Mac)
```bash
chmod +x setup.sh
./setup.sh
```
- Mesmo que o Windows
- Para sistemas Unix-like

---

## 💻 Arquivos Python Principais

### app.py
```python
# Entrada principal da aplicação Flask
python app.py
```

### config.py
- Configurações de planos
- Chaves de API
- Limites do sistema

### models.py
- Modelos do banco de dados
- User, Video, Summary, DailyUsage

### routes.py
- Todas as rotas (auth, api, payment)
- Lógica de negócios

### utils.py
- Funções de IA
- Extração de transcrições
- Validações

---

## 🎨 Arquivos Frontend

### templates/base.html
- Template base com navbar e footer

### templates/index.html
- Página inicial

### templates/dashboard.html
- Dashboard (summarizer + histórico)

### templates/pricing.html
- Página de preços

### static/css/style.css
- Todos os estilos (2000+ linhas)

### static/js/dashboard.js
- Lógica principal do resumidor

---

## 📋 Scripts Auxiliares

### init_db.py
```bash
python init_db.py
```
- Cria tabelas do banco
- Cria planos de assinatura

### create_test_user.py
```bash
python create_test_user.py
```
- Cria usuário de teste
- Username: teste
- Senha: senha123

---

## 🔑 Configuração

### .env
```env
GOOGLE_API_KEY=sua-chave-aqui
STRIPE_PUBLIC_KEY=sua-chave-publica
STRIPE_SECRET_KEY=sua-chave-secreta
SECRET_KEY=sua-chave-flask
```

Edite este arquivo com suas chaves!

---

## 📦 requirements.txt
```bash
pip install -r requirements.txt
```

Lista todas as dependências Python

---

## 🔍 Fluxo de Leitura Recomendado

### Para Usuários Finais
1. COMECE_AQUI.md
2. GUIA_INSTALACAO.md (se tiver problemas)
3. Use o site!

### Para Desenvolvedores
1. COMECE_AQUI.md
2. PROJETO_COMPLETO.md
3. Explore o código (routes.py, models.py)
4. API_DOCUMENTACAO.md (se quiser estender)

### Para Deploys em Produção
1. README.md (seção Deploy)
2. PROJETO_COMPLETO.md (seção Para Produção)
3. GUIA_INSTALACAO.md (seção Deploy)

---

## 🎯 Perguntas Comuns

**P: Por onde começo?**
R: Leia COMECE_AQUI.md

**P: Como instalo?**
R: Execute setup.bat (Windows) ou setup.sh (Linux/Mac)

**P: Como faço resumos?**
R: Faça login e cole uma URL do YouTube no dashboard

**P: Como faço upload de vídeos meus?**
R: A plataforma suporta apenas YouTube. Você pode fazer upload em seu canal YouTube.

**P: Como configuro pagamentos?**
R: Obtenha chaves do Stripe e configure em .env

**P: Como faço deploy?**
R: Leia seção de Deploy em README.md

**P: Como adiciono novas features?**
R: Estude routes.py e implemente as rotas

**P: Como faço debug?**
R: Verifique o terminal onde app.py está rodando

---

## 📞 Onde Encontrar Ajuda

### Erros na Instalação
→ GUIA_INSTALACAO.md (seção Problemas Comuns)

### Entender o Projeto
→ PROJETO_COMPLETO.md

### Usar a API
→ API_DOCUMENTACAO.md

### Deploy
→ README.md (seção Deploy)

### Código Python
→ Veja comentários em routes.py, models.py

### Código Frontend
→ Veja comentários em static/js/dashboard.js

---

## ✅ Checklist de Leitura

- [ ] Li COMECE_AQUI.md
- [ ] Executei setup.bat/setup.sh
- [ ] Testei fazer um resumo
- [ ] Configurei Google API Key
- [ ] Testei login/cadastro
- [ ] Li PROJETO_COMPLETO.md
- [ ] Explorei o código
- [ ] Entendi a estrutura do banco

---

## 🚀 Próximas Ações

1. **Hoje:** Instale e teste
2. **Amanhã:** Configure suas chaves
3. **Esta semana:** Leia toda documentação
4. **Este mês:** Deploy em produção

---

## 📌 Dicas Importantes

1. **Sempre ative o venv** antes de usar `pip`
2. **Guarde suas chaves** em local seguro
3. **Não commita .env** se usar Git
4. **Backup do banco** regularmente
5. **Logs são seus amigos** - verifique o terminal

---

## 🎉 Pronto!

Você tem tudo o que precisa para:
- ✅ Usar a plataforma
- ✅ Entender o código
- ✅ Estender funcionalidades
- ✅ Deploy em produção

**Divirta-se!** 🚀

---

**Última atualização:** Junho 2024  
**Status:** Documentação Completa ✅

