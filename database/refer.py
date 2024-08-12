import pymongo

from info import DATABASE_URI, DATABASE_NAME

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

myclient = pymongo.MongoClient(DATABASE_URI)
mydb = myclient[DATABASE_NAME]


class UserTracker:
    def __init__(self):
        self.user_collection = mydb["referusers"]
        self.refer_collection = mydb["refers"]

    def add_user(self, user_id):
        if not self.is_user_in_list(user_id):
            self.user_collection.insert_one({'user_id': user_id})

    def remove_user(self, user_id):
        self.user_collection.delete_one({'user_id': user_id})

    def is_user_in_list(self, user_id):
        return bool(self.user_collection.find_one({'user_id': user_id}))

    def add_refer_points(self, user_id: int, points: int):
        self.refer_collection.update_one(
            {'user_id': user_id},
            {'$set': {'points': points}},
            upsert=True
        )

    def get_refer_points(self, user_id: int):
        user = self.refer_collection.find_one({'user_id': user_id})
        return user.get('points') if user else 0


referdb = UserTracker()
