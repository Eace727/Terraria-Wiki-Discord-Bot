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
    "💻" ,
    "🎮",
    "📱",
    "🕹",
    "🖊"
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
    # Return the first suggestion (if available)
    return suggestions[0]['title'] if suggestions else None


def get_Version(item: BeautifulSoup) -> str:
    version = ""
    if item.find('div', class_="version-note"):
        if item.find('a', title="Desktop version"):
            version += VersionDifference[0]
        if item.find('a', title="Console version"):
            version += VersionDifference[1]
        if item.find('a', title="Mobile version"):
            version += VersionDifference[2]
        if item.find('a', title="Old-gen console version"):
            version += VersionDifference[3]
        if item.find('a', title="Nintendo 3DS version"):
            version += VersionDifference[4]
    else:
        if item.find('span', class_="i1"):
            version += VersionDifference[0]
        if item.find('span', class_="i2"):
            version += VersionDifference[1]
        if item.find('span', class_="i4"):
            version += VersionDifference[2]
        if item.find('span', class_="i3"):
            version += VersionDifference[3]
        if item.find('span', class_="i5"):
            version += VersionDifference[4]
        if item.find('span', class_="eico"):
            item.find('span', class_="eico").clear()
    return version

# Function to get the description of the page
# params: soup (BeautifulSoup object) - the BeautifulSoup object
# returns: Description (str) - the description of the page
def get_Description(soup: BeautifulSoup) -> str:
    Description = ""
    paraDiv = soup.find('div', class_="mw-parser-output")
    flavorText = paraDiv.find('div', class_="flavor-text")
    if flavorText:
        Description +=flavorText.get_text().replace(" ", "***") + "\n\n"
    hatNote = paraDiv.find('div', class_="hat-note")
    if hatNote:
        Description += "*" + hatNote.get_text() + "*\n\n"
    blockQuotes = paraDiv.find('blockquote')
    if blockQuotes:
        Description += "*" + blockQuotes.get_text() + "*\n\n"
    for child in paraDiv.children:
        if child.name == 'p' and child.get_text() != "":
            if child.find_all('audio'):
                for audio in child.find_all('audio'):
                    audio.decompose()
            if child.find_all('sup'):
                for sup in child.find_all('sup'):
                    sup.decompose()
            Description += child.get_text() + "\n"
        if child.name == 'ul':
            for li in child.find_all('li'):
                if li.find('audio'):
                    li.find('audio').decompose()
                Description += "- " + li.get_text() + "\n"
        if child.next_sibling and child.next_sibling.name == 'h2':
            break
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


# Function to get the statistics of the item
# params:
#         soup (BeautifulSoup object) - the BeautifulSoup object
#         search (str) - the search term
# returns: 
#         statistics (str) - the statistics of the item
def get_Statistics(soup: BeautifulSoup, search: str) -> str:
    statistics = ""
    tables = None
    infobox = soup.find_all('div', class_="infobox item")
    for info in infobox:
        if info.find('div', class_="title"):
            if search == info.find('div', class_="title").get_text():
                tables = info.find_all('table', class_="stat")
                break
    if not tables:
        tables = soup.find_all('table', class_="stat")

    if len(tables) > 0:
        tablerow = tables[0].find_all('tr')
        for j in range(len(tablerow)):
            tableHeader = tablerow[j].find('th')
            tableData = tablerow[j].find_all('td')
            if len(tableHeader) > 0 and len(tableData) > 0:
                statistics += tableHeader.get_text() + ": "  # Table Header
                for k in range(len(tableData)):
                    if tableHeader.get_text() == "Type":    # Types
                        tableDataA = tableData[k].find_all('a')
                        for l in range(len(tableDataA)):
                            statistics += tableDataA[l].get_text() 
                            if l+1 < len(tableDataA):
                                statistics += " / "
                    elif tableHeader.get_text() == "Rarity":    # Rarity
                        tableDataA = tableData[k].find('a')
                        statistics += Rarity[tableDataA['title']] + " " 
                    elif tableHeader.get_text() == "Sell":   # Sell Price
                        tableDataA = tableData[k].find_all('span', class_="coin")
                        for l in range(len(tableDataA)):
                            tableDataCoin = tableDataA[l].find_all('span')
                            for m in range(len(tableDataCoin)):
                                coinvalues = tableDataCoin[m].get_text().split()
                                for n in range(len(coinvalues)):
                                    statistics += coinvalues[n] + " " if coinvalues[n] not in Coin else CoinDict[coinvalues[n]] + " "
                            if len(tableDataA) > 1:
                                statistics += VersionDifference[l] + " "
                    elif tableHeader.get_text() == "Tooltip":   # Tooltip
                        tableDataA = tableData[k].find('i').find('span')
                        for br in tableDataA.find_all('br'):
                            br.replace_with(' / ')
                        statistics += tableDataA.get_text()  
                    else:
                        if tableData[k].find_all('span', class_="i1"):
                            tableData[k].find('span', class_="i1").replace_with("💻🎮📱")
                        if tableData[k].find_all('span', class_="i3"):
                            tableData[k].find('span', class_="i3").replace_with("🕹🖊")
                        for br in tableData[k].find_all('br'):
                            br.replace_with(' ')
                        statistics += tableData[k].get_text() + " " # Rest of Table data
            statistics += "\n"
            statistics = statistics.replace("✔️", "✅") # Replace checkmark for better visibility on discord
    return statistics


