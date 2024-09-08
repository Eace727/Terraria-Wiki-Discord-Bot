import discord
import os
from discord.ext import commands
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup

# Dictionary for Rarity of Items
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
# returns: None
def suggestions(search):
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

    if suggestions:
        for suggestion in suggestions:
            print(f" - {suggestion['title']}")
    else:
        print("No suggestions found.")


# Function to get the description of the page
# params: soup (BeautifulSoup object) - the BeautifulSoup object
# returns: Description (str) - the description of the page
def get_Description(soup):
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
def get_Types(soup):
    types = ""
    tables = soup.find_all('table', class_="stat")
    if len(tables) > 0:
        temp = tables[0].find_all('span', class_="nowrap tag")
        for i in range(len(temp)):
            types += temp[i].get_text() + "\n"
    return types


# Function to get the statistics of the item
# params: soup (BeautifulSoup object) - the BeautifulSoup object
# returns: statistics (str) - the statistics of the item
def get_Statistics(soup):
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
                            statistics += tableDataA[l].get_text() + " " # Types
                    elif tableHeader.get_text() == "Rarity":
                        statistics += Rarity[tableData[k].get_text()] + " "
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
                    else:
                        statistics += tableData[k].get_text() + " " # Rest of Table data
            statistics += "\n"
    return statistics


# Fix/Improve Function to get the image of the item****************************
def get_Image(soup):
    image_url = ""
    images = soup.find_all('img')
    if len(images) > 0:
        for i in range(len(images)):
            if images[i]['src'] not in VersionEventMode:
                image_url = "https://terraria.wiki.gg" + images[i]['src']
            break
    return image_url


# Function to check if the page has crafting tables
# params: soup (BeautifulSoup object) - the BeautifulSoup object
# returns: craftingTables (bool) - True if the page has crafting tables, False otherwise
def has_CraftingTables(soup):
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
def has_Recipes(soup):
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
def has_UsedIn(soup):
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
# returns:
#         item (BeautifulSoup object) - the result item currently on
#         oldgen (bool) - True if the item is from Old-gen console version, False otherwise
#         resultAmount (BeautifulSoup object) - the amount of the result item
def get_Results(tableRow, oldgen, item, resultAmount):
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
def get_Ingredients(tableRow):
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
def get_Station(tableRow, StationString):
    StationExist = tableRow.find('td', class_="station")
    if StationExist:
        StationAmount = StationExist.find_all('span', class_='i')
        if StationAmount:
            StationString += " at "
            for k in range(len(StationAmount)):
                StationString += StationAmount[k].find('span').find('span').get_text()
                if k+1 < len(StationAmount):
                    StationString += " or "
            
        else: 
            StationString += " " + StationExist.get_text()
    return StationString


# Function to get the Recipe table
# params: 
#        tables (BeautifulSoup object) - the table currently on
#        crafting (str) - the crafting of the item
# returns:
#        crafting (str) - updated version of the crafting of the item
def get_Recipes(tables):
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
def get_UsedIn(tables):
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
def get_Crafting(soup):
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

    search = search.replace(" ", "_")

    # Make a request to the Terraria wiki API
    response = requests.get(url, params=params)

    # Check if the request was successful
    if response.status_code != 200:
        await interaction.followup.send(f"Error fetching page: {response.status_code}")

    # Extract the HTML and Image content
    html_content = response.json().get("parse", {}).get("text", {}).get("*")


    if not html_content:
        suggestions(search)
    else:
        # Switched from htmlparser to Beautiful soup for better parsing
        soup = BeautifulSoup(html_content, 'html.parser')
        text_content = ""
        
        Description = get_Description(soup)
        Types = get_Types(soup)
        Statistics = get_Statistics(soup)
        image_url = get_Image(soup)
        CraftingTables = has_CraftingTables(soup)
        Recipes = has_Recipes(soup)
        UsedIn = has_UsedIn(soup)
        crafting = get_Crafting(soup)

        
        text_content = crafting
        print (text_content)

        # Truncate the message if it's too long for Discord
        if len(text_content) > 2000:
            text_content = text_content[:1800] + "...\nContent too long. Please check the wiki for more details."
    
        await interaction.followup.send(image_url + '\n'+ text_content)

client.run(os.getenv('TOKEN'))
