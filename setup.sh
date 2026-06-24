#!/bin/bash
# Script de instalação do ResumosAI para Linux/Mac

echo ""
echo "========================================"
echo "     ResumosAI - Setup Automático"
echo "========================================"
echo ""

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Erro: Python 3 não encontrado!"
    echo "Por favor, instale Python 3.8+ de https://www.python.org"
    exit 1
fi

echo "✅ Python encontrado"
echo ""

# Criar ambiente virtual
echo "Criando ambiente virtual..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Ambiente virtual criado"
else
    echo "ℹ️  Ambiente virtual já existe"
fi

echo ""
echo "Ativando ambiente virtual..."
source venv/bin/activate

echo "✅ Ambiente virtual ativado"
echo ""

# Instalar dependências
echo "Instalando dependências..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Erro ao instalar dependências"
    exit 1
fi

echo "✅ Dependências instaladas"
echo ""

# Inicializar banco de dados
echo "Inicializando banco de dados..."
python init_db.py

if [ $? -ne 0 ]; then
    echo "❌ Erro ao inicializar banco de dados"
    exit 1
fi

echo "✅ Banco de dados inicializado"
echo ""

# Criar usuário de teste
echo "Criando usuário de teste..."
python create_test_user.py

echo ""
echo "========================================"
echo "     Setup Concluído!"
echo "========================================"
echo ""
echo "📝 Próximos passos:"
echo ""
echo "1. Edite o arquivo .env com suas chaves:"
echo "   - GOOGLE_API_KEY (de https://makersuite.google.com/app/apikey)"
echo "   - STRIPE_PUBLIC_KEY e STRIPE_SECRET_KEY (opcional)"
echo ""
echo "2. Inicie o servidor:"
echo "   python app.py"
echo ""
echo "3. Acesse http://localhost:5000 no navegador"
echo ""
echo "ℹ️  Usuário de teste:"
echo "   Username: teste"
echo "   Senha: senha123"
echo ""
