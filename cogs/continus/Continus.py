import nextcord
from nextcord import *
from nextcord.ext import tasks, commands
from datetime import datetime
import datetime as datetime_failed
from oauth2client.service_account import ServiceAccountCredentials
from config import settings
import logging
import requests
import asyncio
import re
import locale
import aiohttp
from cogs.continus.Model_Continus import Model_Continus






# function add_guillemet --------------------------------------------------------------------
def add_guillemet(jackpot_str):
  
    if not isinstance(jackpot_str, str):
        jackpot_str = str(jackpot_str)

    indent = 3
    m = len(jackpot_str)//indent
    r = len(jackpot_str)%indent
    if r == 0:
        r = indent
        m -= 1
    jackpot_send = jackpot_str[:r]

    for x in range(m):
        jackpot_send = "".join(jackpot_send + "'")
        jackpot_send = jackpot_send + jackpot_str[r+x*indent:r+x*indent+indent]

    #print("ajout des guillets")
    return jackpot_send


# change allowed_role setting --------------------------------------------------------------------------------------------
async def change_allowed_role_setting(event_id: str, allowed_role : list[str]):
    url = f"https://raid-helper.dev/api/v2/events/{event_id}"

    headers = {
        "Authorization": settings.api_key_raid_helper,
        "Content-Type": "application/json"
    }

    allowed_roles_str = ",".join(allowed_role) + ","

    payload = {
        "advancedSettings": {
            "allowed_roles": allowed_roles_str
        }
    }
    #print(headers)
    #print(payload)

    async with aiohttp.ClientSession() as session:
        async with session.patch(url, json=payload, headers=headers) as resp:
            if resp.status != 200:
                
                text = await resp.text()
                raise Exception(f"Raid-Helper error {resp.status}: {text}")
            

            return await resp.json()

# change allowed_role setting --------------------------------------------------------------------------------------------
async def show_allowed_role(event_id: str):
    url = f"https://raid-helper.dev/api/v2/events/{event_id}"
    headers = {"Authorization": f"{settings.api_key_raid_helper}"}

    response = requests.get(url, headers=headers)

    #print("Status code:", response.status_code)
    if response.status_code != 200:
        print("Error:", response.text)
    else:
        data = response.json()
        #print("Full event data:", data)  # see everything returned
        setting = data.get("advancedSettings", {}).get("allowed_roles", None)
        if setting:
            print("settings:", setting)
        else:
            print("No advanced_settings found for this event")
        

async def get_customid(event_id: str):
    url = f"https://raid-helper.dev/api/v2/events/{event_id}"
    headers = {"Authorization": f"{settings.api_key_raid_helper}"}

    response = requests.get(url, headers=headers)

    #print("Status code:", response.status_code)
    if response.status_code != 200:
        print("Error:", response.text)
    else:
        data = response.json()
        #print("Full event data:", data)  # see everything returned
        customId = data.get("templateId")
    return customId



