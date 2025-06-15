import asyncio
from aiohttp import web
from sqlalchemy import select
from models import Base, engine, Session, User, Adv  # Добавлен импорт User и Adv

async def init_db(app):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with Session() as session:
        result = await session.execute(select(User))
        if not result.scalars().first():
            test_user = User(
                nickname="admin",
                email="admin@example.com",
                is_admin=True
            )
            test_user.set_password("admin")
            session.add(test_user)
            await session.commit()

async def handle_index(request):
    return web.json_response({"status": "ok"})

async def create_user(request):
    data = await request.json()
    async with Session() as session:
        user = User(
            nickname=data['nickname'],
            email=data['email'],
            is_admin=data.get('is_admin', False)
        )
        user.set_password(data['password'])
        session.add(user)
        await session.commit()
        return web.json_response({"id": user.id})

async def init_app():
    app = web.Application()
    app.on_startup.append(init_db)
    
    # Добавляем роуты
    app.router.add_get("/", handle_index)
    app.router.add_post("/users/", create_user)
    
    return app

if __name__ == '__main__':
    web.run_app(init_app(), port=5000, host='0.0.0.0')
