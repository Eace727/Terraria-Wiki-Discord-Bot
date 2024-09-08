import discord
import os
from discord.ext import commands
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup

load_dotenv()
intents = discord.Intents.default()
intents.message_content = True
searchword = ""
description = ""

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
    
    # Words that need to be lowercase 
    LowercaseWords = [
        "Attack Speed",
        "Critical Hit",
        "Npc Drops",
        "Day And Night Cycle",  
        "Moon Phase",
        "Player Stats",
        "Status Messages",
        "World Size",
    ]

    # Capitalize the first letter of each word in the search term except for "of" and "the"
    search = search.title()
    if search not in ExceptionWords:
        search = search.replace("Of", "of")
        search = search.replace("The", "the")
        search = search.replace("'S", "'s")

    # lowercase the second word if it is in the Mechanics list
    if search in LowercaseWords:
        search = search.lower()

    #print (search)         #debugging for search
 
    url = "https://terraria.wiki.gg/api.php"
    params = {
        "action": "parse",
        "format": "json",
        "page": search,
        "prop": "text",
        "redirects": "true",
    }

    # Make a request to the Terraria wiki API
    response = requests.get(url, params=params)

    # Check if the request was successful
    if response.status_code != 200:
        await interaction.followup.send(f"Error fetching page: {response.status_code}")

    # Extract the HTML and Image content
    html_content = response.json().get("parse", {}).get("text", {}).get("*")

    if html_content:
        # Switched from htmlparser to Beautiful soup for better parsing
        soup = BeautifulSoup(html_content, 'html.parser')
        text_content = ""

        # Get the first or all paragraphs of the page
        paragraphs = soup.find_all('p')
        Description = ""
        #for p in paragraphs:             #debugging for paragraphs
        #    print(p.get_text())
        if len(paragraphs) > 1:
            for i in range(len(paragraphs)):
                if paragraphs[i].get_text() != "": 
                    Description += paragraphs[i].get_text() + "\n"
        elif len(paragraphs) == 1:
            Description = paragraphs[0].get_text()

        # Get the types of the item if it is an item
        types = ""
        tables = soup.find_all('table')
        if len(tables) > 0:
            temp = tables[0].find_all('td')
            temp2 = temp[0].find_all('span')
            for i in range(len(temp2)):
                types += temp2[i].get_text() + "\n"

        # Get the statistics of the item if it is an item

        # Rarity Colors
        Rarity = {
            "-1*" : "Gray",
            "00*" : "White",
            "01*" : "Blue",
            "02*" : "Green",
            "03*" : "Orange",
            "04*" : "Light Red",
            "05*" : "Pink",
            "06*" : "Light Purple",
            "07*" : "Lime",
            "08*" : "Yellow",
            "09*" : "Cyan",
            "10*" : "Red",  
            "12*" : "Rainbow",
            "13*" : "Fiery Red",
        }

        statistics = ""
        tables = soup.find_all('table')
        if len(tables) > 0:
            for i in range(len(tables)):
                if "stat" in tables[i]['class']:
                    tablerow = tables[i].find_all('tr')
                    for j in range(len(tablerow)):
                        tableHeader = tablerow[j].find_all('th')
                        tableData = tablerow[j].find_all('td')
                        if len(tableHeader) > 0 and len(tableData) > 0:
                            statistics += tableHeader[0].get_text() + ": "  # Table Header
                            tableDataA = tableData[0].find_all('a')
                            for k in range(len(tableData)):
                                if tableHeader[0].get_text() == "Type":
                                    for l in range(len(tableDataA)):
                                        statistics += tableDataA[l].get_text() + " " # Types
                                elif tableHeader[0].get_text() == "Rarity":
                                    statistics += Rarity[tableData[k].get_text()] + " "
                                else:
                                    statistics += tableData[k].get_text() + " " # Rest of Table data


                        statistics += "\n"

        # Get the image URL

        # Get the first image that is not a version image
        Versions = [
            "/images/7/72/Desktop_only.png",
            "/images/6/6c/Console_only.png",
            "/images/b/b2/Mobile_only.png",
            "/images/4/4e/Old-Gen_Console_only.png",
            "https://commons.wiki.gg/images/8/8d/3DS.svg",
            "https://commons.wiki.gg/images/0/0f/New_Nintendo_3DS.svg",
            "/images/6/62/Expert_Mode.png",
            "/images/9/9b/Master_Mode.png",
        ]
        
        image_url = ""
        images = soup.find_all('img')
        if len(images) > 0:
            for i in range(len(images)):
                 if images[i]['src'] not in Versions:
                    image_url ="https://terraria.wiki.gg" +images[i]['src']
                    break
        
        # Get the crafting recipe / Used in if it is an item
        crafting = ""
        tables = soup.find_all('table')
        if len(tables) > 0:
            for i in range(len(tables)):
                if "craft" in tables[i]['class']:
                    tablerow = tables[i].find_all('tr')
                    for j in range(len(tablerow)):
                        tableData = tablerow[j].find_all('td')
                        if len(tableData) > 0:
                            for k in range(len(tableData)):
                                crafting += tableData[k].get_text() + " "
                        crafting += "\n"


        print (crafting)

        text_content = Description

        # Truncate the message if it's too long for Discord
        if len(text_content) > 2000:
            text_content = text_content[:1800] + "...\nContent too long. Please check the wiki for more details."
        descembed = discord.Embed(
            title = search,
            description = text_content,
            color = discord.Color.purple()
            )
        await interaction.followup.send(embed = descembed)
    else:
        await interaction.followup.send("No pages found with that title or no content available.")


class SelectView(discord.ui.View):
    #calls init from SelectView
    def __init__(self):
        #ensures init from discord.ui is also called
        super().__init__()
    
    #Create Options
    options =[
        discord.SelectOption(label="Description"),
        discord.SelectOption(label="Stats")
    ]

    @discord.ui.select(placeholder="Sections", options=options)

    async def select_callback(self, interaction: discord.Interaction,select: discord.ui.Select):
        selected_option = select.values[0]
        #For Description
        if selected_option =="Description":
            descripembed = discord.Embed(
                title=search
            )
            await interaction.response.send(embed=descriptembed))
        #For stats
        elif selected_option =="Stats":
            print("stats")

client.run(os.getenv('TOKEN'))
