import os
import discord
from discord import app_commands
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.all()
intents.message_content = True
intents.members = True

bmo = discord.Client(intents=intents)
tree = app_commands.CommandTree(bmo)

@bmo.event
async def on_ready():
    print(f'Logged on as {bmo.user}!')
    try:
        synced = await tree.sync()
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print("não cadastrou nenhum comando")

@bmo.event
async def on_message(message):
    print(f'Message from {message.author}: {message.content}')


async def run_bot():
    await bmo.start(os.getenv('DISCORD_TOKEN'))

@tree.command(name="gpt")
@app_commands.describe(prompt="fala ai")
async def gpt(interaction, prompt: str):
    await interaction.response.send_message(prompt)