import nextcord
from nextcord import slash_command
from nextcord.ext import commands
import gspread
import datetime
import sqlite3
from oauth2client.service_account import ServiceAccountCredentials
from config import settings

class Info(commands.Cog):

  def __init__(self, bot):
    self.bot = bot

  @commands.Cog.listener()
  async def on_ready(self):
    print("Info.py is ready!")


  
  @slash_command(name="help_cmd", description="Show every command")
  async def help_cmd(self,
    interaction: nextcord.Interaction
  ):
    await interaction.response.defer()
    send_message = """BBBBOOOOLLLLLOOOOSSSS faut dm dowo pas le bot :facepalm:
    """
  
    await interaction.followup.send(f"{send_message}")


    


def setup(bot):
  bot.add_cog(Info(bot))