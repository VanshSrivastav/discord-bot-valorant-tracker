import discord, dotenv, os
from discord.ext import commands
from discord import app_commands


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

dotenv.load_dotenv()
bot_token = os.getenv("bot_token")
intents = discord.Intents.default()
intents.message_content = True

client = Client(command_prefix="!", intents=intents)

GUILD_ID = discord.Object(id=1436451930288291985)

@client.tree.command(name='hello', description="Learn", guild=GUILD_ID)
async def sayHello(interaction: discord.Interaction):
    await interaction.response.send_message("Hello")

@client.tree.command(name='register', description="register your riot id with your discord id")
async def register(interaction: discord.Interaction):
    pass


client.run(bot_token)
