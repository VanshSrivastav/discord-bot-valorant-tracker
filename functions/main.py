import discord, dotenv, os, asyncpg
from discord.ext import commands
from discord import app_commands
import valo_api
import valo_api.endpoints as endpoints
import json

GUILD_ID = discord.Object(id=1436451930288291985) # id of test server
dotenv.load_dotenv()
bot_token = os.getenv("bot_token")
connection_string = os.getenv('connection_string')


class Client(commands.Bot):
    async def on_ready(self):
        print(f"Logged in as {self.user}!")

        try:
            guild = discord.Object(id=1436451930288291985)
            synced = await self.tree.sync(guild=guild)
            print("synced")
        except Exception as e:
            print(f"Error synching commands {e}")
            

    async def on_message(self, message):
        if message.author == self.user:
            return
        if client.user in message.mentions:
            await message.channel.send(f'Shadi is my second engineer in this project')


intents = discord.Intents.default()
intents.message_content = True

client = Client(command_prefix="!", intents=intents)


@client.tree.command(name='hello', description="Learn", guild=GUILD_ID)
async def sayHello(interaction: discord.Interaction):
    await interaction.response.send_message("Hello")

@client.tree.command(name='register', description="register your riot id with your discord id", guild=GUILD_ID)
async def register_user(interaction:discord.Interaction, tracker_id: str): # no type hinting for interaction here due to input params (?)
    '''
    Description: Register command for user to register their tracker.gg id to their discord id and store in DB
    Usage: /register tracker_id: name #
    '''

    discord_id = interaction.user.id
    conn = await asyncpg.connect(connection_string) # connect to our database instance
    server_id = interaction.guild_id
    server_name = interaction.guild.name.lower()

    # sanitize the tracker gg id input

    tracker_id_clean = tracker_id.replace(' ', '')
    tracker_id_clean = tracker_id_clean.lower()

    user_exists = await conn.fetchrow(
        "SELECT * FROM users WHERE discord_id = $1",
        discord_id
    )

    server_exists = await conn.fetchrow(
        "SELECT * FROM servers WHERE server_id = $1",
        server_id
    )

    server_user_exists = await conn.fetchrow(
        "SELECT * FROM server_users WHERE discord_id = $1 AND server_id = $2",
        discord_id, server_id
    )

    if server_user_exists:
        await interaction.response.send_message(f"Your account is already registered with this server")
    
    else:

        if not user_exists:
            await conn.execute(
                "INSERT INTO users (discord_id, tracker_id) VALUES ($1, $2)",
                discord_id, tracker_id_clean
            )
    
        if not server_exists:
            await conn.execute(
                "INSERT INTO servers (server_id, server_name)" \
                "VALUES($1, $2)",
                server_id, server_name
            )

            await conn.execute(
                "INSERT INTO server_users (server_id, discord_id)" \
                "VALUES ($1, $2)",
                server_id, discord_id
            )
        
        elif not server_user_exists:
            await conn.execute(
                "INSERT INTO server_users (server_id, discord_id)" \
                "VALUES ($1, $2)",
                server_id, discord_id
            )
            
        
        await interaction.response.send_message(f"Registered user {tracker_id} with {server_name}")



@client.tree.command(name='my-stats', description="retrieve your own stats", guild=GUILD_ID)
async def retrieve_my_stats(interaction:discord.Interaction):

    conn = await asyncpg.connect(connection_string) # connect to our database instance

    discord_id = interaction.user.id
    val_api_key = os.getenv("val_api_key")

    user_exists = await conn.fetchrow(
        "SELECT * FROM users WHERE discord_id = $1",
        discord_id
    )


    if user_exists:
        valo_api.set_api_key(val_api_key)
        record = await conn.fetchrow(
            "SELECT tracker_id FROM users WHERE discord_id = $1",
            discord_id
        )

        tracker_id = record[0]
        print(tracker_id)
        name,tag = tracker_id.split("#")

        response = endpoints.get_mmr_history_by_name_v1(
            version="v1",
            region="na",
            name=name,
            tag=tag
        )

        for match in response:
            print(f"Map: {match.map.name}")
            print(f"Rank: {match.currenttierpatched} (ELO {match.elo})")
            print(f"MMR change: {match.mmr_change_to_last_game}")
            print(f"Date: {match.date}")
            print(f"Match ID: {match.match_id}")
            print(f"Rank image URL: {match.images.small}")
            print("-" * 40)    
    else:
        await interaction.response.send_message(f"Could not retrieve data for {interaction.user.name}, please register your account.")



        
client.run(bot_token)