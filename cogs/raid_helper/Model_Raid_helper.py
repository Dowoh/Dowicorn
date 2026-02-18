from peewee import *
from database.database import database


class Model_Raid_helper(Model):
    
    discord_id                      = IntegerField()
    discord_name                    = CharField()
    discord_display_name            = CharField()
    nombre_raid                     = IntegerField()
        
    class Meta:
        database = database