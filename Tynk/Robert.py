import discord
import os
import asyncio
import time
import serverMatch
import traceback


client = discord.Client()
clusteredBots = []
# Load all the bot IDs to be clustered.
with open ('clusteredBots.txt') as f:
    clusteredBots = [line.rstrip() for line in f]
#Build the bot filename dictionary      
with open ('botDictionary.txt') as f:
    botDictionary = [line.rstrip() for line in f]



start = time.time()

        
# Constants that are uniquely used by this node
controlServerID = '226835458552758275'
controlServerChannel = '322466466479734784'
otherNodeID = '463099719690878987'
otherNode = 'Rubert'
activeNodeCode = '2'
selfNode = 'Robert'


@client.event
async def on_message(message):
    global activeNodeCode
    global selfNode
    global otherNode
    offlineRole = discord.utils.get(client.get_server(controlServerID).roles, id='370340076527288321')
    if message.content.lower().startswith(f'{selfNode.lower()}.eval'):
        if message.author.id == '153273725666590720':
            userstr = message.content
            userstr = userstr.replace(f"{selfNode.lower()}.eval", "")
            try:
                result = eval(userstr)
            except Exception:
                formatted_lines = traceback.format_exc().splitlines()
                await client.send_message(message.channel, 'Failed to Evaluate.\n```py\n{}\n{}\n```'.format(formatted_lines[-1], '/n'.join(formatted_lines[4:-1])))
                return

            if asyncio.iscoroutine(result):
                result = await result

            if result:
                await client.send_message(message.channel, 'Evaluated Successfully.\n```{}```'.format(result))
                return
        else:
            await client.send_message(message.channel, 'No.')
    elif message.content.lower() == f'{selfNode.lower()}.shutdown':
        if message.author.id == '153273725666590720':
            await client.send_message(client.get_channel('322466466479734784'), f'{selfNode} is {offlineRole.mention}')
            await client.logout()
        else:
            await client.send_message(message.channel, 'CANT LET YOU DO THAT, STARFOX.')
    elif message.content.lower() == f'{selfNode.lower()}.setactive':
        if message.author.id == '153273725666590720':
            wr = open('activeNode.txt', 'w')
            wr.seek(0)
            wr.truncate()
            wr.write(activeNodeCode)
            wr.close()
            await client.send_message(client.get_channel(controlServerChannel), 'Set as active node.')
            await client.change_presence(game=discord.Game(name='Cluster status: Active Node', status=discord.Status.online))
        else:
            await client.send_message(message.channel, 'CANT LET YOU DO THAT, STARFOX.')
    elif message.content.lower() == f'{otherNode.lower()}.setactive':
        if message.author.id == '153273725666590720':
            await client.send_message(client.get_channel(controlServerChannel), f'{otherNode} activated as active node. Setting status to failover...')
            await client.change_presence(game=discord.Game(name='Cluster status: Failover Node', status=discord.Status.online))
        else:
            await client.send_message(message.channel, 'CANT LET YOU DO THAT, STARFOX.')
    elif message.content.lower() == 'tynk.shutdown':
        if message.author.id == '153273725666590720':
            await client.send_message(client.get_channel('322466466479734784'), f'{selfNode} is {offlineRole.mention}')
            await client.logout()
        else:
            await client.send_message(message.channel, 'CANT LET YOU DO THAT, STARFOX.')

