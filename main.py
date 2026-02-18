import nextcord
from nextcord.ext import commands
import logging
import re
from datetime import datetime

import aiohttp
from config import settings


FORMAT = "%(asctime)s: %(message)s"
logging.basicConfig(level=logging.INFO, format=FORMAT, datefmt="%Y-%m-%d / %H:%M:%S")

print("Starting bot...")
print(f"Environment: {settings.ENV_FOR_DYNACONF}")
  


# Configure intents explicitly
intents = nextcord.Intents.default()
intents.members = True  # Explicitly enable member intent
intents.messages = True  # Ensure message intent is enabled as well (optional)



bot = commands.Bot(
  command_prefix=settings.command_prefix,
  intents=intents,
  application_id=settings.application_id
  #guilds=[settings.guild]
)


if settings.ENV_FOR_DYNACONF == "DEVELOPMENT":  
  initial_extensions = [
  "cogs.continus.Continus",
  "cogs.raid_helper.Raid_helper",
  "cogs.ticket.Ticket",
  "cogs.info.Info"
  ]
elif settings.ENV_FOR_DYNACONF == "production":
  initial_extensions = [
  "cogs.continus.Continus",
  "cogs.raid_helper.Raid_helper",
  "cogs.ticket.Ticket",
  "cogs.info.Info"
  ]
else: print("error de dynaconf")


async def signup_user(event_id: str, user_id: int, class_name: str):
    url = f"https://raid-helper.dev/api/v2/events/{event_id}/signups"

    headers = {
        "Authorization": settings.api_key_raid_helper,
        "Content-Type": "application/json"
    }

    payload = {
        "userId": str(user_id),
        "className": class_name
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as resp:
            if resp.status not in (200, 201):
                text = await resp.text()
                raise Exception(f"Raid-Helper error {resp.status}: {text}")

            return await resp.json()

async def remove_signup_user(event_id: str, user_id: int):
    url = f"https://raid-helper.dev/api/v2/events/{event_id}/signups/{user_id}"

    headers = {
        "Authorization": settings.api_key_raid_helper,
        "Content-Type": "application/json"
    }

    async with aiohttp.ClientSession() as session:
        async with session.delete(url, headers=headers) as resp:
            if resp.status not in (200, 204):
                text = await resp.text()
                raise Exception(f"Raid-Helper error {resp.status}: {text}")

            # souvent vide en DELETE, mais on reste safe
            return await resp.text()


def get_guild_role():
    guild = bot.get_guild(settings.guild)
    for role in guild.roles:
        print(f"{role.name} / {role.id}")



@bot.event
async def on_ready():
  print(f"Database is : {settings.database}")
  print("Success: Bot is connected to Discord")
  


  #get_guild_role()






if __name__ == '__main__':
  for extension in initial_extensions:
    bot.load_extension(extension)


bot.run(settings.discord_api_key, reconnect=True)