from pyrogram import *
from pyrogram.types import *



@Client.on_message(filters.command("promote") & filters.group)
async def promoting(client, message):
     global new_admin
     if not message.reply_to_message:
         return await message.reply("use this command reply")
     reply = message.reply_to_message
     chat_id = message.chat.id
     new_admin = reply.from_user
     admin = message.from_user
     user_stats = await client.get_chat_member(chat_id, admin.id)
     bot_stats = await client.get_chat_member(chat_id, "self")
     if not bot_stats.privileges:
         return await message.reply("hey dude iam not admin")
     elif not user_stats.privileges:
         return await message.reply("Sorry dude you need admin")
     elif not bot_stats.privileges.can_promote_members:
         return await message.reply("i dont have admin rights ")
     elif not user_stats.privileges.can_promote_members:
         return await message.reply("you need admin rights 😒")
     elif user_stats.privileges.can_promote_members:
          msg = await message.reply_text("Promoting")
          await client.promote_chat_member(
            message.chat.id,
            new_admin.id,
            privileges=pyrogram.types.ChatPrivileges(
            can_change_info=True,
            can_delete_messages=True,
            can_pin_messages=True,
            can_invite_users=True,
            can_manage_video_chats=True,
            can_restrict_members=True
))
          await msg.edit(f"Alright!! Successful promoted")


@Client.on_message(filters.command("demote") & filters.group)
async def demote(client, message):
     global new_admin
     if not message.reply_to_message:
         return await message.reply("use this command reply")
     reply = message.reply_to_message
     chat_id = message.chat.id
     new_admin = reply.from_user
     admin = message.from_user
     user_stats = await client.get_chat_member(chat_id, admin.id)
     bot_stats = await client.get_chat_member(chat_id, "self")
     if not bot_stats.privileges:
         return await message.reply("hey dude iam not admin")
     elif not user_stats.privileges:
         return await message.reply("Sorry dude you need admin")
     elif not bot_stats.privileges.can_promote_members:
         return await message.reply("i dont have admin rights ")
     elif not user_stats.privileges.can_promote_members:
         return await message.reply("you need admin rights 😒")
     elif user_stats.privileges.can_promote_members:
          msg = await message.reply_text("`Proccing...`")
          await client.promote_chat_member(
            chat_id,
            new_admin.id,
            privileges=pyrogram.types.ChatPrivileges(
            can_change_info=False,
            can_invite_users=False,
            can_delete_messages=False,
            can_restrict_members=False,
            can_pin_messages=False,
            can_promote_members=False,
            can_manage_chat=False,
            can_manage_video_chats=False    
))
          await msg.edit(f"Hmm!! demoted 🥺 ")
