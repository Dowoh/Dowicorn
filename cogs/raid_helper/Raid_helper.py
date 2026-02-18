import nextcord
from nextcord import *
from nextcord.ext import commands
from config import settings
import requests
import random
import asyncio
from cogs.raid_helper.Model_Raid_helper import Model_Raid_helper


#class Raid_helper --------------------------------------------------------------------
class Raid_helper(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        Model_Raid_helper.create_table()


    @commands.Cog.listener()
    async def on_ready(self):
        print("Raid_helper.py is ready!")

    @message_command(name="Compare Sign-ups")
    async def my_context_menu(self, 
                              interaction: nextcord.Interaction, 
                              discord_msg_link: nextcord.Message):
        
        # Defer the interaction response
        await interaction.response.defer(ephemeral=True)#ephemeral=True)

        # Get the guild (server) from the interaction
        guild = interaction.guild



        # Split the message link to get IDs
        parts = discord_msg_link.jump_url.split('/')
        guild_id = int(parts[4])    # Guild (Server) ID
        channel_id = int(parts[5])  # Channel ID
        message_id = int(parts[6])  # Message ID

        url = f"https://raid-helper.dev/api/v2/events/{message_id}"
        headers = {
            "Authorization": settings.api_key_raid_helper
        }

        signup_list = []

        # Envoyer une requête GET à l'API
        response = requests.get(url, headers=headers)
       

        # Vérifier si la requête a réussi
        if response.status_code == 200:
            # Charger la réponse JSON
            data = response.json()
            

            for signup_member in data["signUps"]:
                #print(f"id user discord {signup_member['position']} : {signup_member['userId']}")
                if signup_member["className"] != "Absence":
                    signup_list.append(signup_member['userId'])
        else:
            logging.info("Echec de la requête à l'API Raid Helper")


        
        embeds=[]
        # Loop through all voice channels in the guild
        for voice_channel in guild.voice_channels:
            empty_all_chan = True
            embed_msg = Embed(title=f"Vocal : {voice_channel.name}", color=Color(random.randint(0, 0xFFFFFF)))
            embed_value_signup = []
            embed_value_notsignup = []
            # For each voice channel, loop through the connected members
            for member in voice_channel.members:
                empty_all_chan = False
                sign_up_flag = False
                for memberid in signup_list:
                    if int(memberid) == member.id:
                        sign_up_flag = True



                if sign_up_flag:
                    embed_value_signup.append(f"{member.display_name}")
                    embed_value_signup.append(f"`<@{member.id}>`")
                    signup_list.remove(str(member.id))
                else:
                    embed_value_notsignup.append(f"{member.display_name}")
                    embed_value_notsignup.append(f"`<@{member.id}>`")
                       

            if not empty_all_chan:
                embed_value_signup = '\n'.join(embed_value_signup)
                embed_value_notsignup = '\n'.join(embed_value_notsignup)

                embed_msg.add_field(name=f"In {voice_channel.name}, not sign up:", value=embed_value_notsignup, inline=True)
                embed_msg.add_field(name=f"In {voice_channel.name}, signed up:", value=embed_value_signup, inline=True)
                embeds.append(embed_msg)

        

        not_signup_embed_value = []
        not_signup_embed = Embed(color=Color(random.randint(0, 0xFFFFFF)))
        for memberid in signup_list:
            member = guild.get_member(int(memberid))
            not_signup_embed_value.append(f"{member.display_name}")
            not_signup_embed_value.append(f"`<@{member.id}>`")
        not_signup_embed_value = '\n'.join(not_signup_embed_value)
        not_signup_embed.add_field(name=f"Introuvable sur le discord", value=not_signup_embed_value, inline=True)
        embeds.append(not_signup_embed)
            

            

        await interaction.followup.send(embeds=embeds, ephemeral=True)





    @slash_command(name="compare_signup", description="Compare entre les signups de l'event et ceux en coms")
    async def compare_signup(self, 
                             interaction: Interaction,
                             discord_msg_link : str = SlashOption(description="Met le lien du message de l'event que tu veux comparer", required=True)
    ):
        # Defer the interaction response
        await interaction.response.defer(ephemeral=True)#ephemeral=True)

        # Get the guild (server) from the interaction
        guild = interaction.guild



        # Split the message link to get IDs
        parts = discord_msg_link.split('/')
        guild_id = int(parts[4])    # Guild (Server) ID
        channel_id = int(parts[5])  # Channel ID
        message_id = int(parts[6])  # Message ID

        url = f"https://raid-helper.dev/api/v2/events/{message_id}"
        headers = {
            "Authorization": settings.api_key_raid_helper
        }

        signup_list = []

        # Envoyer une requête GET à l'API
        response = requests.get(url, headers=headers)
       

        # Vérifier si la requête a réussi
        if response.status_code == 200:
            # Charger la réponse JSON
            data = response.json()
            

            for signup_member in data["signUps"]:
                #print(f"id user discord {signup_member['position']} : {signup_member['userId']}")
                signup_list.append(signup_member['userId'])
        else:
            logging.info("Echec de la requête à l'API Raid Helper")



        

        
        
        embeds=[]
        # Loop through all voice channels in the guild
        for voice_channel in guild.voice_channels:
            empty_chan = True
            embed_msg = Embed(title=f"Vocal : {voice_channel.name}", color=Color(random.randint(0, 0xFFFFFF)))
            embed_value_signup = []
            embed_value_notsignup = []
            # For each voice channel, loop through the connected members
            for member in voice_channel.members:
                empty_chan = False
                sign_up_flag = False
                for memberid in signup_list:
                    if int(memberid) == member.id:
                        sign_up_flag = True



                if sign_up_flag:
                    embed_value_signup.append(f"{member.display_name}")
                    embed_value_signup.append(f"`<@{member.id}>`")
                else:
                    embed_value_notsignup.append(f"{member.display_name}")
                    embed_value_notsignup.append(f"`<@{member.id}>`")
                       

            if not empty_chan:
                embed_value_signup = '\n'.join(embed_value_signup)
                embed_value_notsignup = '\n'.join(embed_value_notsignup)

                embed_msg.add_field(name=f"In {voice_channel.name}, not sign up:", value=embed_value_notsignup, inline=True)
                embed_msg.add_field(name=f"In {voice_channel.name}, signed up:", value=embed_value_signup, inline=True)
                embeds.append(embed_msg)

        await interaction.followup.send(embeds=embeds, ephemeral=True)
        


    @slash_command(name="move_all", description="Move tous les joueurs de ton channel dans celui séléctionné")
    async def move_all_user_into_another_channel(self, 
    interaction: Interaction,
    voice_channel: VoiceChannel = SlashOption(
            description="Séléctionner le channel vocal dans lequel vous voullez déplacer tout le monde.",
            channel_types=[ChannelType.voice],
            required=True
        ),
    ):
        try:
            await interaction.response.defer(ephemeral=True)
        except nextcord.errors.NotFound:
            # L'interaction a expiré, on ne peut rien faire
            return


        if interaction.user.voice is None:
            await interaction.followup.send(f"Vous devez être dans un channel vocal pour utiliser cette commande")
            return
        
        start_channel = interaction.user.voice.channel
        if voice_channel == start_channel:
            await interaction.followup.send(f"Vous devez sélectionné un channel différent du votre !")
            return
        
        number = 0
        guild = interaction.guild
        a_verifier_role = guild.get_role(settings.ROLE_premier_raid)
        new_raider_role = guild.get_role(settings.ROLE_premier_raid)
        raider_channel = guild.get_channel(settings.channel_new_raider)
        msg_content = f"Tout le monde a bién été déplacé ! \n Commande faites par : {interaction.user.display_name}\n"
        embed = Embed(title="Liste des new raider", color=Color.orange()) 
        for member in start_channel.members:
            if new_raider_role:
                try:
                    if new_raider_role in member.roles:
                        await member.remove_roles(new_raider_role, reason="Fin du statut raider")
                        embed.add_field(name="",value=f"{member.display_name} / {member.mention} / {member.id}",inline=False)

                    await member.move_to(voice_channel)
                    number += 1
                    if number%10 == 0:
                        await asyncio.sleep(5)
                except Exception as e:
                    await interaction.followup.send(f"Une erreur est survenue lors du déplacement des membres. Erreur: {e}")
                    return 
            

        if not embed.fields:
            embed = Embed(title="Aucun new raider dans ce raid", color=Color.red())
            

        await interaction.followup.send("Vous avez bien déplacé tout le monde avec succès !",ephemeral=True)

        await raider_channel.send(content=msg_content, embed=embed)

        



    @slash_command(name="info_player", description="Donne les infos du joueurs")
    async def info_player(self,
    interaction: Interaction,
    name: str = SlashOption(description="Met le nom du joueur que tu veux vérifier", required=True)
    ):
        await interaction.response.defer()

        url_ID = f"https://gameinfo-ams.albiononline.com/api/gameinfo/search?q={name}"
        info_player = "" # value de l'embed par default

        try:
            # Effectuer la requête GET
            response = requests.get(url_ID)
            data = response.json()  # Convertir la réponse en JSON

           

            # Si un joueur est trouvé
            if data['players']:
                joueur_Id = data['players'][0]['Id']  # Prenons le premier joueur trouvé

             
                url_player = f"https://gameinfo-ams.albiononline.com/api/gameinfo/players/{joueur_Id}"

                # Effectuer la requête GET
                response_2 = requests.get(url_player)
                data_2 = response_2.json()  # Convertir la réponse en JSON                


                nom = data_2['Name']
                nom_id = data_2['Id']
                alliance = data_2['AllianceName'] if data_2['AllianceName'] else "Pas d'alliance"
                alliance_id = data_2['AllianceId']
                guilde = data_2['GuildName'] if data_2['GuildName'] else "Pas de guilde"
                guild_id = data_2['GuildId']
                kill_fame = f"{data_2['KillFame']:,}".replace(",", " ")
                death_fame = f"{data_2['DeathFame']:,}".replace(",", " ")
                FameRatio = data_2['FameRatio']
                nom_url = f"https://albiononline.com/killboard/player/{nom_id}?server=live_ams"
                guilde_url = f"https://albiononline.com/killboard/guild/{guild_id}?server=live_ams"
                alliance_url = f"https://albiononline.com/killboard/alliance/{alliance_id}?server=live_ams"

                PvE_fame_total = f"{data_2['LifetimeStatistics']['PvE']['Total']:,}".replace(",", " ")
                PvE_fame_Royal = f"{data_2['LifetimeStatistics']['PvE']['Royal']:,}".replace(",", " ")
                PvE_fame_Outlands = f"{data_2['LifetimeStatistics']['PvE']['Outlands']:,}".replace(",", " ")
                PvE_fame_Avalon = f"{data_2['LifetimeStatistics']['PvE']['Avalon']:,}".replace(",", " ")
                PvE_fame_Hellgate = f"{data_2['LifetimeStatistics']['PvE']['Hellgate']:,}".replace(",", " ")
                PvE_fame_CorruptedDungeon = f"{data_2['LifetimeStatistics']['PvE']['CorruptedDungeon']:,}".replace(",", " ")
                PvE_fame_Mists = f"{data_2['LifetimeStatistics']['PvE']['Mists']:,}".replace(",", " ")
                
                Gather_fame = f"{data_2['LifetimeStatistics']['Gathering']['All']['Total']:,}".replace(",", " ")

                Crafting_fame = f"{data_2['LifetimeStatistics']['Crafting']['Total']:,}".replace(",", " ")

                kill_fame_float = float(data_2['KillFame'])
                PvE_fame_total_float = float(data_2['LifetimeStatistics']['PvE']['Total'])
                if PvE_fame_total == 0:
                    Ratio_PvP_PvE = "PvE_fame is null"  # ou une autre valeur pertinente
                else:
                    Ratio_PvP_PvE = f"{kill_fame_float / PvE_fame_total_float:,.2f}".replace(",", " ")


                if guild_id : guild_final = f"[{guilde}]({guilde_url})"
                else : guild_final = guilde

                if alliance_id : alliance_final = f"[{alliance}]({alliance_url})"
                else : alliance_final = alliance

                    
                info_player += f"Pseudo : [{nom}]({nom_url}) \n"
                info_player += f"Nom de guilde : {guild_final} \n"
                info_player += f"Nom de l'alliance : {alliance_final} \n"
                info_player += f"Kill Fame : {kill_fame} \n"
                info_player += f"Death Fame : {death_fame} \n"
                info_player += f"Ratio KillFame/DeathFame : {FameRatio} \n"
                info_player += f"Ration Fame PvP/PvE: {Ratio_PvP_PvE} \n"
                info_player += "-------------------- \n"
                info_player += f"Fame PvE Total : {PvE_fame_total} \n"
                info_player += f"Fame PvE Royal : {PvE_fame_Royal} \n"
                info_player += f"Fame PvE Outlands : {PvE_fame_Outlands} \n"
                info_player += f"Fame PvE Avalon : {PvE_fame_Avalon} \n"
                info_player += f"Fame PvE Hellgate : {PvE_fame_Hellgate} \n"
                info_player += f"Fame PvE CorruptedDungeon : {PvE_fame_CorruptedDungeon} \n"
                info_player += f"Fame PvE Mists : {PvE_fame_Mists} \n"
                info_player += "-------------------- \n"
                info_player += f"Fame Gather : {Gather_fame} \n"
                info_player += f"Fame Craft : {Crafting_fame} \n"
                

                # Créer un embed pour renvoyer les informations sur Discord
                embed = Embed(title="Information d'un joueur Albion", color=Color.purple())
                embed.add_field(name="", value= info_player)

                # Envoyer l'embed sur Discord
                await interaction.followup.send(embed=embed)
            else:
                await interaction.followup.send(f"Aucun joueur trouvé avec le nom : {name}")
    
        except Exception as e:
            await interaction.followup.send(f"Erreur lors de la récupération des données : {e}")

        
        
        #send_message = f"Alors pour le moment, {member.mention} peux bien aller te faire "
        #await interaction.followup.send(f"{send_message}") 







def setup(bot):
  
  bot.add_cog(Raid_helper(bot))