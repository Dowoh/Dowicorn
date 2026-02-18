from config import settings
import peewee




database = peewee.SqliteDatabase(f"database/{settings.database}")