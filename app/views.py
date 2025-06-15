from aiohttp import web
from models import User, Adv, Session
from schemas import CreateAdvSchema, UpdateAdvSchema, UserSchema
from utils import get_adv, get_user, access_granted
from pydantic import ValidationError
from sqlalchemy import select


class AdvView(web.View):
    async def get(self):
        adv_id = int(self.request.match_info['adv_id'])
        async with Session() as session:
            adv = await get_adv(adv_id, session)
            return web.json_response({
                "title": adv.title,
                "description": adv.desc,
                "owner": adv.owner.nickname,
                "created_at": adv.created_at.isoformat()
            })

    async def post(self):
        try:
            data = await self.request.json()
            validated_data = CreateAdvSchema(**data).dict()
        except ValidationError as e:
            raise web.HTTPBadRequest(text=str(e))

        async with Session() as session:
            user = await get_user(validated_data.pop("owner"), session)
            token = self.request.headers.get("token")
            
            if not await access_granted(user, token, session):
                raise web.HTTPUnauthorized()

            adv = Adv(**validated_data, owner_id=user.id)
            session.add(adv)
            await session.commit()
            
            return web.json_response({
                "status": "success",
                "id": adv.id
            })

    async def patch(self):
        adv_id = int(self.request.match_info['adv_id'])
        try:
            data = await self.request.json()
            validated_data = UpdateAdvSchema(**data).dict(exclude_none=True)
        except ValidationError as e:
            raise web.HTTPBadRequest(text=str(e))

        async with Session() as session:
            adv = await get_adv(adv_id, session)
            token = self.request.headers.get("token")
            
            if not await access_granted(adv.owner, token, session):
                raise web.HTTPUnauthorized()

            for field, value in validated_data.items():
                setattr(adv, field, value)
            
            await session.commit()
            return web.json_response({
                "title": adv.title,
                "description": adv.desc
            })

    async def delete(self):
        adv_id = int(self.request.match_info['adv_id'])
        async with Session() as session:
            adv = await get_adv(adv_id, session)
            token = self.request.headers.get("token")
            
            if not await access_granted(adv.owner, token, session):
                raise web.HTTPUnauthorized()

            await session.delete(adv)
            await session.commit()
            return web.json_response(f"Adv with id {adv_id} deleted")


class UserView(web.View):
    async def post(self):
        try:
            data = await self.request.json()
            validated_data = UserSchema(**data).dict()
        except ValidationError as e:
            raise web.HTTPBadRequest(text=str(e))

        async with Session() as session:
            password = validated_data.pop("password")
            user = User(**validated_data)
            user.set_password(password)
            session.add(user)
            try:
                await session.commit()
            except Exception as e:
                raise web.HTTPBadRequest(text=str(e))
            
            return web.json_response({
                "status": "success",
                "hash": user.password_hash
            })


class TokenView(web.View):
    async def post(self):
        auth = self.request.headers.get("Authorization")
        if not auth:
            raise web.HTTPUnauthorized()
        
        try:
            auth_type, auth_data = auth.split(" ", 1)
            if auth_type.lower() != "basic":
                raise ValueError()
            username, password = base64.b64decode(auth_data).decode().split(":", 1)
        except (ValueError, UnicodeDecodeError):
            raise web.HTTPUnauthorized()

        async with Session() as session:
            user = await session.execute(
                select(User).where(User.nickname == username))
            user = user.scalar()
            if not user or not user.check_password(password):
                raise web.HTTPUnauthorized()

            token = user.get_token()
            await session.commit()
            return web.json_response({'token': token})


async def index(request):
    return web.json_response({
        "status": "success",
        "message": "Welcome to Netology Flask API",
        "endpoints": {
            "users": "POST /users/",
            "tokens": "POST /tokens/",
            "advertisements": {
                "create": "POST /advs/",
                "view": "GET /advs/<id>",
                "update": "PATCH /advs/<id>",
                "delete": "DELETE /advs/<id>"
            }
        }
    })