#!/usr/bin/env python3
"""
Crear usuario admin rápidamente
"""
import asyncio
import sys
import os

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timezone
from passlib.context import CryptContext
from sqlalchemy import select
from app.core.database import AsyncSessionLocal, engine
from app.models import User, UserRole

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# SECURITY: Must be set via environment variables
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@costaricatravel.dev")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")
if not ADMIN_PASSWORD:
    raise ValueError("ADMIN_PASSWORD must be set in environment variables!")

async def create_admin():
    async with AsyncSessionLocal() as db:
        # Check if admin exists
        result = await db.execute(
            select(User).where(User.email == ADMIN_EMAIL)
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            print(f"✓ Admin ya existe: {ADMIN_EMAIL}")
            return
        
        import uuid
        admin = User(
            id=uuid.uuid4(),
            email=ADMIN_EMAIL,
            password_hash=pwd_context.hash(ADMIN_PASSWORD),
            full_name="Super Admin",
            phone="+50688888888",
            role=UserRole.SUPER_ADMIN,
            is_active=True,
            is_verified=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        db.add(admin)
        await db.commit()
        print(f"✅ Admin creado: {ADMIN_EMAIL}")
        print(f"🔑 Password: {'*' * len(ADMIN_PASSWORD)} (hidden for security)")
        
    await engine.dispose()

if __name__ == "__main__":
    print("Creando usuario admin...")
    asyncio.run(create_admin())
    print("Done!")
