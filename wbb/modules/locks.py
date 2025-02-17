"""
MIT License

Copyright (c) 2021 TheHamkerCat

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
from wbb import SUDOERS, app
from wbb.modules.admin import member_permissions, current_chat_permissions
from wbb.core.decorators.errors import capture_err
from pyrogram import filters
from pyrogram.types import ChatPermissions
from pyrogram.errors.exceptions.bad_request_400 import ChatNotModified

__MODULE__ = "Locks"
__HELP__ = """
Commands: /lock | /unlock | /locks [No Parameters Required]

Parameters:
    messages | stickers | gifs | media | games | polls

    inline  | link_previews | group_info | user_add | pin

You can only pass the "all" parameter with /lock, not with /unlock

Example:
    /lock all
"""

incorrect_parameters = "Incorrect Parameters, Check Locks Section In Help."
data = {
    "messages": "can_send_messages",
    "stickers": "can_send_stickers",
    "gifs": "can_send_animations",
    "media": "can_send_media_messages",
    "games": "can_send_games",
    "inline": "can_use_inline_bots",
    "link_previews": "can_add_web_page_previews",
    "polls": "can_send_polls",
    "group_info": "can_change_info",
    "useradd": "can_invite_users",
    "pin": "can_pin_messages"
}


async def tg_lock(message, permissions: list, perm: str, lock: bool):
    if lock:
        if perm not in permissions:
            await message.reply_text("Already locked.")
            return
    else:
        if perm in permissions:
            await message.reply_text("Already Unlocked.")
            return
    (permissions.remove(perm) if lock else permissions.append(perm))
    permissions = {perm: True for perm in list(set(permissions))}
    try:
        await app.set_chat_permissions(message.chat.id, ChatPermissions(**permissions))
    except ChatNotModified:
        await message.reply_text("To unlock this, you have to unlock 'messages' first.")
        return
    await message.reply_text(("Locked." if lock else "Unlocked."))


@app.on_message(filters.command(["lock", "unlock"]) & ~filters.private)
@capture_err
async def locks_func(_, message):
    try:
        user_id = message.from_user.id
        chat_id = message.chat.id
        if len(message.command) != 2:
            await message.reply_text(incorrect_parameters)
            return

        parameter = message.text.strip().split(None, 1)[1].lower()
        state = message.command[0].lower()
        if parameter not in data and parameter != "all":
            await message.reply_text(incorrect_parameters)
            return

        permissions = await member_permissions(chat_id, user_id)
        if "can_restrict_members" not in permissions and user_id not in SUDOERS:
            await message.reply_text("You Don't Have Enough Permissions.")
            return

        permissions = await current_chat_permissions(chat_id)
        if parameter in data:
            await tg_lock(message, permissions, data[parameter], True if state == "lock" else False)
            return
        elif parameter == "all" and state == "lock":
            await app.set_chat_permissions(chat_id, ChatPermissions())
            await message.reply_text("Locked Everything.")
    except Exception as e:
        await message.reply_text(str(e))
        print(e)


@app.on_message(filters.command("locks") & ~filters.private)
async def locktypes(_, message):
    permissions = await current_chat_permissions(message.chat.id)
    if not permissions:
        await message.reply_text("No Permissions.")
        return
    perms = ""
    for i in permissions:
        perms += f"__**{i}**__\n"
    await message.reply_text(perms)
