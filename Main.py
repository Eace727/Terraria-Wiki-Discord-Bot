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
    # (make sure to capitalize all words including letters after an apostrophe
    # eg. "Grox the Great's wings" -> "Grox The Great'S Wings")
    ExceptionWords = [
        "Hand Of Creation",
        "Can Of Worms",
        "Grox The Great'S Wings",
        "Grox The Great'S Horned Cowl",
        "Grox The Great'S Chestplate",
        "Grox The Great'S Greaves",
        ]
    
    # Capitalize the first letter of each word in the search term except for "of" and "the"
    search = search.title()
    if search not in ExceptionWords:
        search = search.replace("Of", "of")
        search = search.replace("The", "the")
        search = search.replace("'S", "'s")
 
    url = "https://terraria.wiki.gg/api.php"
    params = {
        "action": "parse",
        "format": "json",
        "page": search,
        "prop": "text",
        "redirects": "true",
    }

    paramsimage = {
        "action": "query",
        "format": "json",
        "title": search,
        "prop": "imageinfo",
        "iiprop": "url",
    }

    # Make a request to the Terraria wiki API
    response = requests.get(url, params=params)
    image_response = requests.get(url, params=paramsimage)

    # Check if the request was successful
    if response.status_code != 200:
        await interaction.followup.send(f"Error fetching page: {response.status_code}")

    # Extract the HTML and Image content
    html_content = response.json().get("parse", {}).get("text", {}).get("*")
    image_content = image_response.json().get("query", {}).get("pages", {})
    image_urls = []
    for page_id, page_data in image_content.items():
        if "imageinfo" in page_data:
            image_info = page_data["imageinfo"][0]
            image_urls.append(image_info["url"])

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

        types = ""
        tables = soup.find_all('table')
        temp = tables[0].find_all('td')
        temp2 = temp[0].find_all('a')
        for i in range(len(temp2)):
            types += temp2[i].get_text() + "\n"

        # Get the image URL

        print (image_urls)

        text_content = Description

        # Truncate the message if it's too long for Discord
        if len(text_content) > 2000:
            text_content = text_content[:1900] + "...\nContent too long. Please check the wiki for more details."
    
        await interaction.followup.send(text_content)
    else:
        await interaction.followup.send("No pages found with that title or no content available.")

client.run(os.getenv('TOKEN'))
