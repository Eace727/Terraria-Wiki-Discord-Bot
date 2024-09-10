import discord
import os
import requests
from typing import Tuple
from discord.ext import commands
from dotenv import load_dotenv
from bs4 import BeautifulSoup

# Global Variables

# Dictionary for Rarity of Items
Rarity = {
    "Rarity level: -1" : "Gray",
    "Rarity level: 0" : "White",
    "Rarity level: 1" : "Blue",
    "Rarity level: 2" : "Green",
    "Rarity level: 3" : "Orange",
    "Rarity level: 4" : "Light Red",
    "Rarity level: 5" : "Pink",
    "Rarity level: 6" : "Light Purple",
    "Rarity level: 7" : "Lime",
    "Rarity level: 8" : "Yellow",
    "Rarity level: 9" : "Cyan",
    "Rarity level: 10" : "Red",
    "Rarity level: 11" : "Purple",  
    "Rarity level: Rainbow" : "Rainbow",
    "Rarity level: Fiery red" : "Fiery Red",
    "Rarity Level: 12" : "Turquoise",
    "Rarity Level: 13" : "Pure Green",
    "Rarity Level: 14" : "Dark Blue",
    "Rarity Level: 15" : "Violet",
    "Rarity Level: 16" : "Hot Pink",
    "Rarity Level: 17" : "Calamity Red",
    "Rarity Level: Draedon's Arsenal" : "Dark Orange",
}

# Coin Values for Sell Price
Coin = [
    "CC",
    "SC",
    "GC",
    "PC",
]

# Coin Dictionary for Coin Values for Sell Price
CoinDict = {
    "CC" : "Copper Coin(s)",
    "SC" : "Silver Coin(s)",
    "GC" : "Gold Coin(s)",
    "PC" : "Platinum Coin(s)",
}

# Version Differences list for Item Crafting
VersionDifference = [
    "(Desktop, Console and Mobile versions) /" ,
    "(Old-gen console and 3DS versions) ",
]

# List of Version/Event/Mode images that should not be displayed
VersionEventMode = [
    "/images/7/72/Desktop_only.png",
    "/images/6/6c/Console_only.png",
    "/images/b/b2/Mobile_only.png",
    "/images/4/4e/Old-Gen_Console_only.png",
    "https://commons.wiki.gg/images/8/8d/3DS.svg",
    "https://commons.wiki.gg/images/0/0f/New_Nintendo_3DS.svg",
    "/images/6/62/Expert_Mode.png",
    "/images/9/9b/Master_Mode.png",
    "/images/4/44/Horn_o%27_plenty.png",
    "/images/2/2f/Bestiary_Christmas.png",
    "/images/8/82/Suspicious_Looking_Egg.png",
    "/images/3/39/Bestiary_Halloween.png",
    "/images/d/df/Valentine_Ring.png",
    "/images/thumb/4/44/Soul_Scythe.png/32px-Soul_Scythe.png",
]


# Function to get suggestions from the Terraria wiki
# params: search (str) - the search term
# returns: suggestionsResponse (str) - the suggestions from the wiki
def suggestions(search: str) -> str:
    url = "https://terraria.wiki.gg/api.php"
    suggest_params = {
            'action': 'query',
            'format': 'json',
            'list': 'prefixsearch',
            'pssearch': search,
            'pslimit': 5  # Limit number of suggestions
        }
        
    suggest_response = requests.get(url, params=suggest_params)
    suggest_data = suggest_response.json()
        
    suggestions = suggest_data.get('query', {}).get('prefixsearch', [])

    if not suggestions:
        return "No suggestions found."

    # Build the suggestion response
    suggestionsResponse = "No Page found. Did you mean:\n"
    for suggestion in suggestions:
        suggestionsResponse += " - " + suggestion['title'] + "\n"

    # Return the first suggestion (if available)
    return suggestions[0]['title'] if suggestions else None

# Function to get the description of the page
# params: soup (BeautifulSoup object) - the BeautifulSoup object
# returns: Description (str) - the description of the page
def get_Description(soup: BeautifulSoup) -> str:
    Description = ""
    paraDiv = soup.find('div', class_="mw-parser-output")
    paragraphs = paraDiv.find_all('p', recursive=False)
    if len(paragraphs) > 0:
        for i in range(len(paragraphs)):
            if paragraphs[i].get_text() != "": 
                Description += paragraphs[i].get_text() + "\n"
    return Description


# Function to get the types of the item
# params: soup (BeautifulSoup object) - the BeautifulSoup object
# returns: types (str) - the types of the item
def get_Types(soup: BeautifulSoup) -> str:
    types = ""
    tables = soup.find_all('table', class_="stat")
    if len(tables) > 0:
        temp = tables[0].find_all('span', class_="nowrap tag")
        for i in range(len(temp)):
            types += temp[i].get_text() + "\n"
    return types