# function schedule_event --------------------------------------------------------------------
async def schedule_event(bot, chan) :
    
    server_id = settings.guild
    api_key = settings.api_key_raid_helper
    chan_raid = bot.get_channel(chan)
    guild = chan_raid.guild
    calendrier = settings.id_calendar_emote #calendrier emote
    groupe = settings.id_groupe_emote #groupe emote
    embed = None
    locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')  # Linux / macOS

    url = f"https://raid-helper.dev/api/v2/servers/{server_id}/events"
    headers = {
        "Authorization": api_key
    }

    # Envoyer une requête GET à l'API
    response = requests.get(url, headers=headers)
       


    # Vérifier si la requête a réussi
    if response.status_code == 200:
        # Charger la réponse JSON
        data = response.json()

        # Filtrer les événements pour ne conserver que ceux dans le channel #annonce-raid
        events = [event for event in data['postedEvents'] if int(event['channelId']) == chan_raid.id]

        # Tri des événements par date
        events = sorted(events, key=lambda event: event['startTime'])

        # Création d'un dictionnaire pour stocker les événements par jour
        events_by_day = {}

        # Parcourir la liste des événements filtrés
        for event in events:
            start_time = event['startTime']
            event_date = datetime.fromtimestamp(start_time).strftime('%A %d %B')
            event_hour = datetime.fromtimestamp(start_time).strftime('%H:%M')
            event_signup = event['signUpsAmount']
            event_title = event['title']


            event_url = f"https://discord.com/channels/{server_id}/{event['channelId']}/{event['id']}"

            # Si la date de début de l'événement n'est pas déjà présente dans le dictionnaire, l'ajouter avec une liste vide comme valeur
            if event_date not in events_by_day:
                events_by_day[event_date] = []

            # Ajouter l'événement à la liste des événements pour la date de début correspondante
            events_by_day[event_date].append(f"> `{event_hour}`  {groupe}  `{event_signup}` **[{event_title}]({event_url})** <t:{start_time}:R>")

        # Création de l'embed Discord
        embed = Embed(title="Liste des Events :", color=Color.teal())       

        # Parcourir le dictionnaire des événements par jour et ajouter un champ à l'embed pour chaque jour avec la liste des événements pour ce jour
        for event_date, event_list in events_by_day.items():
            # Joindre les événements pour ce jour en les séparant par des sauts de ligne
            events_str = "\n".join(event_list)
            # Ajouter le champ à l'embed avec la date de début comme nom et la liste des événements pour ce jour comme valeur
            embed.add_field(name=f"{calendrier}  {event_date}", value=events_str, inline=False)
            

        if len(events) == 0 :
            embed.add_field(name="Il n'y a pas d'Event actuellement", value="\n", inline=False)

        # Ajouter le dernier champ avec des informations supplémentaires
        embed.add_field(name="", value=f"Les infos sont actualisées toutes les {settings.time_loop_ctr} minutes.")
        
        #enleve le role RP de allowed role
        if len(events) != 0 and False : #remove False to activate the RP role management ------------------------------------------------------------:
            for field in embed.fields[:-1]:
                field_value = field.value
                event_id = re.search(r"/(\d+)\)\*", field_value).group(1)
                timestamp_start_raid = int(re.search(r"<t:(\d+):R>", field_value).group(1))
                message_timestamp = ((int(event_id) >> 22) + 1420070400000) // 1000
                now_timestamp  = int(datetime.now().timestamp())
                #print(f"dif entre now et msg => {now_timestamp-message_timestamp}")
                #print(f"dif entre raid et now => {timestamp_start_raid-now_timestamp}")
                
                customId = await get_customid(str(event_id))
                #print(f"event id : {event_id}")
                #print(f"customId : {customId}")
                TWENTY_FOUR_HOURS = 60*60*24
                time_until_raid = timestamp_start_raid - now_timestamp
                time_since_message = now_timestamp - message_timestamp
                
                if customId in settings.customid_10_man :
                    
                    if time_until_raid < TWENTY_FOUR_HOURS :
                        #print(f"remove RP for allowed_role on {event_id}")
                        await change_allowed_role_setting(str(event_id), [""]) #remove the allowed role restriction
                    elif time_since_message < TWENTY_FOUR_HOURS :   #moins de 24h entre le debut du raid ou apres le raid créer.
                        #print(f"add RP for allowed_role on {event_id}")
                        #await show_allowed_role(str(event_id))
                        await change_allowed_role_setting(str(event_id),[str(settings.ROLE_rp)]) #add the RP role restriction
                        #await show_allowed_role(str(event_id))
                    else:
                        #print(f"remove RP for allowed_role on {event_id}")
                        await change_allowed_role_setting(str(event_id), [""]) #remove the allowed role restriction

                    
           
    




            """ 
            print(f"the start of the raid : {timestamp_start_raid}")
            print(f"now : {now_timestamp}")
        
            print(datetime.fromtimestamp(message_timestamp).strftime('%A %d %B %H %M')) """
        
        
    else:
        try:
            # Try to parse JSON error message
            error = response.json()
            logging.info(f"Echec de la requête à l'API Raid Helper : {error}")
        except ValueError:
            # Fallback if response is plain text
            logging.info(f"Echec de la requête à l'API Raid Helper : {response.text}")
        
    

    return embed


