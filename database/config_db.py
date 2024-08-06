from motor.motor_asyncio import AsyncIOMotorClient
from info import DATABASE_URI
from datetime import datetime

class Database:
    def __init__(self, uri, db_name):
        self.client = AsyncIOMotorClient(uri)
        self.db = self.client[db_name]
        self.col = self.db.user
        self.config_col = self.db.configuration

    async def update_top_messages(self, user_id, message_text):
        user = await self.col.find_one({"user_id": user_id, "messages.text": message_text})
        
        if not user:
            await self.col.update_one(
                {"user_id": user_id},
                {"$push": {"messages": {"text": message_text, "count": 1}}},
                upsert=True
            )
        else:
            await self.col.update_one(
                {"user_id": user_id, "messages.text": message_text},
                {"$inc": {"messages.$.count": 1}}
            )

    async def get_top_messages(self, limit=30):
        pipeline = [
            {"$unwind": "$messages"},
            {"$group": {"_id": "$messages.text", "count": {"$sum": "$messages.count"}}},
            {"$sort": {"count": -1}},
            {"$limit": limit}
        ]
        results = await self.col.aggregate(pipeline).to_list(limit)
        return [result['_id'] for result in results]
    
    async def delete_all_messages(self):
        await self.col.delete_many({})

    def create_configuration_data(
            self, maintenance_mode=False,
            auto_accept=True,
            one_link=True,
            one_link_one_file_group=False,
            private_filter=True,
            group_filter=True,
            terms=True,
            spoll_check=True,
            forcesub=True,
            shortner=None,
            no_ads=False,
            advertisement=None):
        
        return {
            'maintenance_mode': maintenance_mode,
            'auto_accept': auto_accept,
            'one_link': one_link,
            'one_link_one_file_group': one_link_one_file_group,
            'private_filter': private_filter,
            'group_filter': group_filter,
            'terms': terms,
            'spoll_check': spoll_check,
            'forcesub': forcesub,
            'shortner': shortner,
            'no_ads': no_ads,
            'advertisement': advertisement,
        }
    
    
    async def update_advirtisment(self, ads_string=None, ads_name=None, expiry=None, impression=None):
        config = await self.config_col.find_one({})
        if not config:
            await self.config_col.insert_one(self.create_configuration_data())
            config = await self.config_col.find_one({})

        advertisement = config.get('advertisement')

        if advertisement is None:
            # If 'advertisement' field is not present, create it
            advertisement = {}
            config['advertisement'] = advertisement

        # Update the fields within the 'advertisement' field
        advertisement['ads_string'] = ads_string
        advertisement['ads_name'] = ads_name
        advertisement['expiry'] = expiry
        advertisement['impression_count'] = impression

        await self.config_col.update_one({}, {'$set': {'advertisement': advertisement}}, upsert=True)

    async def update_advirtisment_impression(self, impression=None):
        await self.config_col.update_one({}, {'$set': {'advertisement.impression_count': impression}}, upsert=True)

    async def get_advirtisment(self):
        configuration = await self.config_col.find_one({})
        if not configuration:
            await self.config_col.insert_one(self.create_configuration_data())
            configuration = await self.config_col.find_one({})
        advertisement = configuration.get('advertisement', False)
        if advertisement:
            return advertisement.get('ads_string'), advertisement.get('ads_name'), advertisement.get('impression_count')
        return None, None, None

    async def reset_advertisement_if_expired(self):
        configuration = await self.config_col.find_one({})
        if configuration:
            advertisement = configuration.get('advertisement', False)
            if advertisement:
                impression_count = advertisement.get('impression_count', 0)
                expiry = advertisement.get('expiry', None)
                if (impression_count == 0) or (expiry and datetime.now() > expiry):
                    await self.config_col.update_one({}, {'$set': {'advertisement': None}})

    
    async def update_configuration(self, key, value):
        try:
            await self.config_col.update_one({}, {'$set': {key: value}}, upsert=True)

        except Exception as e:
            print(f"An error occurred: {e}")

    async def get_configuration_value(self, key):
        configuration = await self.config_col.find_one({})
        if not configuration:
            await self.config_col.insert_one(self.create_configuration_data())
            configuration = await self.config_col.find_one({})
        return configuration.get(key, False)


mdb = Database(DATABASE_URI, "admin_database")