# Function to get the image of the item or the first image on the page if the item image is not found
# params: 
#         soup (BeautifulSoup object) - the BeautifulSoup object
#         search (str) - the search term
# returns: 
#         image_url (str) - the image URL of the item
def get_Image(soup: BeautifulSoup, search: str) -> str:
    image_url = ""
    images = soup.find_all('div', class_="section images")
    for image in images:
        itemImage = image.find('img', alt=search + " item sprite")
        if itemImage:
            image_url = "https://terraria.wiki.gg" + itemImage['src']
            break
    if image_url == "":
        allImages = soup.find_all('img')
        for img in allImages:
            if img['src'] not in VersionEventMode:
                image_url = "https://terraria.wiki.gg" + img['src']
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
def get_Results(tableRow: BeautifulSoup, item: BeautifulSoup, resultAmount: BeautifulSoup, resultVersion: str) -> Tuple[str, BeautifulSoup, BeautifulSoup, str]:
    ResultString = ""
    result = tableRow.find('td', class_='result')

    if result: 
        item = result.find('a', class_='mw-selflink selflink')
        if not item:
            item = result.find('a', class_='mw-redirect')
            if not item:
                item = result.find('span', class_='i')
                if not item:
                    item = result.find('span', class_='i multi-line').find('span').find('span')
        for id in result.find_all('span', class_='id'):
            id.decompose()
        resultVersion = get_Version(result)
        resultAmount = result.find('span', class_='am')
    if tableRow.find('td', class_="ingredients"):
        ResultString += "\n" + resultVersion + item.get_text() + " "
        if resultAmount:
            ResultString += "x" + resultAmount.get_text() + " "
        ResultString += "= "
    return ResultString, item, resultAmount, resultVersion

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
            IngredientsString += " " + get_Version(Items[k])
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
                StationString += " " + get_Version(StationAmount[k])
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
def get_Recipes(soup: BeautifulSoup) -> str:
    crafting = ""
    if has_Recipes(soup):
        item = None
        resultAmount = None
        resultVersion = ""
        StationString = ""
        crafting = "Recipe:\n"
        tables = soup.find_all('table', class_="recipes")
        tableRow = tables[0].find_all('tr')
        for j in range(len(tableRow)):
        
            # Get the item name and version
            newcrafting = ""
            newcrafting, item, resultAmount, resultVersion = get_Results(tableRow[j], item, resultAmount, resultVersion)
            crafting += newcrafting
            
            # Get the ingredients
            crafting += get_Ingredients(tableRow[j])

            # Get the crafting station(s)
            StationString = get_Station(tableRow[j], StationString)
            crafting += StationString

    return crafting


# Function to get the Used in table
# params:
#        tables (BeautifulSoup object) - the table currently on
#        crafting (str) - the crafting of the item
# returns:
#        crafting (str) - updated version of the crafting of the item
def get_UsedIn(soup: BeautifulSoup) -> str:
    crafting = ""
    if has_UsedIn(soup):
        item = None
        resultAmount = None
        resultVersion = ""
        StationString = ""
        crafting = "Used in:\n"
        tables = soup.find_all('table', class_="recipes")
        tableRow = tables[1].find_all('tr') if has_Recipes(soup) else tables[0].find_all('tr')
        for j in range(len(tableRow)):
            
            # Get the item name and version
            newcrafting = ""
            newcrafting, item, resultAmount, resultVersion = get_Results(tableRow[j], item, resultAmount, resultVersion)
            crafting += newcrafting

            # Get the ingredients
            crafting += get_Ingredients(tableRow[j])

            # Get the crafting station(s)
            StationString = get_Station(tableRow[j], StationString)
            crafting += StationString

    return crafting


