import os
import discord
from dotenv import load_dotenv

load_dotenv()

class BMO(discord.Client):
    async def on_ready(self):
        print(f'Logged on as {self.user}!')

    async def on_message(self, message):
        print(f'Message from {message.author}: {message.content}')


def run_bot():
    intents = discord.Intents.default()
    intents.message_content = True

    client = BMO(intents=intents)
    client.run(os.getenv('DISCORD_TOKEN'))

