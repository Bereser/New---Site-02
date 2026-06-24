@echo off
REM Script de instalação do ResumosAI para Windows
REM Execute este arquivo para configurar o ambiente automaticamente

echo.
echo ========================================
echo     ResumosAI - Setup Automático
echo ========================================
echo.

REM Verificar se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Erro: Python não encontrado!
    echo Por favor, instale Python 3.8+ de https://www.python.org
    pause
    exit /b 1
)

echo ✅ Python encontrado
echo.

REM Criar ambiente virtual
echo Criando ambiente virtual...
if not exist "venv" (
    python -m venv venv
    echo ✅ Ambiente virtual criado
) else (
    echo ℹ️  Ambiente virtual já existe
)

echo.
echo Ativando ambiente virtual...
call venv\Scripts\activate.bat

echo ✅ Ambiente virtual ativado
echo.

REM Instalar dependências
echo Instalando dependências...
pip install -r requirements.txt

if errorlevel 1 (
    echo ❌ Erro ao instalar dependências
    pause
    exit /b 1
)

echo ✅ Dependências instaladas
echo.

REM Inicializar banco de dados
echo Inicializando banco de dados...
python init_db.py

if errorlevel 1 (
    echo ❌ Erro ao inicializar banco de dados
    pause
    exit /b 1
)

echo ✅ Banco de dados inicializado
echo.

REM Criar usuário de teste (opcional)
echo Criando usuário de teste...
python create_test_user.py

echo.
echo ========================================
echo     Setup Concluído!
echo ========================================
echo.
echo 📝 Próximos passos:
echo.
echo 1. Edite o arquivo .env com suas chaves:
echo    - GOOGLE_API_KEY (de https://makersuite.google.com/app/apikey)
echo    - STRIPE_PUBLIC_KEY e STRIPE_SECRET_KEY (opcional)
echo.
echo 2. Inicie o servidor:
echo    python app.py
echo.
echo 3. Acesse http://localhost:5000 no navegador
echo.
echo ℹ️  Usuário de teste:
echo    Username: teste
echo    Senha: senha123
echo.
pause
