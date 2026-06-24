"""
Script de inicialização do banco de dados
Execute este arquivo para criar o banco de dados com dados de exemplo
"""

from app import app, db
from models import User, SubscriptionPlan
from datetime import datetime, timedelta

def init_db():
    with app.app_context():
        # Criar todas as tabelas
        db.create_all()
        
        # Criar planos de assinatura
        free_plan = SubscriptionPlan.query.filter_by(name='free').first()
        if not free_plan:
            free_plan = SubscriptionPlan(
                name='free',
                price=0,
                currency='BRL',
                max_videos_per_day=3,
                description='Plano gratuito com limite de 3 resumos por dia'
            )
            db.session.add(free_plan)
        
        premium_plan = SubscriptionPlan.query.filter_by(name='premium').first()
        if not premium_plan:
            premium_plan = SubscriptionPlan(
                name='premium',
                price=19.99,
                currency='BRL',
                max_videos_per_day=-1,  # Ilimitado
                description='Plano premium com resumos ilimitados'
            )
            db.session.add(premium_plan)
        
        db.session.commit()
        
        print("✅ Banco de dados inicializado com sucesso!")
        print("📊 Planos criados:")
        print("   - Gratuito: 3 resumos/dia")
        print("   - Premium: Ilimitado (R$19,99/mês)")

if __name__ == '__main__':
    init_db()
