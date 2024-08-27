import discord
import os
from discord.ext.commands import Bot
from discord.ext import commands
from dotenv import load_dotenv
import requests

load_dotenv()
intents = discord.Intents.default()
intents.message_content = True


client = commands.Bot(command_prefix='!', intents=intents)

@client.event
async def on_ready():
    await client.tree.sync()
    print('We have logged in as {0.user}'.format(client))

# sends pong when pinged
@client.tree.command(name="ping", description="Check the bot's latency")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong!")

# searches the terraria wiki for the given search term
@client.tree.command(name="search", description="search the terraria wiki")
async def search_wiki(interaction: discord.Interaction, search: str):
    url = "https://terraria.wiki.gg/api.php"
    
    params = {
        "action": "query",
        "format": "json",
        "list": "search",
        "srsearch": search
    }

    response = requests.get(url, params=params)
    data = response.json()

    if data["query"]["search"]:
        # Retrieve the first search result
        result = data["query"]["search"][0]
        title = result["title"]
        snippet = result["snippet"]

        # Format the response message
        message = f"**{title}**\n{snippet}..."
    else:
        message = "No results found."

    await interaction.response.send_message(message)


client.run(os.getenv('TOKEN'))
