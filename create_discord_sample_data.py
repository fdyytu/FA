"""
Script untuk menambahkan sample data Discord logs dan commands
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.core.database import get_db, engine
from app.domains.discord.models.discord import (
    DiscordBot, DiscordUser, DiscordLog, DiscordCommand
)
from datetime import datetime, timedelta
import random

def create_sample_data():
    """Buat sample data untuk testing"""
    db = next(get_db())
    
    try:
        # Buat sample Discord bot jika belum ada
        bot = db.query(DiscordBot).first()
        if not bot:
            bot = DiscordBot(
                bot_name="Test Bot",
                bot_token="test_token_encrypted",
                guild_id="123456789012345678",
                live_stock_channel_id="987654321098765432",
                status="ACTIVE",
                is_active=True
            )
            db.add(bot)
            db.commit()
            db.refresh(bot)
            print(f"Created sample bot: {bot.bot_name}")
        
        # Buat sample Discord users jika belum ada
        users = db.query(DiscordUser).limit(3).all()
        if len(users) < 3:
            sample_users = [
                DiscordUser(
                    discord_id="111111111111111111",
                    discord_username="TestUser1",
                    grow_id="TESTUSER1",
                    is_verified=True,
                    is_active=True
                ),
                DiscordUser(
                    discord_id="222222222222222222",
                    discord_username="TestUser2",
                    grow_id="TESTUSER2",
                    is_verified=True,
                    is_active=True
                ),
                DiscordUser(
                    discord_id="333333333333333333",
                    discord_username="TestUser3",
                    grow_id="TESTUSER3",
                    is_verified=False,
                    is_active=True
                )
            ]
            
            for user in sample_users:
                existing = db.query(DiscordUser).filter(DiscordUser.discord_id == user.discord_id).first()
                if not existing:
                    db.add(user)
            
            db.commit()
            users = db.query(DiscordUser).limit(3).all()
            print(f"Created {len(users)} sample users")
        
        # Buat sample Discord logs
        log_count = db.query(DiscordLog).count()
        if log_count < 20:
            log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
            log_actions = ['command', 'event', 'error', 'startup', 'shutdown']
            log_messages = [
                'Bot started successfully',
                'User executed command',
                'Database connection established',
                'Error processing command',
                'Warning: High memory usage',
                'Critical: Database connection lost',
                'Debug: Processing user request',
                'Info: Command completed successfully'
            ]
            
            for i in range(20):
                created_time = datetime.utcnow() - timedelta(
                    days=random.randint(0, 7),
                    hours=random.randint(0, 23),
                    minutes=random.randint(0, 59)
                )
                
                log = DiscordLog(
                    user_id=random.choice(users).id if random.choice([True, False]) else None,
                    bot_id=bot.id,
                    level=random.choice(log_levels),
                    message=random.choice(log_messages),
                    action=random.choice(log_actions),
                    channel_id="987654321098765432",
                    guild_id="123456789012345678",
                    created_at=created_time
                )
                db.add(log)
            
            db.commit()
            print("Created 20 sample Discord logs")
        
        # Buat sample Discord commands
        command_count = db.query(DiscordCommand).count()
        if command_count < 15:
            command_names = ['help', 'balance', 'buy', 'sell', 'inventory', 'profile', 'stats', 'ping']
            
            for i in range(15):
                created_time = datetime.utcnow() - timedelta(
                    days=random.randint(0, 3),
                    hours=random.randint(0, 23),
                    minutes=random.randint(0, 59)
                )
                
                success = random.choice([True, True, True, False])  # 75% success rate
                
                command = DiscordCommand(
                    user_id=random.choice(users).id,
                    command_name=random.choice(command_names),
                    command_args='{"arg1": "value1"}' if random.choice([True, False]) else None,
                    channel_id="987654321098765432",
                    guild_id="123456789012345678",
                    success=success,
                    execution_time=round(random.uniform(0.1, 2.5), 4),
                    error_message="Command failed" if not success else None,
                    response_message="Command executed successfully" if success else None,
                    created_at=created_time
                )
                db.add(command)
            
            db.commit()
            print("Created 15 sample Discord commands")
        
        print("Sample data creation completed!")
        
    except Exception as e:
        print(f"Error creating sample data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_sample_data()
