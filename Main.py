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
        "prop": "extracts",
        "titles": search,
    }

    response = requests.get(url, params=params)
    data = response.json()

    if response.status_code != 200:
        await interaction.response.send_message(f"Error fetching page: {response.status_code}")
        return
    
    data = response.json()

    # Print out the response data to debug
    print(data)

    pages = data.get("query", {}).get("pages", {})
    if pages and "revisions" in pages[0]:
        content = pages[0]["revisions"][0]["content"]

        # Truncate the message if it's too long for Discord
        if len(content) > 2000:
            content = content[:2000] + "...\nContent too long. Please check the wiki for more details."

        await interaction.response.send_message(content)
    else:
        await interaction.response.send_message("No pages found with that title or no content available.")



client.run(os.getenv('TOKEN'))
