import random
import humanize
from Script import script
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ForceReply, CallbackQuery
from info import URL, LOG_CHANNEL, SHORTLINK
from urllib.parse import quote_plus
from TechVJ.util.file_properties import get_name, get_hash, get_media_file_size
from TechVJ.util.human_readable import humanbytes
from database.users_chats_db import db
from utils import temp, get_shortlink
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@Client.on_message(filters.command("start") & filters.incoming)
async def start(client, message):
    try:
        if not await db.is_user_exist(message.from_user.id):
            await db.add_user(message.from_user.id, message.from_user.first_name)
            await client.send_message(LOG_CHANNEL, script.LOG_TEXT_P.format(message.from_user.id, message.from_user.mention))
        rm = InlineKeyboardMarkup(
            [[
                InlineKeyboardButton("✨ Update Channel", url="https://t.me/sdbots1")
            ]]
        )
        await client.send_message(
            chat_id=message.from_user.id,
            text=script.START_TXT.format(message.from_user.mention, temp.U_NAME, temp.B_NAME),
            reply_markup=rm,
            parse_mode=enums.ParseMode.HTML
        )
    except Exception as e:
        logger.error(f"Error in start command: {str(e)}")
        await client.send_message(
            chat_id=message.from_user.id,
            text="An error occurred while processing the /start command. Please try again later."
        )

@Client.on_message(filters.private & (filters.document | filters.video))
async def stream_start(client, message):
    try:
        file = getattr(message, message.media.value)
        filename = file.file_name
        filesize = humanize.naturalsize(file.file_size)
        fileid = file.file_id
        user_id = message.from_user.id
        username = message.from_user.mention

        log_msg = await client.send_cached_media(
            chat_id=LOG_CHANNEL,
            file_id=fileid,
        )
        fileName = quote_plus(get_name(log_msg))
        if SHORTLINK == False:
            stream = f"{URL}watch/{str(log_msg.id)}/{fileName}?hash={get_hash(log_msg)}"
            download = f"{URL}{str(log_msg.id)}/{fileName}?hash={get_hash(log_msg)}"
        else:
            stream = await get_shortlink(f"{URL}watch/{str(log_msg.id)}/{fileName}?hash={get_hash(log_msg)}")
            download = await get_shortlink(f"{URL}{str(log_msg.id)}/{fileName}?hash={get_hash(log_msg)}")

        playit_url = f"playit://playerv2/video?url={download}"
        logger.info(f"Generated URLs - Stream: {stream}, Download: {download}, PlayIt: {playit_url}")

        await log_msg.reply_text(
            text=f"•• ʟɪɴᴋ ɢᴇɴᴇʀᴀᴛᴇᴅ ꜰᴏʀ ɪᴅ #{user_id} \n•• ᴜꜱᴇʀɴᴀᴍᴇ : {username} \n\n•• ᖴᎥᒪᗴ Nᗩᗰᗴ : {fileName}\n\n•• ᴘʟᴀʏ ɪɴ ᴘʟᴀʏɪᴛ : <a href='{playit_url}'>Play in PlayIt</a>",
            quote=True,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("🚀 Fast Download 🚀", url=download),
                    InlineKeyboardButton('🖥️ Watch online 🖥️', url=stream)
                ]
            ]),
            parse_mode=enums.ParseMode.HTML
        )
        rm = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("sᴛʀᴇᴀᴍ 🖥", url=stream),
                    InlineKeyboardButton("ᴅᴏᴡɴʟᴏᴀᴅ 📥", url=download)
                ]
            ]
        )
        msg_text = """<i><u>𝗬𝗼𝘂𝗿 𝗟𝗶𝗻𝗸 𝗚𝗲𝗻𝗲𝗿𝗮𝘁𝗲𝗱 !</u></i>\n\n<b>📂 Fɪʟᴇ ɴᴀᴍᴇ :</b> <i>{}</i>\n\n<b>📦 Fɪʟᴇ ꜱɪᴢᴇ :</b> <i>{}</i>\n\n<b>📥 Dᴏᴡɴʟᴏᴀᴅ :</b> <i>{}</i>\n\n<b> 🖥ᴡᴀᴛᴄʜ  :</b> <i>{}</i>\n\n<b> ▶️ ᴘʟᴀʏ ɪɴ ᴘʟᴀʏɪᴛ :</b> <i><a href='{}'>Play in PlayIt</a></i>\n\n<b>🚸 Nᴏᴛᴇ : ʟɪɴᴋ ᴡᴏɴ'ᴛ ᴇxᴘɪʀᴇ ᴛɪʟʟ ɪ ᴅᴇʟᴇᴛᴇ</b>"""

        await message.reply_text(
            text=msg_text.format(get_name(log_msg), humanbytes(get_media_file_size(message)), download, stream, playit_url),
            quote=True,
            disable_web_page_preview=True,
            reply_markup=rm,
            parse_mode=enums.ParseMode.HTML
        )
    except Exception as e:
        logger.error(f"Error in stream_start: {str(e)}")
        await message.reply_text(
            text="An error occurred while processing your file. Please try again later.",
            quote=True
        )
