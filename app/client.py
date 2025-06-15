import asyncio
import aiohttp
import base64


async def create_users():
    users = [
        {"nickname": "test_user1", "email": "a1@a.a", "password": "1234"},
        {"nickname": "test_user2", "email": "a2@a.a", "password": "4321"},
        {"nickname": "test_admin", "email": "admin@a.a", "password": "007", "is_admin": True}
    ]

    async with aiohttp.ClientSession() as session:
        for user in users:
            async with session.post(
                "http://localhost:5000/users/",
                json=user
            ) as resp:
                print(f"Создан пользователь {user['nickname']}: {resp.status}")


async def get_tokens():
    users = [
        {"nickname": "test_user1", "password": "1234"},
        {"nickname": "test_user2", "password": "4321"},
        {"nickname": "test_admin", "password": "007"}
    ]
    tokens = {}

    async with aiohttp.ClientSession() as session:
        for user in users:
            auth = base64.b64encode(f"{user['nickname']}:{user['password']}".encode()).decode()
            async with session.post(
                "http://localhost:5000/tokens/",
                headers={"Authorization": f"Basic {auth}"}
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    tokens[user['nickname']] = data['token']
                    print(f"Токен для {user['nickname']}: {tokens[user['nickname']]}")
                else:
                    print(f"Ошибка получения токена для {user['nickname']}: {await resp.text()}")

    return tokens


async def create_adv(token):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "http://localhost:5000/advs/",
            json={"title": "Тестовое объявление", "desc": "Описание объявления", "owner": "test_user1"},
            headers={"token": token}
        ) as resp:
            print(f"Создание объявления: {resp.status} - {await resp.text()}")


async def update_adv(token):
    async with aiohttp.ClientSession() as session:
        async with session.patch(
            "http://localhost:5000/advs/1",
            json={"desc": "Обновленное описание"},
            headers={"token": token}
        ) as resp:
            print(f"Обновление объявления: {resp.status} - {await resp.text()}")


async def main():
    await create_users()
    tokens = await get_tokens()

    if 'test_admin' in tokens:
        await create_adv(tokens['test_admin'])
        await update_adv(tokens['test_admin'])


if __name__ == '__main__':
    asyncio.run(main())
