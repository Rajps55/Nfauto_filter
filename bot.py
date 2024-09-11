import logging
import logging.config
import os
import asyncio
from pyrogram import Client, __version__
from pyrogram.raw.all import layer
from database.ia_filterdb import Media
from database.users_chats_db import db
from info import *
from utils import temp
from typing import Union, Optional, AsyncGenerator
from pyrogram import types
from aiohttp import web
from plugins import web_server
from lazybot import LazyPrincessBot
from util.keepalive import ping_server
from lazybot.clients import initialize_clients

# Logging configuration
logging.config.fileConfig('logging.conf')
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("imdbpy").setLevel(logging.ERROR)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logging.getLogger("aiohttp").setLevel(logging.ERROR)
logging.getLogger("aiohttp.web").setLevel(logging.ERROR)
logging.getLogger("pyrogram").setLevel(logging.WARNING)

PORT = "8000"

async def Lazy_start():
    print('\n')
    print('Initalizing Telegram Bot')
    
    if not os.path.isdir(DOWNLOAD_LOCATION):
        os.makedirs(DOWNLOAD_LOCATION)

    # Start the bot and ensure it's awaited
    await LazyPrincessBot.start()

    bot_info = await LazyPrincessBot.get_me()
    LazyPrincessBot.username = bot_info.username
    await initialize_clients()

    if ON_HEROKU:
        asyncio.create_task(ping_server())

    try:
        b_users, b_chats, lz_verified = await db.get_banned()
        temp.BANNED_USERS = b_users
        temp.BANNED_CHATS = b_chats
        temp.LAZY_VERIFIED_CHATS = lz_verified
    except Exception as e:
        logging.error(f"Error getting banned data: {e}")
        raise

    await Media.ensure_indexes()

    me = await LazyPrincessBot.get_me()
    temp.ME = me.id
    temp.U_NAME = me.username
    temp.B_NAME = me.first_name
    LazyPrincessBot.username = '@' + me.username

    app = web.AppRunner(await web_server())
    await app.setup()

    bind_address = "0.0.0.0" if ON_HEROKU else BIND_ADRESS
    await web.TCPSite(app, bind_address, PORT).start()

    logging.info(f"{me.first_name} with Pyrogram v{__version__} (Layer {layer}) started on {me.username}.")
    logging.info(LOG_STR)
    await idle()

if __name__ == '__main__':
    try:
        # Create a new event loop and set it as current
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Run the Lazy_start coroutine
        loop.run_until_complete(Lazy_start())
        logging.info('-----------------------🧐 Service running in Lazy Mode 😴-----------------------')
    except KeyboardInterrupt:
        logging.info('-----------------------😜 Service Stopped Sweetheart 😝-----------------------')
    except Exception as e:
        logging.error(f"Unhandled exception: {e}")
