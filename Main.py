import discord
import os
from discord.ext import commands
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup

load_dotenv()
intents = discord.Intents.default()
intents.message_content = True

client = commands.Bot(command_prefix='!', intents=intents)

@client.event
async def on_ready():
    await client.tree.sync()
    print('We have logged in as {0.user}'.format(client))

# Sends pong to channel when pinged
@client.tree.command(name="ping", description="Check the bot's latency")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong!")

# Searches the Terraria wiki for the given search term
@client.tree.command(name="search", description="Search the Terraria wiki")
async def search_wiki(interaction: discord.Interaction, search: str):
    # Defer the response to avoid the 3 second timeout limit on discord
    await interaction.response.defer()

    url = "https://terraria.wiki.gg/api.php"
    
    params = {
        "action": "parse",
        "format": "json",
        "page": search,
        "prop": "text",
    }

    # Make a request to the Terraria wiki API
    response = requests.get(url, params=params)

    # Check if the request was successful
    if response.status_code != 200:
        await interaction.followup.send(f"Error fetching page: {response.status_code}")
        return

    # Extract the HTML content
    html_content = response.json()["parse"]["text"]["*"]

    if html_content:
        # Switched from htmlparser to Beautiful soup for better parsing
        soup = BeautifulSoup(html_content, 'html.parser')
        paragraphs = soup.find_all('p')
        text_content = ""
        for p in paragraphs:
            print(p.get_text())
        if len(paragraphs) > 1:
            for i in range(len(paragraphs)):
                if paragraphs[i].get_text() != "": 
                    text_content += paragraphs[i].get_text() + "\n"
        else:
            text_content = paragraphs[0].get_text()

        # Truncate the message if it's too long for Discord
        if len(text_content) > 2000:
            text_content = text_content[:1900] + "...\nContent too long. Please check the wiki for more details."

        
        await interaction.followup.send(text_content)
    else:
        await interaction.followup.send("No pages found with that title or no content available.")

client.run(os.getenv('TOKEN'))
