import discord
import os
from discord.ext import commands
from dotenv import load_dotenv
import requests
from html.parser import HTMLParser

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

# HTML Parser class to extract text from HTML
class HTMLTextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.convert_charrefs = True
        self.text_parts = []

    def handle_data(self, d):
        self.text_parts.append(d)

    def get_text(self):
        return ''.join(self.text_parts)

# Searches the Terraria wiki for the given search term
@client.tree.command(name="search", description="Search the Terraria wiki")
async def search_wiki(interaction: discord.Interaction, search: str):
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
        await interaction.response.send_message(f"Error fetching page: {response.status_code}")
        return
    
    data = response.json()

    ## Searches other parts of the page that parse doesnt get
    #'
    #params = {
    #    "action": "query",
    #    "format": "json",
    #    "list": "search",
    #    "srsearch": search,
    #}
    #response = requests.get(url, params=params)
    #data2 = response.json()
    #
    #search_results = data2.get("query", {}).get("search", [])
    #print(search_results)
    # '

    # Extract the HTML content
    html_content = data.get("parse", {}).get("text", {}).get("*", "")

    if html_content:
        # Create an instance of the HTMLTextExtractor
        extractor = HTMLTextExtractor()
        extractor.feed(html_content)
        text_content = extractor.get_text()
        print(text_content)

        # Truncate the message if it's too long for Discord
        if len(text_content) > 2000:
            text_content = text_content[:1800] + "...\nContent too long. Please check the wiki for more details."

        
        await interaction.response.send_message(text_content)
    else:
        await interaction.response.send_message("No pages found with that title or no content available.")

client.run(os.getenv('TOKEN'))
