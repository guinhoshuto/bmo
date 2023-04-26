import os
import discord
from discord import app_commands
import utils
from rich import print
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

# --------
# commands
# --------

@tree.command(name="gpt")
@app_commands.describe(prompt="fala ai", system="quem vc pensa que é?")
async def gpt(interaction, prompt: str, system: str):
    await interaction.response.defer(thinking=True)
    response = await utils.getCompletion(prompt, system) 
    # await interaction.followup.send(response.choices[0].message.content)
    await interaction.followup.send(response)