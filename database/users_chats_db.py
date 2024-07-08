# @codeflix-bots

import datetime
import pytz
from motor.motor_asyncio import AsyncIOMotorClient
from info import *
# from utils import get_seconds
client = AsyncIOMotorClient(DATABASE_URI)
mydb = client[DATABASE_NAME]
fsubs = client['fsubs']
class Database:
    default = SETTINGS.copy()
    def __init__(self):
        self.col = mydb.users
        self.grp = mydb.groups
        self.misc = mydb.misc
        self.verify_id = mydb.verify_id
        self.users = mydb.uersz
        self.req = mydb.requests
        self.mGrp = mydb.mGrp
        self.pmMode = mydb.pmMode
        self.stream_link = mydb.stream_link
        self.grp_and_ids = fsubs.grp_and_ids
        self.movies_update_channel = mydb.movies_update_channel
        self.update_post_mode = mydb.update_post_mode
    def new_user(self, id, name):
        return dict(
            id = id,
            name = name,
            point = 0,
            ban_status=dict(
                is_banned=False,
                ban_reason=""
            )
        )

    async def get_settings(self, id):
        chat = await self.grp.find_one({'id':int(id)})
        if chat:
            return chat.get('settings', self.default)
        else:
            await self.grp.update_one({'id': int(id)}, {'$set': {'settings': self.default}} , upsert=True)
        return self.default

    async def find_join_req(self, id):
        return bool(await self.req.find_one({'id': id}))
        
    async def add_join_req(self, id):
        await self.req.insert_one({'id': id})

    async def del_join_req(self):
        await self.req.drop()

    def new_group(self, id, title):
        return dict(
            id = id,
            title = title,
            chat_status=dict(
                is_disabled=False,
                reason=""
            )
        )
    
    async def add_user(self, id, name):
        user = self.new_user(id, name)
        await self.col.insert_one(user)
        
    async def update_point(self ,id):
        await self.col.update_one({'id' : id} , {'$inc':{'point' : 100}})
        point = (await self.col.find_one({'id' : id}))['point']
        if point >= PREMIUM_POINT :
            seconds = (REF_PREMIUM * 24 * 60 * 60)
            oldEx =(await self.users.find_one({'id' : id}))
            if oldEx :
                expiry_time = oldEx['expiry_time'] + datetime.timedelta(seconds=seconds)
            else: 
                expiry_time = datetime.datetime.now() + datetime.timedelta(seconds=seconds)
            user_data = {"id": id, "expiry_time": expiry_time}
            await db.update_user(user_data)
            await self.col.update_one({'id' : id} , {'$set':{'point' : 0}})

    async def get_point(self , id):
        newPoint = await self.col.find_one({'id' : id})
        return newPoint['point'] if newPoint else None
        
    async def is_user_exist(self, id):
        user = await self.col.find_one({'id':int(id)})
        return bool(user)
    
    async def total_users_count(self):
        count = await self.col.count_documents({})
        return count
    
    async def get_all_users(self):
        return self.col.find({})

    async def delete_user(self, user_id):
        await self.col.delete_many({'id': int(user_id)})

    async def delete_chat(self, id):
        await self.grp.delete_many({'id': int(id)})
        
    async def get_banned(self):
        users = self.col.find({'ban_status.is_banned': True})
        chats = self.grp.find({'chat_status.is_disabled': True})
        b_chats = [chat['id'] async for chat in chats]
        b_users = [user['id'] async for user in users]
        return b_users, b_chats
    
    async def add_chat(self, chat, title):
        chat = self.new_group(chat, title)
        await self.grp.insert_one(chat)

    async def get_chat(self, chat):
        chat = await self.grp.find_one({'id':int(chat)})
        return False if not chat else chat.get('chat_status')  

    async def update_settings(self, id, settings):
        await self.grp.update_one({'id': int(id)}, {'$set': {'settings': settings}})   
    
    async def total_chat_count(self):
        count = await self.grp.count_documents({})
        return count
    
    async def get_all_chats(self):
        return self.grp.find({})

    async def get_db_size(self):
        return (await mydb.command("dbstats"))['dataSize'] 

    async def get_notcopy_user(self, user_id):
        user_id = int(user_id)
        user = await self.misc.find_one({"user_id": user_id})
        ist_timezone = pytz.timezone('Asia/Kolkata')
        if not user:
            res = {
                "user_id": user_id,
                "last_verified": datetime.datetime(2020, 5, 17, 0, 0, 0, tzinfo=ist_timezone),
                "second_time_verified": datetime.datetime(2019, 5, 17, 0, 0, 0, tzinfo=ist_timezone),
            }
            user = await self.misc.insert_one(res)
        return user

    async def update_notcopy_user(self, user_id, value:dict):
        user_id = int(user_id)
        myquery = {"user_id": user_id}
        newvalues = {"$set": value}
        return await self.misc.update_one(myquery, newvalues)

    async def is_user_verified(self, user_id):
        user = await self.get_notcopy_user(user_id)
        try:
            pastDate = user["last_verified"]
        except Exception:
            user = await self.get_notcopy_user(user_id)
            pastDate = user["last_verified"]
        ist_timezone = pytz.timezone('Asia/Kolkata')
        pastDate = pastDate.astimezone(ist_timezone)
        current_time = datetime.datetime.now(tz=ist_timezone)
        seconds_since_midnight = (current_time - datetime.datetime(current_time.year, current_time.month, current_time.day, 0, 0, 0, tzinfo=ist_timezone)).total_seconds()
        time_diff = current_time - pastDate
        total_seconds = time_diff.total_seconds()
        return total_seconds <= seconds_since_midnight

    async def user_verified(self, user_id):
        user = await self.get_notcopy_user(user_id)
        try:
            pastDate = user["second_time_verified"]
        except Exception:
            user = await self.get_notcopy_user(user_id)
            pastDate = user["second_time_verified"]
        ist_timezone = pytz.timezone('Asia/Kolkata')
        pastDate = pastDate.astimezone(ist_timezone)
        current_time = datetime.datetime.now(tz=ist_timezone)
        seconds_since_midnight = (current_time - datetime.datetime(current_time.year, current_time.month, current_time.day, 0, 0, 0, tzinfo=ist_timezone)).total_seconds()
        time_diff = current_time - pastDate
        total_seconds = time_diff.total_seconds()
        return total_seconds <= seconds_since_midnight

    async def use_second_shortener(self, user_id, time):
        user = await self.get_notcopy_user(user_id)
        if not user.get("second_time_verified"):
            ist_timezone = pytz.timezone('Asia/Kolkata')
            await self.update_notcopy_user(user_id, {"second_time_verified":datetime.datetime(2019, 5, 17, 0, 0, 0, tzinfo=ist_timezone)})
            user = await self.get_notcopy_user(user_id)
        if await self.is_user_verified(user_id):
            try:
                pastDate = user["last_verified"]
            except Exception:
                user = await self.get_notcopy_user(user_id)
                pastDate = user["last_verified"]
            ist_timezone = pytz.timezone('Asia/Kolkata')
            pastDate = pastDate.astimezone(ist_timezone)
            current_time = datetime.datetime.now(tz=ist_timezone)
            time_difference = current_time - pastDate
            if time_difference > datetime.timedelta(seconds=time):
                pastDate = user["last_verified"].astimezone(ist_timezone)
                second_time = user["second_time_verified"].astimezone(ist_timezone)
                return second_time < pastDate
        return False

    async def use_third_shortener(self, user_id, time):
        user = await self.get_notcopy_user(user_id)
        if not user.get("third_time_verified"):
            ist_timezone = pytz.timezone('Asia/Kolkata')
            await self.update_notcopy_user(user_id, {"third_time_verified":datetime.datetime(2018, 5, 17, 0, 0, 0, tzinfo=ist_timezone)})
            user = await self.get_notcopy_user(user_id)
        if await self.user_verified(user_id):
            try:
                pastDate = user["second_time_verified"]
            except Exception:
                user = await self.get_notcopy_user(user_id)
                pastDate = user["second_time_verified"]
            ist_timezone = pytz.timezone('Asia/Kolkata')
            pastDate = pastDate.astimezone(ist_timezone)
            current_time = datetime.datetime.now(tz=ist_timezone)
            time_difference = current_time - pastDate
            if time_difference > datetime.timedelta(seconds=time):
                pastDate = user["second_time_verified"].astimezone(ist_timezone)
                second_time = user["third_time_verified"].astimezone(ist_timezone)
                return second_time < pastDate
        return False
   
    async def create_verify_id(self, user_id: int, hash):
        res = {"user_id": user_id, "hash":hash, "verified":False}
        return await self.verify_id.insert_one(res)

    async def get_verify_id_info(self, user_id: int, hash):
        return await self.verify_id.find_one({"user_id": user_id, "hash": hash})

    async def update_verify_id_info(self, user_id, hash, value: dict):
        myquery = {"user_id": user_id, "hash": hash}
        newvalues = { "$set": value }
        return await self.verify_id.update_one(myquery, newvalues)

    async def get_user(self, user_id):
        user_data = await self.users.find_one({"id": user_id})
        return user_data
        
    async def update_user(self, user_data):
        await self.users.update_one({"id": user_data["id"]}, {"$set": user_data}, upsert=True)

    async def has_premium_access(self, user_id):
        user_data = await self.get_user(user_id)
        if user_data:
            expiry_time = user_data.get("expiry_time")
            if expiry_time is None:
                return False
            elif isinstance(expiry_time, datetime.datetime) and datetime.datetime.now() <= expiry_time:
                return True
            else:
                await self.users.update_one({"id": user_id}, {"$set": {"expiry_time": None}})
        return False
        
    async def update_one(self, filter_query, update_data):
        try:
            result = await self.users.update_one(filter_query, update_data)
            return result.matched_count == 1
        except Exception as e:
            print(f"Error updating document: {e}")
            return False

    async def get_expired(self, current_time):
        expired_users = []
        if data := self.users.find({"expiry_time": {"$lt": current_time}}):
            async for user in data:
                expired_users.append(user)
        return expired_users

    async def remove_premium_access(self, user_id):
        return await self.update_one(
            {"id": user_id}, {"$set": {"expiry_time": None}}
        )
    async def get_set_grp_links(self , links=None , ispm = None, index = 0):
        try:
            if (links and ispm) is not None :
                await self.mGrp.update_one({} , {'$set': {'links': links , "ispm": bool(ispm)}}, upsert=True)
            else:
                myLinks = await self.mGrp.find_one({})
                if myLinks is not None:
                    if index == 0:
                        return myLinks.get("links")[0] , myLinks.get("ispm")
                    
                    else :
                        return myLinks.get("links")[1]
                else:
                    if index == 0:
                        return "https://t.me/movie7xchat" , False
                    else :
                        return "https://t.me/movie7xchat"
        except Exception as e:
            print(f"got err in db set : {e}")
    async def set_stream_link(self,link):
        await self.stream_link.update_one({} , {'$set': {'link': link}} , upsert=True)
    async def get_stream_link(self):
        link = await self.stream_link.find_one({})
        if link is not None:
            return link.get("link")
        else:
            return None
    async def del_stream_link(self):
        try: 
            isDeleted = await self.stream_link.delete_one({})
            if isDeleted.deleted_count > 0:
                return True
            else:
                return False
        except Exception as e:
            print(f"Got err in db set : {e}")
            return False
    async def setFsub(self , grpID , fsubID):
        return await self.grp_and_ids.update_one({'grpID': grpID} , {'$set': {'grpID': grpID , "fsubID": fsubID}}, upsert=True)    
    async def getFsub(self , grpID):
        link = await self.grp_and_ids.find_one({"grpID": grpID})
        if link is not None:
            return link.get("fsubID")
        else:
            return None
    async def delFsub(self , grpID):
        result =  await self.grp_and_ids.delete_one({"grpID": grpID})
        if result.deleted_count != 0:
            return True
        else:
            return False
    async def movies_update_channel_id(self , id=None):
        if id is None:
            myLinks = await self.movies_update_channel.find_one({})
            if myLinks is not None:
                return myLinks.get("id")
            else:
                return None
        return await self.movies_update_channel.update_one({} , {'$set': {'id': id}} , upsert=True)
    async def del_movies_channel_id(self):
        try: 
            isDeleted = await self.movies_update_channel.delete_one({})
            if isDeleted.deleted_count > 0:
                return True
            else:
                return False
        except Exception as e:
            print(f"Got err in db set : {e}")
            return False
    async def update_post_mode_handle(self, index=0):
        post_mode = await self.update_post_mode.find_one({})
        if post_mode is None:
            post_mode = DEFAULT_POST_MODE
        if index == 1:
            post_mode["singel_post_mode"] = not post_mode.get("singel_post_mode", True)
        elif index == 2:
            post_mode["all_files_post_mode"] = not post_mode.get("all_files_post_mode", True)
        
        await self.update_post_mode.update_one({}, {"$set": post_mode}, upsert=True)
        
        return post_mode
db = Database()
