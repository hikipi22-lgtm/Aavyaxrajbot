import asyncio
from pyrogram.types import InputMediaPhoto
from pytgcalls import PyTgCalls, types
from anony import app, db, logger, queue
from anony.helpers import buttons

class TgCall(PyTgCalls):
    # ... (init aur baki parts same rahenge)

    async def play_media(self, chat_id: int, media, message=None):
        client = await db.get_assistant(chat_id)
        stream = types.MediaStream(media_path=media.file_path)
        
        try:
            await client.play(chat_id, stream)
            if message:
                # 🕒 Timer Logic loop
                duration_sec = media.duration_sec
                played_sec = 0
                
                while played_sec < duration_sec:
                    # Timer aur Progress Bar format
                    percentage = int((played_sec / duration_sec) * 100)
                    bar = "🔘" + "─" * 15 # Static bar with current time
                    
                    text = (
                        f"**| Started streaming**\n\n"
                        f"**Title:** [{media.title}]({media.url})\n"
                        f"**Duration:** `{played_sec//60:02d}:{played_sec%60:02d} / {media.duration}`\n"
                        f"**Requested by:** {media.user}\n\n"
                        f"{bar}"
                    )
                    
                    try:
                        await message.edit_media(
                            media=InputMediaPhoto(media=media.thumb, caption=text),
                            reply_markup=buttons.controls(chat_id) # Buttons yahan se aayenge
                        )
                    except:
                        break # Agar message delete ho jaye toh loop rok do
                        
                    await asyncio.sleep(10) # Har 10 sec mein timer update hoga
                    played_sec += 10
                    
        except Exception as e:
            logger.error(f"Timer Error: {e}")
