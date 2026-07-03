import os
import discord
from discord import app_commands
import asyncio
import utils
import json
import io
from rich import print
import requests
from dotenv import load_dotenv

load_dotenv()

channel_geral = 701502306545434807
guild_principal = 701502306545434804
kao_error = '𖦹 ´ ᯅ ` 𖦹'

intents = discord.Intents.all()
intents.message_content = True
intents.members = True

bmo = discord.Client(intents=intents)
tree = app_commands.CommandTree(bmo)


async def require_discord_admin(interaction: discord.Interaction) -> bool:
    permissions = getattr(interaction.user, "guild_permissions", None)
    if permissions and permissions.administrator:
        return True

    await interaction.response.send_message(
        "Este comando requer permissao de administrador.",
        ephemeral=True,
    )
    return False


async def send_api_response(
    interaction: discord.Interaction,
    title: str,
    payload,
    filename: str,
):
    content = json.dumps(payload, ensure_ascii=False, indent=2)
    message = f"**{title}**\n```json\n{content}\n```"

    if len(message) <= 2000:
        await interaction.followup.send(message, ephemeral=True)
        return

    file = discord.File(
        io.BytesIO(content.encode("utf-8")),
        filename=filename,
    )
    await interaction.followup.send(
        f"**{title}**",
        file=file,
        ephemeral=True,
    )


async def send_cacareco_error(interaction: discord.Interaction, error: Exception):
    if isinstance(error, requests.RequestException):
        response = getattr(error, "response", None)
        detail = response.text if response is not None else str(error)
    else:
        detail = str(error)

    await interaction.followup.send(
        f"Erro ao chamar a API Cacareco: {detail[:1500]}",
        ephemeral=True,
    )

@bmo.event
async def on_ready():
    print(f'Logged on as {bmo.user}!')
    try:
        guild = discord.Object(id=guild_principal)
        tree.copy_global_to(guild=guild)
        synced_guild = await tree.sync(guild=guild)
        print(f"Synced {len(synced_guild)} commands to guild {guild_principal}")
        synced = await tree.sync()
        print(f"Synced {len(synced)} commands globally")
    except Exception as e:
        print(f"Error syncing commands: {e}")
        print("não cadastrou nenhum comando")

async def send_completion(prompt, api): 
    channel = bmo.get_channel(channel_geral)
    response = await utils.get_completion(prompt, channel_geral, 'shortcuts') 
    await channel.send('**prompt**: ' + prompt)
    for msg in utils.split_text(response["message"]):
        await channel.send(msg)


@bmo.event
async def on_message(message):
    print(message.channel.id)
    print(f'Message from {message.author}: {message.content}')
    if message.content == '(´･_ ･`)':
        return
    if message.author.bot:
        return
    if message.channel.id == 1203547736792764416:
        utils.handleHevyWorkout(message.content)
    if message.channel.type.name == 'public_thread':
        response = await utils.get_agent_response(message.content, message.channel.id)
        await message.channel.send(response["message"])
        # await handle_thread_chat(message)
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
    with open('assets/loading.gif', 'rb') as f:
        picture = discord.File(f)
    loading = await msg.channel.send(file=picture)
    return loading


# --------
# commands
# --------

@tree.command(name="test")
@app_commands.describe(input="fala ai")
async def test(interaction, input: str):
    await utils.push()
    await interaction.followup.send('oi')

@tree.command(name="optimize")
@app_commands.describe(prompt="optimize this prompt")
async def optimize(interaction, prompt: str):
    await interaction.response.defer(thinking=True)
    optimized_prompt = await utils.optimize_prompt(prompt)
    await interaction.followup.send(optimized_prompt)

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
            For every translation you make, make at least 5 versions of the translation.
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

@tree.command(name="http")
@app_commands.describe(url="url", body="body", params="Url Params", header="Headers")
@app_commands.choices(method=[
    app_commands.Choice(name="GET", value="GET"),
    app_commands.Choice(name="POST", value="POST"),
    app_commands.Choice(name="PUT", value="PUT")
])
async def http(interaction, method: app_commands.Choice[str], url: str, body: str = None, params: str = None, header: str = None):
    await interaction.response.defer(thinking=True)
    response = await utils.http_request(url, method.value, body, params, header)
    
    if(response.get("is_file")):
        await interaction.followup.send(file=response.get("message"))
    else: 
        await interaction.followup.send(response.get("message"))