# Function to get the statistics of the item                                #probably break this up later***********
# params: soup (BeautifulSoup object) - the BeautifulSoup object
# returns: statistics (str) - the statistics of the item
def get_Statistics(soup: BeautifulSoup) -> str:
    statistics = ""
    tables = soup.find_all('table', class_="stat")
    if len(tables) > 0:
        tablerow = tables[0].find_all('tr')
        for j in range(len(tablerow)):
            tableHeader = tablerow[j].find('th')
            tableData = tablerow[j].find_all('td')
            if len(tableHeader) > 0 and len(tableData) > 0:
                statistics += tableHeader.get_text() + ": "  # Table Header
                for k in range(len(tableData)):
                    if tableHeader.get_text() == "Type":
                        tableDataA = tableData[k].find_all('a')
                        for l in range(len(tableDataA)):
                            statistics += tableDataA[l].get_text() # Types
                            if l+1 < len(tableDataA):
                                statistics += " / "
                    elif tableHeader.get_text() == "Rarity":
                        tableDataA = tableData[k].find('a')
                        statistics += Rarity[tableDataA['title']] + " " # Rarity
                    elif tableHeader.get_text() == "Sell":
                        tableDataA = tableData[k].find_all('span', class_="coin")
                        for l in range(len(tableDataA)):
                            tableDataCoin = tableDataA[l].find_all('span')
                            for m in range(len(tableDataCoin)):
                                coinvalues = tableDataCoin[m].get_text().split() # Sell Price
                                for n in range(len(coinvalues)):
                                    statistics += coinvalues[n] + " " if coinvalues[n] not in Coin else CoinDict[coinvalues[n]] + " "
                            if len(tableDataA) > 1:
                                statistics += VersionDifference[l] + " "
                    elif tableHeader.get_text() == "Tooltip":
                        tableDataA = tableData[k].find('i').find('span')
                        for br in tableDataA.find_all('br'):
                            br.replace_with(' / ')
                        statistics += tableDataA.get_text()  # Tooltip
                    else:
                        statistics += tableData[k].get_text() + " " # Rest of Table data
            statistics += "\n"
            statistics = statistics.replace("✔️", "✅")         
    return statistics


# Fix/Improve Function to get the image of the item****************************
def get_Image(soup):
    image_url = ""
    images = soup.find_all('img')
    if len(images) > 0:
        for i in range(len(images)):
            if images[i]['src'] not in VersionEventMode:
                image_url = "https://terraria.wiki.gg" + images[i]['src'] # remember to switch this depending on the wiki
            break
    return image_url


# Function to check if the page has crafting tables
# params: soup (BeautifulSoup object) - the BeautifulSoup object
# returns: craftingTables (bool) - True if the page has crafting tables, False otherwise
def has_CraftingTables(soup: BeautifulSoup) -> bool:
    craftingTables = False
    Headers = soup.find_all('h2')
    for i in range(len(Headers)):
        if Headers[i].find('span', id="Crafting"):
            craftingTables = True
            break
    return craftingTables


# Function to check if the page has a Recipe table
# params: soup (BeautifulSoup object) - the BeautifulSoup object
# returns: Recipes (bool) - True if the page has a Recipe table, False otherwise
def has_Recipes(soup: BeautifulSoup) -> bool:
    Recipes = False
    if has_CraftingTables(soup):
        Headers = soup.find_all('h3')
        for i in range(len(Headers)):
            if Headers[i].find('span', id="Recipes"):
                Recipes = True
                break
    return Recipes


# Function to check if the page has a Used in table
# params: soup (BeautifulSoup object) - the BeautifulSoup object
# returns: UsedIn (bool) - True if the page has a Used in table, False otherwise
def has_UsedIn(soup: BeautifulSoup) -> bool:
    UsedIn = False
    if has_CraftingTables(soup):
        Headers = soup.find_all('h3')
        for i in range(len(Headers)):
            if Headers[i].find('span', id="Used_in"):
                UsedIn = True
                break
    return UsedIn


