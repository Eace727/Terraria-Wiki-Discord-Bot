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

    # Exception Words that need to be capitalized differently
    # (make sure to capitalize all words
    # eg. "hand of creation" -> "Hand Of Creation")
    ExceptionWords = [
        "Hand Of Creation",
        "Can Of Worms",
        "Grox The Great's Wings",
        "Grox The Great's Horned Cowl",
        "Grox The Great's Chestplate",
        "Grox The Great's Greaves",
        ]
    
    # Capitalize the first letter of each word in the search term except for "of" and "the"
    search = search.title()
    if search not in ExceptionWords:
        search = search.replace("Of", "of")
        search = search.replace("The", "the")

 
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

    # Extract the HTML content
    html_content = response.json().get("parse", {}).get("text", {}).get("*")

    if html_content:
        # Switched from htmlparser to Beautiful soup for better parsing
        soup = BeautifulSoup(html_content, 'html.parser')
        text_content = ""

        paragraphs = soup.find_all('p')
        Description = ""
        #for p in paragraphs:             #debugging for paragraphs
        #    print(p.get_text())
        if len(paragraphs) > 1:
            for i in range(len(paragraphs)):
                if paragraphs[i].get_text() != "": 
                    Description += paragraphs[i].get_text() + "\n"
        else:
            Description = paragraphs[0].get_text()


        something = soup.find_all('td')
        for td in something:                #debugging for list items
            print(td.get_text())
        for i in range(len(something)):
            if something[i].get_text() != "":
                text_content += something[i].get_text() + "\n"

        # Truncate the message if it's too long for Discord
        if len(text_content) > 2000:
            text_content = text_content[:1900] + "...\nContent too long. Please check the wiki for more details."
    
        await interaction.followup.send(text_content)
    else:
        await interaction.followup.send("No pages found with that title or no content available.")

client.run(os.getenv('TOKEN'))
