import nextcord
from nextcord import *
from nextcord.ext import commands
from config import settings
import requests
import random
from cogs.ticket.Model_Ticket import Model_Ticket





#class Ticket --------------------------------------------------------------------
class Ticket(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        Model_Ticket.create_table()


    @commands.Cog.listener()
    async def on_ready(self):
        print("Ticket.py is ready!")

    
    @slash_command(name="extract_list_member", description="Exctract la liste des joueurs")
    async def extract_list_member(self,
        interaction: Interaction,
    ):
        # Defer the interaction response
        await interaction.response.defer(ephemeral=True)#ephemeral=True)

        guild = interaction.guild

        if not guild:
            await interaction.response.send_message("Error: Unable to find the guild.")
            return
        
        members = guild.members  # List of members already cached

        

        with open("liste_membres.txt", "w", encoding="utf-8") as file:
            for member in members:
                role_member = False
                if member.get_role(settings.id_role_member):
                    role_member = True
                pseudo = member.name
                tag = member.discriminator
                user_id = member.id
                file.write(f"(member={role_member}) ({pseudo}#{tag}) ({user_id}) ({member.display_name}) \n")

        await interaction.followup.send(f"Exctract finished")





    @slash_command(name="set_vouch", description="add the voucher on the list")
    async def set_vouch(self,
        interaction: Interaction,
        new_member: Member = SlashOption(description="Tag the player who wanna register inside the discord", required=True),
        voucher: Member = SlashOption(description="Tag the player who is the voucher", required=True),
    ):
        # Defer the interaction response
        await interaction.response.defer(ephemeral=False)#ephemeral=True)

        try :
            query = Model_Ticket.select().where((Model_Ticket.discord_id == new_member.id) & (Model_Ticket.active == True)).get()
            await interaction.followup.send(f"{new_member.mention} is already vouched by <@{query.voucher_discord_id}>")


        except :

            Model_Ticket.create(discord_id=new_member.id, 
                            discord_name=new_member.name, 
                            discord_display_name=new_member.display_name, 
                            voucher_discord_id=voucher.id, 
                            voucher_discord_name=voucher.name,
                            voucher_discord_display_name=voucher.display_name,
                            active=True
                            )
        
            await interaction.followup.send(f"{new_member.mention} is vouched by {voucher.mention}")


    # remove the vouch from a member
    @slash_command(name="remove_vouch", description="Disactivate the vouch from a player (will not remove it from the list to keep a history)")
    async def remove_vouch(self,
        interaction: Interaction,
        member: Member = SlashOption(description="Tag the member who the voucher wanna remove his vouch", required=True)
    ):

        # Defer the interaction response
        await interaction.response.defer(ephemeral=False)#ephemeral=True)

        try :
            query = Model_Ticket.select().where((Model_Ticket.discord_id == member.id) & (Model_Ticket.active == True)).get()
            Model_Ticket.update(active=False).where((Model_Ticket.discord_id == member.id) & (Model_Ticket.active == True)).execute()
            await interaction.followup.send(f"<@{query.voucher_discord_id}> is removed as vouch for {member.mention}")

        except :
            await interaction.followup.send(f"{member.mention} isn't vouched yet.>")



    @slash_command(name="unvouch_member", description="give you 5 unvouch member to give the correct vouch")
    async def unvouch_member(self,
        interaction: Interaction,
    ):
        # Defer the interaction response
        await interaction.response.defer(ephemeral=False)#ephemeral=True)

        guild = interaction.guild

        if not guild:
            await interaction.response.send_message("Error: Unable to find the guild.")
            return
        
        members = guild.members  # List of members already cached

        


        send_msg = ""
        i = 0
        n = 0
        for member in members:
            if member.get_role(settings.id_role_member):   
                try :
                    query = Model_Ticket.select().where((Model_Ticket.discord_id == member.id)).get()
                    n += 1

                except:
                    i += 1 
                    pseudo = member.name
                    tag = member.discriminator
                    user_id = member.id
                    send_msg += (f"({pseudo}#{tag}) ({user_id}) ({member.display_name}) \n")
            else:
                n += 1
            if i >=5:
                break

        if len(members) == 0:
            send_msg = f"Y'a plus rien a faire, let's go !!"
        else:
            send_msg += (f"il reste encore {len(members)-n} à traiter")


        await interaction.followup.send(send_msg)


    @slash_command(name="list_vouch", description="See how many people the member have vouch and see the list if needed")
    async def list_vouch(self,
        interaction: Interaction,
        member: Member = SlashOption(description="Tag the player to see the number of people vouch by him", required=True),
        see_the_list: bool = SlashOption(description="If True, see the full list of people",choices={"True" : True, "False": False}, required=False),
    ):
        # Defer the interaction response
        await interaction.response.defer(ephemeral=False)#ephemeral=True)

        try :
            query = Model_Ticket.select().where((Model_Ticket.voucher_discord_id == member.id) & (Model_Ticket.active == True)).order_by(Model_Ticket.discord_display_name)

            await interaction.followup.send(f"{member.mention} have {len(query)} members vouch at his name.")

            if see_the_list:
                list_player = "" # value de l'embed par default
                for user in query:
                    list_player += f"<@{user.discord_id}> "


                embed = Embed(title="Information d'un joueur Albion", color=Color.purple())
                embed.add_field(name="", value= list_player)
                await interaction.followup.send(embed=embed)


        except :
            await interaction.followup.send(f"{member.mention} have vouched no one yet.>")

        
   

def setup(bot):
  bot.add_cog(Ticket(bot))