async def event_summary(bot):
    # function event summary --------------------------------------------------------------------

    server_id = settings.guild
    channel_ids = [settings.channel_event_raid_helper_fs, 
                   settings.channel_event_raid_helper_lym, 
                   settings.channel_event_raid_helper_bw, 
                   settings.channel_event_raid_helper_ml, 
                   settings.channel_event_raid_helper_tf]
    api_key = settings.api_key_raid_helper
    calendrier = settings.id_calendar_emote #calendrier emote
    groupe = settings.id_groupe_emote #groupe emote
    embed = None
    locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')  # Linux / macOS

    url = f"https://raid-helper.dev/api/v2/servers/{server_id}/events"
    headers = {
        "Authorization": api_key
    }

    # Envoyer une requête GET à l'API
    response = requests.get(url, headers=headers)
       


    # Vérifier si la requête a réussi
    if response.status_code == 200:
        # Charger la réponse JSON
        data = response.json()

        # Filtrer les événements pour ne conserver que ceux dans les channels spécifiés
        events = [event for event in data['postedEvents'] if int(event['channelId']) in channel_ids]

        # Tri des événements par date
        events = sorted(events, key=lambda event: event['startTime'])

        # Création d'un dictionnaire pour stocker les événements par jour
        events_by_day = {}

        # Parcourir la liste des événements filtrés
        for event in events:
            start_time = event['startTime']
            event_date = datetime.fromtimestamp(start_time).strftime('%A %d %B')
            event_hour = datetime.fromtimestamp(start_time).strftime('%H:%M')
            event_signup = event['signUpsAmount']
            event_title = event['title']

            if event['channelId'] == str(settings.channel_event_raid_helper_fs) :
                groupe = "<:FS:1284679570079092776>"
            elif event['channelId'] == str(settings.channel_event_raid_helper_lym) :
                groupe = "<:LYM:1284679574487306312>"
            elif event['channelId'] == str(settings.channel_event_raid_helper_bw) :
                groupe = "<:BW:1284679576097919067>"
            elif event['channelId'] == str(settings.channel_event_raid_helper_ml) :
                groupe = "<:ML:1284679571374997524>"
            elif event['channelId'] == str(settings.channel_event_raid_helper_tf) :
                groupe = "<:TF:1284679572906049627>"
            else :
                groupe = ":no_entry:"


            event_url = f"https://discord.com/channels/{server_id}/{event['channelId']}/{event['id']}"

            # Si la date de début de l'événement n'est pas déjà présente dans le dictionnaire, l'ajouter avec une liste vide comme valeur
            if event_date not in events_by_day:
                events_by_day[event_date] = []

            # Ajouter l'événement à la liste des événements pour la date de début correspondante
            events_by_day[event_date].append(f"> `{event_hour}`  {groupe}  `{event_signup}` **[{event_title}]({event_url})** <t:{start_time}:R>")

        # Création de l'embed Discord
        embed = Embed(title="Liste des Events :", color=Color.teal())       

        # Parcourir le dictionnaire des événements par jour et ajouter un champ à l'embed pour chaque jour avec la liste des événements pour ce jour
        for event_date, event_list in events_by_day.items():
            # Joindre les événements pour ce jour en les séparant par des sauts de ligne
            events_str = "\n".join(event_list)
            # Ajouter le champ à l'embed avec la date de début comme nom et la liste des événements pour ce jour comme valeur
            embed.add_field(name=f"{calendrier}  {event_date}", value=events_str, inline=False)
            

        if len(events) == 0 :
            embed.add_field(name="Il n'y a pas d'Event actuellement", value="\n", inline=False)

        # Ajouter le dernier champ avec des informations supplémentaires
        embed.add_field(name="", value=f"Les infos sont actualisées toutes les {settings.time_loop_ctr} minutes.")

    else:
        try:
            # Try to parse JSON error message
            error = response.json()
            logging.info(f"Echec de la requête à l'API Raid Helper : {error}")
        except ValueError:
            # Fallback if response is plain text
            logging.info(f"Echec de la requête à l'API Raid Helper : {response.text}")

    return embed
    

