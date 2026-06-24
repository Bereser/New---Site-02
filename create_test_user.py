"""
Script para criar um usuário de teste (OPCIONAL)
"""

from app import app, db
from models import User

def create_test_user():
    with app.app_context():
        # Verificar se o usuário já existe
        existing_user = User.query.filter_by(username='teste').first()
        if existing_user:
            print("❌ Usuário 'teste' já existe")
            return
        
        # Criar novo usuário
        user = User(
            username='teste',
            email='teste@resumosai.com',
            full_name='Usuário Teste',
            plan='free'
        )
        user.set_password('senha123')
        
        db.session.add(user)
        db.session.commit()
        
        print("✅ Usuário de teste criado com sucesso!")
        print("   Username: teste")
        print("   Senha: senha123")
        print("   Email: teste@resumosai.com")

if __name__ == '__main__':
    create_test_user()
