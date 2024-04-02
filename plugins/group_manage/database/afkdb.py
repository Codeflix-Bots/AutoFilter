from plugins.group_manage.database import afkusers


async def is_afk(user_id: int) -> bool:
    user = await afkusers.find_one({"user_id": user_id})
    if not user:
        return False, {}
    return True, user["reason"]


async def add_afk(user_id: int, mode):
    await afkusers.update_one(
        {"user_id": user_id}, {"$set": {"reason": mode}}, upsert=True
    )


async def remove_afk(user_id: int):
    user = await afkusers.find_one({"user_id": user_id})
    if user:
        return await afkusers.delete_one({"user_id": user_id})


async def get_afk_users() -> list:
    users = afkusers.find({"user_id": {"$gt": 0}})
    if not users:
        return []
    users_list = []
    for user in await users.to_list(length=1000000000):
        users_list.append(user)
    return users_list