# Function to get the crafting results
# params:
#         tableRow (BeautifulSoup object) - the table row currently on
#         oldgen (bool) - True if the item is from Old-gen console version, False otherwise
#         item (BeautifulSoup object) - the Result item currently on
#         resultAmount (BeautifulSoup object) - the result amount of the item
# returns:
#         ResultString (str) - the result of the item
#         oldgen (bool) - updated version of the item
#         item (BeautifulSoup object) - updated version of the item
#         resultAmount (BeautifulSoup object) - updated version of the item
def get_Results(tableRow: BeautifulSoup, oldgen: bool, item: BeautifulSoup, resultAmount: BeautifulSoup) -> Tuple[str, bool, BeautifulSoup, BeautifulSoup]:
    ResultString = ""
    result = tableRow.find('td', class_='result')

    if result: 
        oldgen = False
        item = result.find('a', class_='mw-selflink selflink')
        if not item:
            item = result.find('a', class_='mw-redirect')
            if not item:
                item = result.find('span', class_='i multi-line').find('span').find('span')
        itemVersion = result.find('a', title='Old-gen console version')
        if itemVersion:
            oldgen = True
        resultAmount = result.find('span', class_='am')
    if tableRow.find('td', class_="ingredients"):
        ResultString += "\n" + item.get_text() + " "
        if resultAmount:
            ResultString += "x" + resultAmount.get_text() + " "
        ResultString += "= "
    return ResultString, oldgen, item, resultAmount

# Function to get the crafting ingredients
# params: 
#         tableRow (BeautifulSoup object) - the table row currently on
#         item (BeautifulSoup object) - the Result item currently on
#         resultAmount (BeautifulSoup object) - the result amount of the item
# returns: 
#         IngredientsString (str) - the ingredients of the item
def get_Ingredients(tableRow: BeautifulSoup) -> str:
    Ingredients = tableRow.find('td', class_="ingredients")
    IngredientsString = ""
    if Ingredients:
        Items = Ingredients.find_all('li')
        for k in range(len(Items)):
            ItemsA = Items[k].find_all('a')
            for l in range(len(ItemsA)):
                IngredientsString += ItemsA[l].get_text()
            Amount = Items[k].find('span', class_='am')
            if Amount:
                IngredientsString += " x" + Amount.get_text()
            else:
                IngredientsString += " x1"
            if k+1 < len(Items):
                IngredientsString += " + "
    return IngredientsString


# Function to get the crafting station(s)
# params: tableRow (BeautifulSoup object) - the table row currently on
# returns: StationString (str) - the crafting station(s) of the item
def get_Station(tableRow: BeautifulSoup, StationString: str) -> str:
    StationExist = tableRow.find('td', class_="station")
    if StationExist:
        StationString = ""
        StationAmount = StationExist.find_all('span', class_='i')
        if StationAmount:
            StationString += " at "
            for k in range(len(StationAmount)):
                StationString += StationAmount[k].find('span').find('span').get_text()
                if k+1 < len(StationAmount):
                    StationString += " or "
            
        else: 
            StationString = " " + StationExist.get_text()
    return StationString


# Function to get the Recipe table
# params: 
#        tables (BeautifulSoup object) - the table currently on
#        crafting (str) - the crafting of the item
# returns:
#        crafting (str) - updated version of the crafting of the item
def get_Recipes(tables: BeautifulSoup) -> str:
    oldgen = False
    item = None
    resultAmount = None
    StationString = ""
    crafting = "Recipe:\n"
    tableRow = tables.find_all('tr')
    for j in range(len(tableRow)):
       
        # Get the item name and version
        newcrafting = ""
        newcrafting, oldgen, item, resultAmount = get_Results(tableRow[j], oldgen, item, resultAmount)
        crafting += newcrafting
        
        # Get the ingredients
        crafting += get_Ingredients(tableRow[j])

        # Get the crafting station(s)
        StationString = get_Station(tableRow[j], StationString)
        crafting += StationString

        # Add the version difference if the item is from Old-gen console version
        if oldgen:
                crafting += " " + VersionDifference[1]

    return crafting


# Function to get the Used in table
# params:
#        tables (BeautifulSoup object) - the table currently on
#        crafting (str) - the crafting of the item
# returns:
#        crafting (str) - updated version of the crafting of the item
def get_UsedIn(tables: BeautifulSoup) -> str:
    oldgen = False
    item = None
    resultAmount = None
    StationString = ""
    crafting = "Used in:\n"
    tableRow = tables.find_all('tr')
    for j in range(len(tableRow)):
        
        # Get the item name and version
        newcrafting = ""
        newcrafting, oldgen, item, resultAmount = get_Results(tableRow[j], oldgen, item, resultAmount)
        crafting += newcrafting

        # Get the ingredients
        crafting += get_Ingredients(tableRow[j])

        # Get the crafting station(s)
        StationString = get_Station(tableRow[j], StationString)
        crafting += StationString

        # Add the version difference if the item is from Old-gen console version
        if oldgen:
                crafting += " " + VersionDifference[1]

    return crafting


