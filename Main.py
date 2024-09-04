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
class SelectView(discord.ui.View):
    #calls init from ButtonView
    def __init__(self):
        #this lines ensures that init from discord.ui is also called
        super().__init__()

    #create the options
    options =[
        discord.SelectOption(label="Bruh 1", description="Bruh the first"),
        discord.SelectOption(label="Bruh 2", description="Bruh the second")
    ]
    #Creating the actual button itself
    @discord.ui.select(placeholder="Choose a bruh", options=options)

    #Used when an option is selected
    async def select_callback(self,interaction: discord.Interaction,select: discord.ui.Select):
       selected_option = select.values[0]
       #Bruh 1 option
       if selected_option == "Bruh 1":
           bruhembed = discord.Embed(
               title="Hooray!!"
           )
           bruhembed.set_image(url="https://media2.giphy.com/media/kEQIxNd2i2SSsQ6S2U/giphy.gif?cid=6c09b952fj7qzjk206t24oket0u687i47jxz38s6v8auiotb&ep=v1_internal_gif_by_id&rid=giphy.gif&ct=g")
           await interaction.response.edit_message(embed=bruhembed)
        
       #Bruh 2 option
       elif selected_option == "Bruh 2":
           oofembed = discord.Embed(
               title="Epic"
           )
           oofembed.set_image(url="https://gifdb.com/images/thumbnail/ishowspeed-closing-eyes-while-smiling-cgsdgti6o0v4oot7.gif")
           await interaction.response.edit_message(embed=oofembed)







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

    #Add the Button
    view = SelectView()
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