# Function to get the crafting tables
# params: soup (BeautifulSoup object) - the BeautifulSoup object
# returns: crafting (str) - the crafting of the item
def get_Crafting(soup: BeautifulSoup) -> str:
    crafting = ""
    craftingTables = has_CraftingTables(soup)
    Recipes = has_Recipes(soup)
    UsedIn = has_UsedIn(soup)
    if craftingTables: 
        if Recipes:
            crafting += get_Recipes(soup)

        if UsedIn:
            if Recipes:
                crafting += "\n\n"
            crafting += get_UsedIn(soup)

    return crafting


# Function to get the Obtained From table
# params: soup (BeautifulSoup object) - the BeautifulSoup object
# returns: obtainedFrom (str) - the obtained from of the item
def get_ObtainedFrom(soup: BeautifulSoup) -> str:
    obtainedFrom = ""
    dropMenu = soup.find('div', class_="drop")
    if dropMenu:
        table = dropMenu.find('table')
        if table:
            tableRow = table.find_all('tr')
            for i in range(len(tableRow)):
                tableData = tableRow[i].find_all('td')
                if tableData:
                    dropTemp = ""
                    # Item Drop Source
                    # Remove the Desktop, Console and Mobile versions span
                    if tableData[0].find('span', title="Desktop, Console and Mobile versions"):
                        tableData[0].find('span', title="Desktop, Console and Mobile versions").clear()
                    if tableData[0].find('span', class_="eico"):
                        tableData[0].find('span', class_="eico").clear()
                    # Item Drop Source Name
                    obtainedFrom += tableData[0].find('span', class_="eil").get_text() + " "
                    dropTemp += tableData[0].find('span', class_="eil").get_text() + " "
                    # Item Drop Source Note
                    if tableData[0].find('div', class_="note-text"):
                        obtainedFrom += tableData[0].find('div', class_="note-text").get_text() + " "
                        dropTemp += tableData[0].find('div', class_="note-text").get_text() + " "
                    elif tableData[0].find('span', class_="note-text"):
                        obtainedFrom += tableData[0].find('span', class_="note-text").get_text() + " "
                        dropTemp += tableData[0].find('span', class_="note-text").get_text() + " "
                    dropTemp += get_Version(tableData[0]) + " | "
                    obtainedFrom += get_Version(tableData[0]) + " | "
                    # Item Drop Amount
                    if tableData[1]:
                        obtainedFrom += tableData[1].get_text() + " | "
                        dropTemp += tableData[1].get_text() + " | "
                    # Item Drop Chance
                    if tableData[2]:
                        versionChances = False
                        oldgen = False
                        desktop = False
                        
                        # Remove version span as well as record if there is a version difference
                        if tableData[2].find('span', class_="i1") and tableData[2].find('span', class_="i3"):
                            versionChances = True
                            tableData[2].find('span', class_="i3").decompose()
                            tableData[2].find('span', class_="i1").decompose()
                        elif tableData[2].find('span', class_="i1"):
                            tableData[2].find('span', class_="i1").decompose()
                            desktop = True
                        elif tableData[2].find('span', class_="i3"):
                            tableData[2].find('span', class_="i3").decompose()
                            oldgen = True

                        # if drop source has different chances for different versions or/and modes
                        if versionChances:
                            tableData[2].find('br').replace_with('`')
                            # if drop source has different chances for different versions
                            if tableData[2].find('span', class_="m-expert-master"):
                                chances = tableData[2].span.span.get_text().split('`')
                                obtainedFrom += chances[0] + "/ " + tableData[2].find('span', class_="m-expert-master").get_text() + VersionDifference[0] + VersionDifference[1] + VersionDifference[2] + "\n"
                                obtainedFrom += dropTemp + chances[1] + "/ N/A " + VersionDifference[3] + VersionDifference[4]
                            # if drop source has different chances for different versions only
                            else:
                                chances = tableData[2].span.get_text().split('`')
                                obtainedFrom += chances[0] + "/ " + chances[0] + VersionDifference[0] + VersionDifference[1] + VersionDifference[2] + "\n"
                                obtainedFrom += dropTemp + chances[1] + "/ " + chances[1] + VersionDifference[3] + VersionDifference[4]
                        # if drop source has different chances for different modes
                        elif tableData[2].find('span', class_="mode-content"):
                            dropChance = tableData[2].find('span', class_="mode-content").find_all('span', recursive=False)
                            for j in range(len(dropChance)):
                                obtainedFrom += dropChance[j].get_text()
                                if j+1 < len(dropChance):
                                    obtainedFrom += " / "
                        # if drop source only drops in master mode
                        elif "m-master" in tableRow[i]['class']:
                            obtainedFrom += tableData[2].get_text() + " (Only Master Mode)"
                        # if drop source only drops in expert/master or normal mode
                        elif "m-normal" in tableRow[i]['class'] or "m-expert-master" in tableRow[i]['class'] :
                            obtainedFrom += tableData[2].get_text() + " / N/A" if "m-normal" in tableRow[i]['class'] else "N/A / "+ tableData[2].get_text()
                            if oldgen:
                                obtainedFrom += " " + VersionDifference[3] + VersionDifference[4]
                            if desktop:
                                obtainedFrom += " " + VersionDifference[0] + VersionDifference[1] + VersionDifference[2]
                        # if drop source has the same chances for all versions and all modes
                        else:
                            obtainedFrom += tableData[2].get_text() + " / " + tableData[2].get_text()
                            if oldgen:
                                obtainedFrom += " " + VersionDifference[3] + VersionDifference[4]
                            if desktop:
                                obtainedFrom += " " + VersionDifference[0] + VersionDifference[1] + VersionDifference[2]
                    
                obtainedFrom += "\n"
    return obtainedFrom


