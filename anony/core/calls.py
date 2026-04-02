import asyncio
from pyrogram.types import InputMediaPhoto, InlineKeyboardButton, InlineKeyboardMarkup
from pytgcalls import PyTgCalls, types
from pytgcalls.pytgcalls_session import PyTgCallsSession
from anony import app, db, logger, userbot

class TgCall(PyTgCalls):
    def __init__(self):
        self.clients = []

    async def play_media(self, chat_id: int, media, message=None):
        client = await db.get_assistant(chat_id)
        stream = types.MediaStream(
            media_path=media.file_path,
            audio_parameters=types.AudioQuality.HIGH,
            video_parameters=types.VideoQuality.HD_720p,
        )
        
        # UI Buttons
        btns = InlineKeyboardMarkup([[
            InlineKeyboardButton("⏸", callback_data=f"pause_{chat_id}"),
            InlineKeyboardButton("▶️", callback_data=f"resume_{chat_id}"),
            InlineKeyboardButton("⏭", callback_data=f"skip_{chat_id}"),
        ]])

        try:
            await client.play(chat_id, stream)
            if message:
                duration_sec = media.duration_sec
                played = 0
                while played < duration_sec:
                    # 🕒 Timer calculation
                    p_min, p_sec = divmod(played, 60)
                    
                    # 📊 Progress Bar Logic
                    bar_fill = int((played / duration_sec) * 15)
                    bar = "🔘" + "─" * bar_fill + "─" * (15 - bar_fill)
                    
                    text = (
                        f"**| Started streaming**\n\n"
                        f"**Title:** [{media.title}]({media.url})\n\n"
                        f"**Duration:** `{p_min:02d}:{p_sec:02d} / {media.duration}`\n"
                        f"**Requested by:** {media.user}\n\n"
                        f"{bar}"
                    )
                    try:
                        await message.edit_media(
                            media=InputMediaPhoto(media=media.thumb, caption=text),
                            reply_markup=btns
                        )
                    except:
                        break # Stop loop if message deleted
                    
                    await asyncio.sleep(10) # 10 sec update interval
                    played += 10
        except Exception as e:
            logger.error(f"Streaming Error: {e}")

    async def boot(self) -> None:
        PyTgCallsSession.notice_displayed = True
        for ub in userbot.clients:
            client = PyTgCalls(ub)
            await client.start()
            self.clients.append(client)
        logger.info("Bot started with Original UI & Timer!")
