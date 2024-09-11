import discord
from discord.ext import commands
import requests
import shodan
import sherlock
import os
import json
import asyncio

# Set up Discord bot token
TOKEN = 'MTI4MzA2NTU5NTkyMzAwOTUzNg.G0UlEf.fQzbi09DegLzdcxLfekg_VfgfiayiWsTeq_AM0'

# API keys for Shodan and IPInfo (Hunter.io doesn't need an API key for basic validation)
SHODAN_API_KEY = 'IKgg4gD8ijpDF8bPncE7KN3fss3t9CtK'
IPINFO_API_KEY = 'aefa9adb9f278c'

# Setting up intents for the bot to receive message content
intents = discord.Intents.default()
intents.message_content = True

# Initialize bot with command prefix
bot = commands.Bot(command_prefix='!', intents=intents)

# OSINT command to fetch info based on a Discord ID
@bot.command(name='osint', help='Performs OSINT on a user by Discord ID')
async def osint(ctx, discord_id: str):
    # Perform Hunter.io lookup
    email = f'{discord_id}@gmail.com'  # Assuming Discord ID maps to Gmail
    hunter_result = hunter_lookup(email)

    # Perform Sherlock lookup for username across platforms
    sherlock_result = await sherlock_lookup(discord_id)

    # Perform Shodan IP lookup (example IP)
    shodan_result = shodan_lookup('8.8.8.8')  # Replace with actual IP if needed

    # Perform IP Info lookup (example IP)
    ipinfo_result = ipinfo_lookup('8.8.8.8')  # Replace with actual IP if needed

    # Send the results as a response in Discord
    result_message = f"**OSINT Results for Discord ID {discord_id}:**\n\n"
    result_message += f"**Hunter.io Email Info:**\n{json.dumps(hunter_result, indent=2)}\n\n"
    result_message += f"**Sherlock Username Search:**\n{sherlock_result}\n\n"
    result_message += f"**Shodan IP Search:**\n{json.dumps(shodan_result, indent=2)}\n\n"
    result_message += f"**IPInfo IP Search:**\n{json.dumps(ipinfo_result, indent=2)}"

    await ctx.send(result_message)

# Function to perform Hunter.io email lookup
def hunter_lookup(email):
    url = f"https://api.hunter.io/v2/email-verifier?email={email}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Error occurred: {response.status_code}"}

# Function to perform Shodan IP lookup
def shodan_lookup(ip):
    api = shodan.Shodan(SHODAN_API_KEY)
    try:
        result = api.host(ip)
        return result
    except shodan.APIError as e:
        return str(e)

# Function to perform IPInfo lookup
def ipinfo_lookup(ip):
    url = f"https://ipinfo.io/{ip}/json?token={IPINFO_API_KEY}"
    response = requests.get(url)
    return response.json()

# Function to perform Sherlock username lookup
async def sherlock_lookup(username):
    # Run Sherlock to search for the username across platforms
    result_dir = f'./sherlock_results/{username}'
    os.makedirs(result_dir, exist_ok=True)

    # Run Sherlock asynchronously
    await sherlock.sherlock(username, result_dir)

    # Read the results
    result_file = os.path.join(result_dir, f'{username}.txt')
    if os.path.exists(result_file):
        with open(result_file, 'r') as f:
            return f.read()
    else:
        return "No results found."

# Run the bot
bot.run(TOKEN)