@tree.command(name="etsy")
@app_commands.default_permissions(administrator=True)
@app_commands.describe(
    listing_id="ID da listing para consultar",
    shop_id="ID da loja para listar produtos",
    estado="Estado das listings da loja",
    limite="Quantidade de listings da loja, entre 1 e 100",
    offset="Posicao inicial das listings da loja",
)
async def etsy(
    interaction: discord.Interaction,
    listing_id: str = None,
    shop_id: str = None,
    estado: str = "active",
    limite: int = 25,
    offset: int = 0,
):
    if not await require_discord_admin(interaction):
        return

    listing_id = listing_id.strip() if listing_id else None
    shop_id = shop_id.strip() if shop_id else None

    if bool(listing_id) == bool(shop_id):
        await interaction.response.send_message(
            "Informe apenas `listing_id` ou apenas `shop_id`.",
            ephemeral=True,
        )
        return
    if not 1 <= limite <= 100 or offset < 0:
        await interaction.response.send_message(
            "`limite` deve estar entre 1 e 100 e `offset` nao pode ser negativo.",
            ephemeral=True,
        )
        return

    await interaction.response.defer(thinking=True, ephemeral=True)

    try:
        if listing_id:
            response = await asyncio.to_thread(utils.get_etsy_listing, listing_id)
            title = f"Etsy listing {listing_id}"
        else:
            response = await asyncio.to_thread(
                utils.get_etsy_shop_listings,
                shop_id,
                state=estado,
                limit=limite,
                offset=offset,
            )
            title = f"Etsy shop {shop_id}"

        await send_api_response(interaction, title, response, "etsy-response.json")
    except (utils.CacarecoConfigError, requests.RequestException, ValueError) as error:
        await send_cacareco_error(interaction, error)


@tree.command(name="twitch")
@app_commands.default_permissions(administrator=True)
@app_commands.describe(
    canal="Canal que recebera as mensagens de teste",
    quantidade="Quantidade de mensagens, entre 1 e 100",
    intervalo="Intervalo em segundos, entre 0 e 60",
    mensagem="Mensagem personalizada opcional",
)
async def twitch(
    interaction: discord.Interaction,
    canal: str = "guinhoshuto",
    quantidade: int = 8,
    intervalo: float = 1.5,
    mensagem: str = None,
):
    if not await require_discord_admin(interaction):
        return

    canal = canal.strip()
    mensagem = mensagem.strip() if mensagem else None

    if not canal:
        await interaction.response.send_message(
            "`canal` nao pode ser vazio.",
            ephemeral=True,
        )
        return
    if not 1 <= quantidade <= 100 or not 0 <= intervalo <= 60:
        await interaction.response.send_message(
            "`quantidade` deve estar entre 1 e 100 e `intervalo` entre 0 e 60.",
            ephemeral=True,
        )
        return

    await interaction.response.defer(thinking=True, ephemeral=True)

    try:
        response = await asyncio.to_thread(
            utils.send_twitch_test_messages,
            channel_username=canal,
            quantity=quantidade,
            interval_seconds=intervalo,
            messages=[mensagem] if mensagem else None,
        )
        await send_api_response(
            interaction,
            f"Twitch test messages para {canal}",
            response,
            "twitch-response.json",
        )
    except (utils.CacarecoConfigError, requests.RequestException, ValueError) as error:
        await send_cacareco_error(interaction, error)


@tree.command(name="sync")
@app_commands.describe(guild_id="Guild ID to sync to (leave empty for global sync)")
async def sync(interaction, guild_id: str = None):
    """Manually sync slash commands"""
    await interaction.response.defer(ephemeral=True)
    try:
        if guild_id:
            guild = discord.Object(id=int(guild_id))
            synced = await tree.sync(guild=guild)
            await interaction.followup.send(f"Synced {len(synced)} commands to guild {guild_id}", ephemeral=True)
        else:
            synced = await tree.sync()
            await interaction.followup.send(f"Synced {len(synced)} commands globally", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"Error syncing commands: {str(e)}", ephemeral=True)