def has_Notes(soup: BeautifulSoup) -> bool:
    notes = False
    notesDiv = soup.find_all('h2')
    for h2 in notesDiv:
        if h2.find('span', id="Notes"):
            notes = True
            break
    return notes


def get_Notes(soup: BeautifulSoup) -> str:
    notes = ""
    if has_Notes(soup):
        notesDiv = soup.find_all('h2')
        for h2 in notesDiv:
            if h2.find('span', id="Notes"):
                note = h2
                break
        for sibling in note.next_siblings:
            if sibling.name == 'ul':
                for li in sibling.find_all('li', recursive=False):
                    for eico in li.find_all('span', class_="i1"):
                        eico.decompose()
                    for sup in li.find_all('sup'):
                        sup.decompose()
                    for rarity in li.find_all('span', class_="rarity"):
                        rarityReplacement = Rarity[rarity.find('a')['title']]
                        rarity.find('s').replace_with(rarityReplacement)
                    notesTemp = ""
                    if li.find('ul'):
                        for subli in li.find_all('li'):
                            notesTemp += "  - " + subli.get_text() + "\n"
                        li.find('ul').decompose()
                    notes += "- " + li.get_text() + notesTemp if notesTemp != "" else "- " + li.get_text() + "\n"
            if sibling.name == 'h2':
                break
    return notes


def get_Tips(soup: BeautifulSoup) -> str:
    tips = ""
    tipsDiv = soup.find('div', class_="tips")
    if tipsDiv:
        tips += tipsDiv.get_text() + "\n"
    return tips

def get_Trivia(soup: BeautifulSoup) -> str:
    trivia = ""
    triviaDiv = soup.find('div', class_="trivia")
    if triviaDiv:
        trivia += triviaDiv.get_text() + "\n"
    return trivia

def get_History(soup: BeautifulSoup) -> str:
    history = ""
    historyDiv = soup.find('div', class_="history")
    if historyDiv:
        history += historyDiv.get_text() + "\n"
    return history


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
        search = search.replace("Of ", "of ").replace("The ", "the ").replace("'S", "'s").replace("In ", "in ").replace("And ", "and ").replace("A ", "a ")

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
        if suggested_page and suggested_page != search:
            # If there's a suggestion, perform the search with the first suggestion
            await perform_search(interaction, suggested_page)
        else:
            await interaction.followup.send('No page found named: "' + search + '".\nPlease check the spelling and try again.')
        return

    # Switched from htmlparser to BeautifulSoup for better parsing
    soup = BeautifulSoup(html_content, 'html.parser')

    # Retrieve different sections of the wiki page # Currently for Debugging
    Description = get_Description(soup)
    Types = get_Types(soup)
    Statistics = get_Statistics(soup, search)
    image_url = get_Image(soup, search)
    hasCraftingTables = has_CraftingTables(soup)
    hasRecipes = has_Recipes(soup)
    hasUsedIn = has_UsedIn(soup)
    recipes = get_Recipes(soup)
    usedIn = get_UsedIn(soup)
    crafting = get_Crafting(soup)
    obtainedFrom = get_ObtainedFrom(soup)
    hasNotes = has_Notes(soup)
    notes = get_Notes(soup)

    # Prepare the content to send
    text_content = obtainedFrom
    print(text_content)

    # Truncate the message if it's too long for Discord
    if len(text_content) > 1900:
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