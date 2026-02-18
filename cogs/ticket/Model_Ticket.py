from peewee import *
from database.database import database


class Model_Ticket(Model):
    
    discord_id                      = IntegerField()
    discord_name                    = CharField()
    discord_display_name            = CharField()
    voucher_discord_id              = IntegerField()
    voucher_discord_name            = CharField()
    voucher_discord_display_name    = CharField()
    active                          = BooleanField()
        
    class Meta:
        database = database