#Loop through all the bots on the list. 
@client.event
async def on_member_update(before, after):
    global clusteredBots
    global botDictionary
    global controlServerID
    global controlServerChannel
    global otherNodeID
    global otherNode
    global activeNodeCode
    alertRole = discord.utils.get(client.get_server(controlServerID).roles, id='385962440397160448') 
    if before.id in clusteredBots or before.id == otherNodeID:
        with open('activeNode.txt') as f:
            activeNode = f.readline()
        f.close()
        # Another node is down, and the active node is not this one.
        # Waits for the other node to come up. If the other node does not come up, changes activeNode to this host's code and attempts to start the bot.
        if client.get_server(controlServerID).get_member(otherNodeID).status != 'online' and activeNode != activeNodeCode and str(before.status) == 'online' and str(after.status) != 'online' and before.id != otherNodeID:
            await client.send_message(client.get_channel(controlServerChannel), f'{otherNode} is offline, waiting to see if {otherNode} will come back online...')
            for index in range (0,10):
                if str(client.get_server(controlServerID).get_member(otherNodeID).status) == 'online':
                    await client.send_message(client.get_channel(controlServerChannel), f'{otherNode} node has come back online. Standing by as failover...')
                    break
                elif index == 9:
                    await client.send_message(client.get_channel(controlServerChannel), f'{alertRole.mention} {otherNode} has failed to come back online. Starting Bot(s)...')
                    wr = open('activeNode.txt', 'w')
                    wr.seek(0)
                    wr.truncate()
                    wr.write(activeNodeCode)
                    wr.close()
                    for index in range(len(clusteredBots)):
                        try:
                            if str(client.get_server(controlServerID).get_member(clusteredBots[index]).status) == 'online':
                                pass
                            elif str(client.get_server(controlServerID).get_member(clusteredBots[index]).status) != 'online':
                                botFile = serverMatch.get_botFile(clusteredBots[index])
                                for index in range(len(botDictionary)):
                                    try:
                                        os.startfile (botFile)
                                        break
                                    except Exception as e:
                                        await client.send_message(client.get_channel(controlServerChannel), f'{alertRole.mention} Unable to restart {before.name}. Error has been logged to console.')
                                        print('Unable to start bot file.')
                                        print(e)
                                        break
                            else:
                                await client.send_message(client.get_channel(controlServerChannel), f'{alertRole.mention}' + f' Unable to find Bot {before.name} based on the ID provided. Is the Bot properly set up in the cluster?')
                        except Exception as e:        
                            print('A status or identification error has occurred.')
                            print(e)
                    await client.change_presence(game=discord.Game(name='Cluster status: Active Node', status=discord.Status.online))
                else:
                    #print ('Iteration ' + str(index) + ' has been reached.')
                    await asyncio.sleep(3)
        # The other node is on and the bot goes down? eh. Leave it. The other node should be handling it.
        elif client.get_server(controlServerID).get_member(otherNodeID).status == 'online' and activeNode != activeNodeCode:
            pass
        elif before.id == otherNodeID and str(before.status) == 'online' and str(after.status) != 'online':
            await client.send_message(client.get_channel(controlServerChannel), f'{alertRole.mention} {otherNode} node has gone offline.')
            if activeNode != '2':
                for i in range (0,10):
                    if str(client.get_server(controlServerID).get_member(otherNodeID).status) == 'online':
                        print (f'{otherNode} node has came back online. Maintaining Failover status')
                        break
                    else:
                        print ('Iteration ' + str(i) + ' has been reached.')
                        await asyncio.sleep(3)
                    if i == 5:
                        await client.send_message(client.get_channel(controlServerChannel), f'{alertRole.mention} {otherNode} hasn''t returned online for a while. Taking over as active node.')
                        wr = open('activeNode.txt', 'w')
                        wr.seek(0)
                        wr.truncate()
                        wr.write(activeNodeCode)
                        wr.close()
                        await client.change_presence(game=discord.Game(name='Cluster status: Active Node', status=discord.Status.online))
                        break
        # Case where the node is active, and is responsible for the bots.   
        elif activeNode == activeNodeCode and str(before.status) == 'online' and str(after.status) != 'online':
            await client.send_message(client.get_channel(controlServerChannel), f'{alertRole.mention}' + f' {before.name} has went down. Attempting restart of bot.')
            for index in range(len(clusteredBots)):
                try:
                    if str(client.get_server(controlServerID).get_member(clusteredBots[index]).status) == 'online':
                        pass
                    elif str(client.get_server(controlServerID).get_member(clusteredBots[index]).status) != 'online':
                        botFile = serverMatch.get_botFile(clusteredBots[index])
                        for index in range(len(botDictionary)):
                            try:
                                os.startfile (botFile)
                                break
                            except Exception as e:
                                await client.send_message(client.get_channel(controlServerChannel), f'{alertRole.mention}' + f' Unable to restart {before.name}. Error has been logged to console.')
                                print('Unable to start bot file.')
                                print(e)
                                break
                    else:
                        await client.send_message(client.get_channel(controlServerChannel), f'{alertRole.mention}' + f' Unable to find Bot {before.name} based on the ID provided. Is the Bot properly set up in the cluster?')
                except Exception as e:        
                   print('A status or identification error has occurred.')
                   print(e)
        else:
            pass
    
