import os
import discord
from discord import app_commands
import asyncio
import utils
from rich import print
from dotenv import load_dotenv

load_dotenv()

channel_geral = 701502306545434807

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

async def send_completion(prompt, api): 
    channel = bmo.get_channel(channel_geral)
    response = await utils.get_completion(prompt, channel_geral, 'shortcuts') 
    await channel.send(response["message"])


@bmo.event
async def on_message(message):
    print(f'Message from {message.author}: {message.content}')
    if message.author.bot:
        return
    if message.attachments:
        for attachment in message.attachments:
            print(attachment.content_type)
            if attachment.content_type.startswith('image'):
                reply = await loadingMsg(message)
                img_suggestions = await utils.get_image_suggestions(message)
                await reply.delete()
                for msg in utils.split_text(img_suggestions):
                    await message.channel.send(msg)
                # await message.channel.send(img_suggestions)

async def run_bot():
    await bmo.start(os.getenv('DISCORD_TOKEN'))

async def loadingMsg(msg):
    with open('assets/thinking.gif', 'rb') as f:
        picture = discord.File(f)
    loading = await msg.channel.send(file=picture)
    return loading


async def get_thread_history(channel):
    history = []
    async for message in channel.history(limit=100):
        history.append(message.content)
    return history

# --------
# commands
# --------

@tree.command(name="test")
@app_commands.describe(input="fala ai")
async def test(interaction, input: str):
    await utils.push()
    await interaction.followup.send('oi')

@tree.command(name="gemini")
@app_commands.describe(input="fala ai")
async def test(interaction, input: str):
    await interaction.response.defer(thinking=True)
    msg = await utils.get_gemini_completion(input)
    await interaction.followup.send(msg)

@tree.command(name="mistral")
@app_commands.describe(prompt="fala ai", model="modelo")
async def test(interaction, prompt: str, model:str = "mistral-medium"):
    await interaction.response.defer(thinking=True)
    response = await utils.get_mistral_completion(prompt, model)
    await interaction.followup.send(f"**Prompt**: {prompt}")
    for msg in utils.split_text(response["message"]):
        await interaction.followup.send(msg)


@tree.command(name="gpt")
@app_commands.describe(prompt="fala ai", system="quem vc pensa que é?")
async def gpt(interaction, prompt:str, system: str = None):
    history=None
    # print(interaction.channel.type)
    await interaction.response.defer(thinking=True)
    if interaction.channel.type == discord.ChannelType.public_thread:
        history = get_thread_history(interaction.channel_id)
    print(history)
    response = await utils.get_completion(prompt, interaction.channel_id, interaction.user, system=system, history=history) 
    await interaction.followup.send(f"**Prompt**: {prompt}")
    for msg in utils.split_text(response["message"]):
        await interaction.followup.send(msg)

@tree.command(name="babel")
@app_commands.describe(prompt="diga lá", lang="english or japanese", mood="in a ... way")
async def babel(interaction, prompt: str, lang: str = "english", mood: str = "normal"):
    await interaction.response.defer(thinking=True)
    response = await utils.get_completion(
        f"""I want you to act as an {lang} translator, \
            spelling corrector and improver. \
            Translate the text delimited by triple backticks. \
            It is in brazilian portuguese and you will translate it \
            and answer in the corrected and improved version of my text, \
            in {lang}. I want you to only reply the correction, \
            the improvements and nothing else, \ 
            do not write explanations and make it in a {mood} way. \ 
            My first sentence is ```{prompt}```""", interaction.channel_id, interaction.user)
    await interaction.followup.send(response["message"])

@tree.command(name="search")
@app_commands.describe(search="lmgfy")
async def search(interaction, search: str):
    await interaction.response.defer(thinking=True)
    response = utils.search_for_discord(search)
    print(response["items"])
    await interaction.followup.send(response["message"])
    # await interaction.followup.send(view=view)



