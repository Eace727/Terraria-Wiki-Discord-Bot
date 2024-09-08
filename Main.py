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



    if html_content:
        # Switched from htmlparser to Beautiful soup for better parsing
        soup = BeautifulSoup(html_content, 'html.parser')
        text_content = ""

        # Get the first or all paragraphs of the page
        Description = ""
        paraDiv = soup.find('div', class_="mw-parser-output")
        paragraphs = paraDiv.find_all('p', recursive=False)
        if len(paragraphs) > 0:
            for i in range(len(paragraphs)):
                if paragraphs[i].get_text() != "": 
                    Description += paragraphs[i].get_text() + "\n"

        # Get the types of the item if it is an item
        types = ""
        tables = soup.find_all('table', class_="stat")
        if len(tables) > 0:
            temp = tables[0].find_all('span', class_="nowrap tag")
            for i in range(len(temp)):
                types += temp[i].get_text() + "\n"

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
        
        # Coin Values
        Coin = [
            "CC",
            "SC",
            "GC",
            "PC",
        ]

        # Coin Dictionary for Coin Values
        CoinDict = {
            "CC" : "Copper Coin(s)",
            "SC" : "Silver Coin(s)",
            "GC" : "Gold Coin(s)",
            "PC" : "Platinum Coin(s)",
        }

        VersionDifference = [
            "(Desktop, Console and Mobile versions) /" ,
            "(Old-gen console and 3DS versions) ",
        ]

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

        # Get the image URL

        # Get the first image that is not a version/event/mode image
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
        
        image_url = ""
        images = soup.find_all('img')
        if len(images) > 0:
            for i in range(len(images)):
                 if images[i]['src'] not in VersionEventMode:
                    image_url = "https://terraria.wiki.gg" + images[i]['src']
                    break
        
        # Check if there are crafting tables
        craftingTables = False
        Headers = soup.find_all('h2')
        for i in range(len(Headers)):
            if Headers[i].find('span', id="Crafting"):
                craftingTables = True
                break

        # Check if it has a Recipe and/or Used in table
        Recipes = False
        UsedIn = False
        if craftingTables:
            Headers = soup.find_all('h3')
            for i in range(len(Headers)):
                if Headers[i].find('span', id="Recipes"):
                    Recipes = True
                elif Headers[i].find('span', id="Used_in"):
                    UsedIn = True
                if Recipes and UsedIn:
                    break


        # Get the crafting recipe / Used in if it is an item

        VersionNames = [
            "(only: Desktop, Console and Mobile versions)",
            "(only: Old-gen console and 3DS versions)",
        ]

        
        crafting = ""
        Recipes1 = True # To get the Recipe only once
        StationString = ""
        if craftingTables:
            tables = soup.find_all('table', class_="recipes")
            if len(tables) > 0:
                for i in range(len(tables)):
                    if Recipes and Recipes1:
                        crafting += "Recipe:\n"
                        tableRow = tables[i].find_all('tr')
                        for j in range(len(tableRow)):
                            
                            
                            result = tableRow[j].find('td', class_='result')
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
                            
                            Ingredients = tableRow[j].find('td', class_="ingredients")
                            if Ingredients:
                                crafting += "\n" + item.get_text() + " "
                                if resultAmount:
                                    crafting += "x" + resultAmount.get_text() + " "
                                crafting += "= "
                                Items = Ingredients.find_all('li')
                                for k in range(len(Items)):
                                    ItemsA = Items[k].find_all('a')
                                    for l in range(len(ItemsA)):
                                        crafting += ItemsA[l].get_text()
                                    Amount = Items[k].find('span', class_='am')
                                    if Amount:
                                        crafting += " x" + Amount.get_text()
                                    else:
                                        crafting += " x1"
                                    if k+1 < len(Items):
                                        crafting += " + "
                            
                            StationExist = tableRow[j].find('td', class_="station")
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
                                    StationString += " " + StationExist.get_text()
                            crafting += StationString

                            if oldgen:
                                    crafting += " " + VersionNames[1]
                                    oldgen = False

                        crafting += "\n\n"
                        StationString = "" # Reset the StationString since its the only variable in both scopes
                        Recipes1 = False    

                    elif UsedIn:
                        crafting += "Used in:\n"
                        tableRow = tables[i].find_all('tr')
                        for j in range(len(tableRow)):
                            oldgen = False
                            
                            result = tableRow[j].find('td', class_='result')
                            if result:
                                item = result.find('a', class_='mw-selflink selflink')
                                if not item:
                                    item = result.find('a', class_='mw-redirect')
                                    if not item:
                                        item = result.find('span', class_='i multi-line').find('span').find('span')
                                itemVersion = result.find('a', title='Old-gen console version')
                                if itemVersion:
                                    oldgen = True
                                resultAmount = result.find('span', class_='am')
                            
                            Ingredients = tableRow[j].find('td', class_="ingredients")
                            if Ingredients:
                                crafting += "\n" + item.get_text() + " "
                                if resultAmount:
                                    crafting += "x" + resultAmount.get_text() + " "
                                crafting += "= "
                                Items = Ingredients.find_all('li')
                                for k in range(len(Items)):
                                    ItemsA = Items[k].find_all('a')
                                    for l in range(len(ItemsA)):
                                        crafting += ItemsA[l].get_text()
                                    Amount = Items[k].find('span', class_='am')
                                    if Amount:
                                        crafting += " x" + Amount.get_text()
                                    else:
                                        crafting += " x1"
                                    if k+1 < len(Items):
                                        crafting += " + "
                            
                            StationExist = tableRow[j].find('td', class_="station")
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
                                    StationString += " " + StationExist.get_text()
                            crafting += StationString

                            if oldgen:
                                    crafting += " " + VersionNames[1]
                                    oldgen = False

    
        print (crafting)
        text_content = crafting

        # Truncate the message if it's too long for Discord
        if len(text_content) > 2000:
            text_content = text_content[:1800] + "...\nContent too long. Please check the wiki for more details."
    
        await interaction.followup.send(image_url + '\n'+ text_content)
    else:
        await interaction.followup.send("No pages found with that title or no content available.")

client.run(os.getenv('TOKEN'))
