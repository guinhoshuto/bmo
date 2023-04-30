import os
import discord
from discord import app_commands
import asyncio
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
async def gpt(interaction, prompt:str, system: str = None):
    await interaction.response.defer(thinking=True)
    # await interaction.response.send('oi')
    # thread = await interaction.original_response().create_thread(
    #     name=f"{prompt}",
    #     auto_archive_duration=60
    # )
    response = await utils.getCompletion(prompt, system) 
    await interaction.followup.send(response.choices[0].message.content)

@tree.command(name="babel")
@app_commands.describe(prompt="diga lá", lang="english or japanese", mood="in a ... way")
async def babel(interaction, prompt: str, lang: str = "english", mood: str = "normal"):
    await interaction.response.defer(thinking=True)
    response = await utils.getCompletion(
        f'I want you to act as an {lang} translator, spelling corrector and improver. I will speak to you in brazilian portuguese and you will translate it and answer in the corrected and improved version of my text, in {lang}. I want you to only reply the correction, the improvements and nothing else, do not write explanations and make it in a {mood} way. My first sentence is "{prompt}"')
    await interaction.followup.send(response.choices[0].message.content)




