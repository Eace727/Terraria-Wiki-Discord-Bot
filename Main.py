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

#Creating a button
#Basically inheriting ButtonView from discord.ui.View
class ButtonView(discord.ui.View):
    #calls init from ButtonView
    def __init__(self):
        #this lines ensures that init from discord.ui is also called
        super().__init__()

    #Creating the actual button itself
    @discord.ui.button(label="Button 1", style=discord.ButtonStyle.primary)
    async def button1_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        #Ephemeral dictates whether or not the response is visible to all or just button clicker (False for all, True for just button clicker)
        await interaction.response.send_message("Hooray!!!!", ephemeral=False)




# Welcome Message to test embeds
@client.tree.command(name="welcome-boogaloo", description="It's a welcomeer message")
async def welcome(interaction: discord.Interaction):
    #Create the embed
    embed = discord.Embed(
        title="Welcome to the server crodie",
        description="epic embed success",
        color=discord.Color.green()
    )
    #sets up fields and footer this is NOT in the embed thing above
    embed.add_field(name="Field 1,", value="Value 1", inline=True)
    embed.add_field(name="Field 2,", value="Value 2", inline=True)
    embed.set_image(url="https://i1.sndcdn.com/artworks-C6yjsFe6xHn2Edqk-dLKqOA-t500x500.jpg")
    embed.set_footer(text="I love feet!")

    #make a button/view
    view = ButtonView()
    #for posting the embed just copy this for a new embed
    await interaction.response.send_message(embed=embed, view=view)

# searches the terraria wiki for the given search term
@client.tree.command(name="search", description="search the terraria wiki")
async def search_wiki(interaction: discord.Interaction, search: str):
    url = "https://terraria.wiki.gg/api.php"
    
    params = {
        "action": "query",
        "format": "json",
        "list": "search",
        "srsearch": search
    }

    response = requests.get(url, params=params)
    data = response.json()

    if data["query"]["search"]:
        # Retrieve the first search result
        result = data["query"]["search"][0]
        title = result["title"]
        snippet = result["snippet"]

        # Format the response message
        message = f"**{title}**\n{snippet}..."
    else:
        message = "No results found."

    await interaction.response.send_message(message)


client.run(os.getenv('TOKEN'))
