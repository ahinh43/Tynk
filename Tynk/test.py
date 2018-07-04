import discord
import os
import asyncio
import time

client = discord.Client()


@client.event
async def on_ready():
    print('Logged in as:')
    print(client.user.name)
    print(client.user.id)
    print('Logged into servers:')
    print('------')
    try:
        os.startfile (r'tonk.lnk')
    except:
        print('Unable to start bot file.')
    
client.run('NDYzMDk5NjIxMjI1NTI5MzQ1.Dhrfpw.VFUvRJelo6xRMZ76jdADh96FeOc')

# Requires Python 3.5 to run. Written by Tenj