from pyrogram.types import InputMediaPhoto
from pytgcalls import PyTgCalls, exceptions, types
from anony import app, db, logger, queue, userbot, yt
from anony.helpers import buttons

# Premium UI Image
IMG = "https://telegra.ph/file/af55d7879948408f65792.jpg"

class TgCall(PyTgCalls):
    def __init__(self):
        self.clients = []

    async def play_media(self, chat_id: int, media, message=None):
        client = await db.get_assistant(chat_id)
        stream = types.MediaStream(
            media_path=media.file_path,
            audio_parameters=types.AudioQuality.HIGH,
            video_parameters=types.VideoQuality.HD_720p,
            video_flags=types.MediaStream.Flags.AUTO_DETECT if media.video else types.MediaStream.Flags.IGNORE,
        )
        try:
            await client.play(chat_id, stream)
            await db.add_call(chat_id)
            
            if message:
                # 🔥 YEH HAI TUMHARA MANGTA HUA UI
                text = (
                    f"✨ **ɴᴏᴡ ᴘʟᴀʏɪɴɢ ᴏɴ ᴠᴏɪᴄᴇᴄʜᴀᴛ** ✨\n\n"
                    f"🎵 **ᴛɪᴛʟᴇ:** `{media.title}`\n"
                    f"👤 **ʀᴇǫᴜᴇsᴛᴇᴅ ʙʏ:** {media.user}\n\n"
                    f"⏳ **sᴛᴀᴛᴜs:** `sᴛʀᴇᴀᴍɪɴɢ ʟɪᴠᴇ` 📡\n"
                    f"───────────────\n"
                    f"▶️ 🔘──────────────── 05:00\n\n"
                    f"🛡️ **ᴅᴇᴠᴇʟᴏᴘᴇᴅ ʙʏ:** @aavyabots"
                )
                try:
                    # Purana 'Downloading...' hatakar photo wala UI layega
                    await message.edit_media(
                        media=InputMediaPhoto(media=IMG, caption=text),
                        reply_markup=buttons.controls(chat_id)
                    )
                except Exception as e:
                    logger.error(f"UI Update Error: {e}")
        except Exception as e:
            logger.error(f"Play Error: {e}")
            await self.play_next(chat_id)

    async def play_next(self, chat_id: int):
        media = queue.get_next(chat_id)
        if not media:
            if await db.is_autoplay_mode(chat_id):
                media = await yt.get_next_autoplay_video(chat_id)
                if not media: return await self.stop(chat_id)
            else: return await self.stop(chat_id)

        link = await yt.get_stream_link(media.id)
        if not link: return await self.play_next(chat_id)
        
        media.file_path = link
        msg = await app.send_message(chat_id, "🔄 **ꜰᴇᴛᴄʜɪɴɢ ɴᴇxᴛ ᴛʀᴀᴄᴋ...**")
        await self.play_media(chat_id, media, msg)