# function affichage_event --------------------------------------------------------------------
async def show_ctr(bot, channel_id):
    bot_id = int(settings.application_id)
    chan_event = bot.get_channel(channel_id)
    if chan_event is None:
        return

    embed = await schedule_event(bot, channel_id)
    if embed is not  None:
        bot_message_id = None
        messages = [msg async for msg in chan_event.history(limit=None)]

        for index, message in enumerate(messages):
            if message.author.id == bot_id:
                bot_message_id = message.id
                break

        #print(f"index : {index}")

        if bot_message_id == None :
            await chan_event.send(embed=embed)
            #print(f"send embed message in {chan_event.name}")
        elif index != 0:
            await messages[index].delete()
            await chan_event.send(embed=embed)
            #print(f"delete and send embed message in {chan_event.name}")
        else:
            try:
                #print(f"edit embed message in {chan_event.name}")
                await message.edit(embed=embed)
            except nextcord.errors.DiscordServerError as e:
                logging.info(f"Discord API Error : {e}. Retrying in 5 seconds...")
                await asyncio.sleep(5)
                await message.edit(embed=embed)

# function affichage_event --------------------------------------------------------------------
async def show_summary(bot):
    bot_id = int(settings.application_id)
    channel_id = settings.channel_event_summary
    chan_event = bot.get_channel(channel_id)
    if chan_event is None:
        return

    embed = await event_summary(bot)
    if embed is not  None:
        bot_message_id = None
        messages = [msg async for msg in chan_event.history(limit=None)]

        for index, message in enumerate(messages):
            if message.author.id == bot_id:
                bot_message_id = message.id
                break

        #print(f"index : {index}")

        if bot_message_id == None :
            await chan_event.send(embed=embed)
            #print(f"send embed message in {chan_event.name}")
        elif index != 0:
            await messages[index].delete()
            await chan_event.send(embed=embed)
            #print(f"delete and send embed message in {chan_event.name}")
        else:
            try:
                #print(f"edit embed message in {chan_event.name}")
                await message.edit(embed=embed)
            except nextcord.errors.DiscordServerError as e:
                logging.info(f"Discord API Error : {e}. Retrying in 5 seconds...")
                await asyncio.sleep(5)
                await message.edit(embed=embed)



#class Continus --------------------------------------------------------------------
class Continus(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.update_raid_helper.start()

    def cog_unload(self):
        self.update_raid_helper.cancel()


    @commands.Cog.listener()
    async def on_ready(self):
        print("Continus.py is ready!")


  

    # Raid helper schedule
    @tasks.loop(minutes=settings.time_loop_ctr)
    async def update_raid_helper(self):
        try:
            #logging.info("---------- START EMBED RAID HELPER LOOP ----------")
            logging.info("---------- UPDATE CTR FS ----------")
            await show_ctr(self.bot, settings.channel_event_raid_helper_fs)
            logging.info("---------- UPDATE CTR LYM ----------")
            await show_ctr(self.bot, settings.channel_event_raid_helper_lym)
            logging.info("---------- UPDATE CTR BW ----------")
            await show_ctr(self.bot, settings.channel_event_raid_helper_bw)
            logging.info("---------- UPDATE CTR ML ----------")
            await show_ctr(self.bot, settings.channel_event_raid_helper_ml)
            logging.info("---------- UPDATE CTR TF ----------")
            await show_ctr(self.bot, settings.channel_event_raid_helper_tf)
            logging.info("---------- UPADTE SUMMARY ---------")
            await show_summary(self.bot)
            logging.info("---------- END   EMBED RAID HELPER LOOP ----------")
            
        
        except Exception as e:
            logging.info(f"Error in update:raid:helper loop : {e}")

        


    @update_raid_helper.before_loop
    async def before_boucle(self):
        await self.bot.wait_until_ready()


          




def setup(bot):
  bot.add_cog(Continus(bot))



