# ⚡ INÍCIO RÁPIDO - ResumosAI

## 5 Passos para Começar em 5 Minutos

### 1️⃣ Instalar (1 minuto)

**Windows:**
- Duplo-clique em `setup.bat`
- Aguarde "Setup Concluído!"

**Linux/Mac:**
```bash
chmod +x setup.sh
./setup.sh
```

### 2️⃣ Configurar Google AI (2 minutos)

1. Vá para: https://makersuite.google.com/app/apikey
2. Clique em "Create API Key"
3. Copie a chave
4. Abra `.env` e substitua `GOOGLE_API_KEY=` com sua chave

Exemplo:
```env
GOOGLE_API_KEY=AIzaSyDxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 3️⃣ Iniciar o Servidor (30 segundos)

```bash
# Ativar ambiente (se não estiver ativado)
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Rodar
python app.py
```

Você verá:
```
 * Running on http://127.0.0.1:5000
```

### 4️⃣ Acessar o Site (30 segundos)

Abra no navegador: **http://localhost:5000**

### 5️⃣ Testar (1 minuto)

1. Clique em "Cadastro"
2. Preencha os dados
3. Clique em "Começar Agora"
4. Cole qualquer URL do YouTube: https://www.youtube.com/watch?v=jNQXAC9IVRw
5. Clique em "Gerar Resumo"

**Pronto! ✅**

---

## 🧪 Credenciais de Teste

Você também pode usar o usuário de teste criado:

- **Username**: teste
- **Senha**: senha123

---

## 🆘 Problemas Comuns?

| Problema | Solução |
|----------|---------|
| "ModuleNotFoundError" | Ative o venv e reinstale: `pip install -r requirements.txt` |
| "Port 5000 already in use" | Mude a porta em app.py última linha para 5001 |
| "API Key inválida" | Verifique a chave em .env |
| "Sem transcrição" | Use outro vídeo do YouTube com legendas |

---

## 📚 Próximos Passos

1. Leia **PROJETO_COMPLETO.md** para entender tudo
2. Leia **GUIA_INSTALACAO.md** para detalhes
3. Explore o código em `routes.py`
4. Configure Stripe se quiser pagamentos reais

---

**Questões? Consulte os arquivos .md na pasta do projeto!** 📖

