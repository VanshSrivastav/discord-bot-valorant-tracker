import discord, dotenv, os, asyncpg
from discord.ext import commands
from discord import app_commands


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

    print("SERVER", server_id)

    await conn.execute(
        "INSERT INTO users VALUES($1, $2)", # $1, $2 are auto sanitized by asyncpg
        discord_id, tracker_id.lower()
    )

    print(discord_id, tracker_id)

    await interaction.response.send_message(f"Registered user {tracker_id}")

client.run(bot_token)