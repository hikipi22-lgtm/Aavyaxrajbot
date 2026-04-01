# Copyright (c) 2025 AnonymousX1025
# Licensed under the MIT License.
# This file is part of AnonXMusic

from pathlib import Path
from pyrogram import filters, types
from pyrogram.types import InputMediaPhoto # Naya import UI ke liye

from anony import anon, app, config, db, lang, queue, tg, yt
from anony.helpers import buttons, utils
from anony.helpers._play import checkUB

# ✨ PREMIUM UI SETTINGS
IMG = "https://telegra.ph/file/af55d7879948408f65792.jpg"
DEV = "@aavyabots" # Tera credit yahan hai

def playlist_to_queue(chat_id: int, tracks: list) -> str:
    text = "<blockquote expandable>"
    for track in tracks:
        pos = queue.add(chat_id, track)
        text += f"<b>{pos}.</b> {track.title}\n"
    text = text[:1948] + "</blockquote>"
    return text

@app.on_message(
    filters.command(["play", "playforce", "vplay", "vplayforce"])
    & filters.group
    & ~app.bl_users
)
@lang.language()
@checkUB
async def play_hndlr(
    _,
    m: types.Message,
    force: bool = False,
    m3u8: bool = False,
    video: bool = False,
    url: str = None,
) -> None:
    # 🖼️ SEARCHING UI START
    sent = await m.reply_photo(
        photo=IMG,
        caption=f"✨ **sᴇᴀʀᴄʜɪɴɢ ʏᴏᴜʀ sᴏɴɢ...**\n\n🛡️ **ᴘᴏᴡᴇʀᴇᴅ ʙʏ:** {DEV}"
    )
    
    file = None
    mention = m.from_user.mention
    media = tg.get_media(m.reply_to_message) if m.reply_to_message else None
    tracks = []

    if media:
        setattr(sent, "lang", m.lang)
        file = await tg.download(m.reply_to_message, sent)

    elif m3u8:
        file = await tg.process_m3u8(url, sent.id, video)

    elif url:
        if "playlist" in url:
            await sent.edit_caption(f"✨ **ꜰᴇᴛᴄʜɪɴɢ ᴘʟᴀʏʟɪsᴛ...**\n🛡️ **ᴘᴏᴡᴇʀᴇᴅ ʙʏ:** {DEV}")
            tracks = await yt.playlist(config.PLAYLIST_LIMIT, mention, url, video)
            if not tracks:
                return await sent.edit_caption("❌ **ᴘʟᴀʏʟɪsᴛ ɴᴏᴛ ꜰᴏᴜɴᴅ ᴏʀ ᴇʀʀᴏʀ!**")
            file = tracks[0]
            tracks.remove(file)
            file.message_id = sent.id
        else:
            file = await yt.search(url, sent.id, video=video)

    elif len(m.command) >= 2:
        query = " ".join(m.command[1:])
        file = await yt.search(query, sent.id, video=video)

    if not file:
        return await sent.edit_caption(f"❌ **sᴏɴɢ ɴᴏᴛ ꜰᴏᴜɴᴅ!**\n\n💬 **ᴛʀʏ ᴀɢᴀɪɴ ᴡɪᴛʜ ᴄᴏʀʀᴇᴄᴛ ɴᴀᴍᴇ.**\n🛡️ **ᴘᴏᴡᴇʀᴇᴅ ʙʏ:** {DEV}")

    if file.duration_sec > config.DURATION_LIMIT:
        return await sent.edit_caption(f"⚠️ **ᴅᴜʀᴀᴛɪᴏɴ ʟɪᴍɪᴛ ᴇxᴄᴇᴇᴅᴇᴅ!**\n\n🕒 **ᴍᴀx ᴀʟʟᴏᴡᴇᴅ:** `{config.DURATION_LIMIT // 60} ᴍɪɴs`")

    file.user = mention
    if force:
        queue.force_add(m.chat.id, file)
    else:
        position = queue.add(m.chat.id, file)
        if position != 0 or await db.get_call(m.chat.id):
            # 📝 QUEUED UI
            cap = (
                f"📝 **ᴀᴅᴅᴇᴅ ᴛᴏ ǫᴜᴇᴜᴇ ᴀᴛ #{position}**\n\n"
                f"🎵 **ᴛɪᴛʟᴇ:** [{file.title}]({file.url})\n"
                f"👤 **ʙʏ:** {mention}\n"
                f"🕒 **ᴅᴜʀᴀᴛɪᴏɴ:** `{file.duration}`\n\n"
                f"🛡️ **ᴘᴏᴡᴇʀᴇᴅ ʙʏ:** {DEV}"
            )
            await sent.edit_caption(
                caption=cap,
                reply_markup=buttons.play_queued(m.chat.id, file.id, m.lang["play_now"])
            )
            return

    # 📥 DOWNLOADING UI
    if not file.file_path:
        fname = f"downloads/{file.id}.{'mp4' if video else 'webm'}"
        if Path(fname).exists():
            file.file_path = fname
        else:
            await sent.edit_caption(f"📥 **ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ ꜰʀᴏᴍ ʏᴏᴜᴛᴜʙᴇ...**\n\n▶️ 🔘──────────────── 05:00\n🛡️ **ᴘᴏᴡᴇʀᴇᴅ ʙʏ:** {DEV}")
            file.file_path = await yt.download(file.id, video=video)

    # 🚀 FINAL PLAY
    await anon.play_media(chat_id=m.chat.id, message=sent, media=file)
    
    if tracks:
        added = playlist_to_queue(m.chat.id, tracks)
        await app.send_message(
            chat_id=m.chat.id,
            text=f"✅ **{len(tracks)} ᴛʀᴀᴄᴋs ᴀᴅᴅᴇᴅ ᴛᴏ ǫᴜᴇᴜᴇ!**\n" + added,
        )