# When the node starts, it will check the status of the bots it is responsible for.
# If the other node is active, it will wait for that node to come online.
# If the other node does not come online within the alloted time, then it will take over as the active node then start the bots on its own.
@client.event
async def on_ready():
    global clusteredBots
    global botDictionary
    global controlServerID
    global controlServerChannel
    global otherNodeID
    global otherNode
    global activeNodeCode
    global selfNode
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    end = time.time()
    with open('activeNode.txt') as f:
        activeNode = f.readline()
        f.close()
    loadupTime = (end - start)
    onlineRole = discord.utils.get(client.get_server(controlServerID).roles, id='370337403769978880')
    alertRole = discord.utils.get(client.get_server(controlServerID).roles, id='385962440397160448')
    #print (str(client.get_server(controlServerID).get_member(otherNodeID).status))
    if str(client.get_server(controlServerID).get_member(otherNodeID).status) == 'online' and activeNode != activeNodeCode:
        print (f'{selfNode} is now ready\nFinished loadup in ' + time.strftime('%H hours, %M minutes, %S seconds', time.gmtime(loadupTime)) + '\nCluster Status: Standby as Failover')
        await client.send_message(client.get_channel(controlServerChannel), f'{selfNode} Node is now {onlineRole.mention}' + '\nStartup time: ' + time.strftime('%H hours, %M minutes, %S seconds', time.gmtime(loadupTime)) + '\nCluster Status: Standby as Failover')
        await client.change_presence(game=discord.Game(name='Cluster status: Failover Node', status=discord.Status.online))
    elif str(client.get_server(controlServerID).get_member(otherNodeID).status) != 'online' and activeNode != activeNodeCode:
        print (f'{selfNode} is now ready\nFinished loadup in ' + time.strftime('%H hours, %M minutes, %S seconds', time.gmtime(loadupTime)) + f'\nCluster Status: Awaiting {otherNode} node to come online...')
        await client.send_message(client.get_channel(controlServerChannel), f'{selfNode} Node is now {onlineRole.mention}' + '\nStartup time: ' + time.strftime('%H hours, %M minutes, %S seconds', time.gmtime(loadupTime)) + f'\nCluster Status: Awaiting {otherNode} node to come online...')
        for i in range (0,4):
            if str(client.get_server(controlServerID).get_member(otherNodeID).status) == 'online':
                print (f'{otherNode} node is online, standing by as failover...')
                await client.send_message(client.get_channel(controlServerChannel), f'{otherNode} node has come online. Setting status to failover.')
                await client.change_presence(game=discord.Game(name='Cluster status: Failover node', status=discord.Status.online))
                break
            else:
                #print ('Iteration ' + str(i) + ' has been reached.')
                await asyncio.sleep(3)
            if i == 3:
                print ('Rubert node failed to respond. Attempting bot startup process...')
                await client.send_message(client.get_channel(controlServerChannel), f'{alertRole.mention} Failed to reach {otherNode} node. Checking for existing bot status...')
                wr = open('activeNode.txt', 'w')
                wr.seek(0)
                wr.truncate()
                wr.write(activeNodeCode)
                wr.close()
                for index in range(len(clusteredBots)):
                    if str(client.get_server(controlServerID).get_member(clusteredBots[index]).status) == 'online':
                        pass
                    elif str(client.get_server(controlServerID).get_member(clusteredBots[index]).status) != 'online':
                        botFile = serverMatch.get_botFile(clusteredBots[index])
                        for index in range(len(botDictionary)):
                            try:
                                os.startfile (botFile)
                                break
                            except:
                                print('Unable to start bot file.')
                                break
                    else:
                        print('Error bamboo. Something has gone terribly wrong.')
                print('Bot startup process is complete, or the bots are already online.')
                await client.change_presence(game=discord.Game(name='Cluster status: Active Node', status=discord.Status.online))
                break
    elif activeNode == activeNodeCode:
        print (f'{selfNode} is now ready\nFinished loadup in ' + time.strftime('%H hours, %M minutes, %S seconds', time.gmtime(loadupTime)) + '\nCluster Status: Set as primary node. Running bots if they are not already online.')
        await client.send_message(client.get_channel('322466466479734784'), f'{selfNode} Node is now {onlineRole.mention}' + '\nStartup time: ' + time.strftime('%H hours, %M minutes, %S seconds', time.gmtime(loadupTime)) + '\nCluster Status: Set as active node.')
        for index in range(len(clusteredBots)):
            if str(client.get_server(controlServerID).get_member(clusteredBots[index]).status) == 'online':
                pass
            elif str(client.get_server(controlServerID).get_member(clusteredBots[index]).status) != 'online':
                botFile = serverMatch.get_botFile(clusteredBots[index])
                for index in range(len(botDictionary)):
                    try:
                        os.startfile (botFile)
                        break
                    except:
                        print('Unable to start bot file.')
                        break
            else:
                print('Error bamboo. Something has gone terribly wrong.')
        print('Bot startup process is complete, or the bots are already online.')
        await client.change_presence(game=discord.Game(name='Cluster status: Active Node', status=discord.Status.online))
    print('------')
client.run('')