# Function to get the crafting tables
# params: soup (BeautifulSoup object) - the BeautifulSoup object
# returns: crafting (str) - the crafting of the item
def get_Crafting(soup: BeautifulSoup) -> str:
    crafting = ""
    Recipes1 = True # To get the Recipe only once
    craftingTables = has_CraftingTables(soup)
    Recipes = has_Recipes(soup)
    UsedIn = has_UsedIn(soup)
    if craftingTables:
        tables = soup.find_all('table', class_="recipes") 
        if len(tables) > 0:
            for i in range(len(tables)):
                if Recipes and Recipes1:
                    crafting += get_Recipes(tables[i])
                    Recipes1 = False    

                elif UsedIn:
                    if not Recipes1:
                        crafting += "\n\n"
                    crafting += get_UsedIn(tables[i])

    return crafting


# Function to get the Obtained From table
def get_ObtainedFrom(soup: BeautifulSoup) -> str:
    obtainedFrom = ""
    tables = soup.find_all('table', class_="obtainedfrom")
    if len(tables) > 0:
        for i in range(len(tables)):
            tableRow = tables[i].find_all('tr')
            for j in range(len(tableRow)):
                tableHeader = tableRow[j].find('th')
                tableData = tableRow[j].find_all('td')
                if len(tableHeader) > 0 and len(tableData) > 0:
                    obtainedFrom += tableHeader.get_text() + ": "  # Table Header
                    for k in range(len(tableData)):
                        if tableHeader.get_text() == "Dropped by":
                            tableDataA = tableData[k].find_all('a')
                            for l in range(len(tableDataA)):
                                obtainedFrom += tableDataA[l].get_text() # Dropped by
                                if l+1 < len(tableDataA):
                                    obtainedFrom += " / "
                        elif tableHeader.get_text() == "Found in":
                            tableDataA = tableData[k].find_all('a')
                            for l in range(len(tableDataA)):
                                obtainedFrom += tableDataA[l].get_text() # Found in
                                if l+1 < len(tableDataA):
                                    obtainedFrom += " / "
                        else:
                            obtainedFrom += tableData[k].get_text() + " " # Rest of Table data
                    obtainedFrom += "\n"
    return obtainedFrom


# Function to format the search term
# params: search (str) - the search term
# returns: search (str) - the formatted search term
def format_Search(search: str):
    # Exception Words that need to be capitalized differently
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

    # Capitalize the first letter of each word in the search term except for "of", "the", and "'s"
    search = search.title()
    if search not in ExceptionWords:
        search = search.replace("Of", "of").replace("The", "the").replace("'S", "'s")

    # Lowercase the second word if it is in the Mechanics list
    if search in LowercaseWords:
        search = search.lower()

    # Replace spaces with underscores
    searchForUrl = search.replace(" ", "_")

    return search, searchForUrl


# Function to fetch the Terraria wiki page
# params:
#        interaction (discord.Interaction) - the Discord interaction
#        search (str) - the search term
# returns:
#        html_content (str) - the HTML content of the page
async def fetch_Terraria_Page(interaction: discord.Interaction, search: str):
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
        return

    # Extract the HTML
    html_content = response.json().get("parse", {}).get("text", {}).get("*")

    return html_content


# Function to perform the search
# params:
#        interaction (discord.Interaction) - the Discord interaction
#        search (str) - the search term
async def perform_search(interaction: discord.Interaction, search: str):
    # Format the search term
    search, searchForUrl = format_Search(search)

    # Make a request to the Terraria wiki API
    html_content = await fetch_Terraria_Page(interaction, search)

    if not html_content:
        # If no page is found, get suggestions
        suggested_page = suggestions(search)
        if suggested_page:
            # If there's a suggestion, perform the search with the first suggestion
            await perform_search(interaction, suggested_page)
        else:
            await interaction.followup.send("No suggestions found.")
        return

    # Switched from htmlparser to BeautifulSoup for better parsing
    soup = BeautifulSoup(html_content, 'html.parser')

    # Retrieve different sections of the wiki page # Currently for Debugging
    Description = get_Description(soup)
    Types = get_Types(soup)
    Statistics = get_Statistics(soup)
    image_url = get_Image(soup)
    CraftingTables = has_CraftingTables(soup)
    Recipes = has_Recipes(soup)
    UsedIn = has_UsedIn(soup)
    crafting = get_Crafting(soup)
    obtainedFrom = get_ObtainedFrom(soup)

    # Prepare the content to send
    text_content = Statistics
    print(text_content)

    # Truncate the message if it's too long for Discord
    if len(text_content) > 2000:
        text_content = text_content[:1800] + "...\nContent too long. Please check the wiki for more details."
    
    # Send the image and content to the Discord interaction
    await interaction.followup.send(image_url + '\n' + text_content)


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
    # Defer the response to avoid the 3-second timeout limit on Discord
    await interaction.response.defer()
    
    # Perform the search using the helper function
    await perform_search(interaction, search)

client.run(os.getenv('TOKEN'))
