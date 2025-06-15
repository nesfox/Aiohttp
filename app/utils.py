from aiohttp import web
from datetime import datetime
from models import Session, Adv, User
from sqlalchemy import select


async def get_adv(adv_id: int, session: Session) -> Adv:
    adv = await session.get(Adv, adv_id)
    if adv is None:
        raise web.HTTPBadRequest(text=f"adv_id {adv_id} not found")
    return adv


async def get_user(user_name: str, session: Session) -> User:
    result = await session.execute(select(User).where(User.nickname == user_name))
    user = result.scalar()
    if user is None:
        raise web.HTTPBadRequest(text=f"user {user_name} not found")
    return user


async def get_user_by_token(token: str, session: Session) -> User:
    result = await session.execute(select(User).where(User.token == token))
    user = result.scalar()
    if user is None or user.token_expiration < datetime.utcnow():
        raise web.HTTPUnauthorized(text="Invalid token")
    return user


async def access_granted(owner: User, token: str, session: Session) -> bool:
    token_user = await get_user_by_token(token, session)
    if token_user.is_admin or token_user.id == owner.id:
        return True
    raise web.HTTPUnauthorized(text=f"Wrong token for user {owner.nickname}")
