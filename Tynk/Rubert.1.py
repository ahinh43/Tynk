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

        
#Cluster project

controlServerID = '226835458552758275'
controlServerChannel = '322466466479734784'
robertID = '463099621225529345'


@client.event
async def on_message(message):
    if message.content.lower().startswith('rubert.eval'):
        if message.author.id == '153273725666590720':
            userstr = message.content
            userstr = userstr.replace("rubert.eval", "")
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
    elif message.content.lower() == 'rubert.shutdown':
        if message.author.id == '153273725666590720':
            await client.send_message(client.get_channel('322466466479734784'), 'Rubert is {}'.format(client.get_server('226835458552758275').roles[25].mention))
            await client.logout()
        else:
            await client.send_message(message.channel, 'CANT LET YOU DO THAT, STARFOX.')
    elif message.content.lower() == 'rubert.setactive':
        if message.author.id == '153273725666590720':
            wr = open('activeNode.txt', 'w')
            wr.seek(0)
            wr.truncate()
            wr.write('1')
            wr.close()
            await client.send_message(client.get_channel(controlServerChannel), 'Set as active node.')
            await client.change_presence(game=discord.Game(name='Cluster status: Active Node', status=discord.Status.online))
        else:
            await client.send_message(message.channel, 'CANT LET YOU DO THAT, STARFOX.')
    elif message.content.lower() == 'robert.setactive':
        if message.author.id == '153273725666590720':
            await client.send_message(client.get_channel(controlServerChannel), 'Rubert activated as active node. Setting status to failover...')
            await client.change_presence(game=discord.Game(name='Cluster status: Failover Node', status=discord.Status.online))
        else:
            await client.send_message(message.channel, 'CANT LET YOU DO THAT, STARFOX.')
    elif message.content.lower() == 'tynk.shutdown':
        if message.author.id == '153273725666590720':
            await client.send_message(client.get_channel('322466466479734784'), 'Robert is {}'.format(client.get_server('226835458552758275').roles[25].mention))
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
    global robertID
    alertRole = discord.utils.get(client.get_server(controlServerID).roles, id='385962440397160448') 
    print (before.id)
    if before.id in clusteredBots or before.id == robertID:
        with open('activeNode.txt') as f:
            activeNode = f.readline()
        f.close()
        print ('VERBOSE: ' + activeNode)
        print ('VERBOSE: ' + str(before.status))
        print ('VERBOSE: ' + str(after.status))
        # Robert is down, and the active node is set to Robert (2)
        # Wait for Robert to come online. If no go, set activeNode to 1 and start the bot.
        if client.get_server(controlServerID).get_member(robertID).status != 'online' and activeNode == '2' and str(before.status) == 'online' and str(after.status) != 'online' and before.id != robertID:
            await client.send_message(client.get_channel(controlServerChannel), 'Robert is offline, waiting to see if Robert will come back online...')
            for index in range (0,10):
                if str(client.get_server(controlServerID).get_member(robertID).status) == 'online':
                    await client.send_message(client.get_channel(controlServerChannel), 'Robert node has come back online. Standing by as failover...')
                    break
                elif index == 9:
                    await client.send_message(client.get_channel(controlServerChannel), '{} Robert has failed to come back online. Starting Bot(s)...'.format(alertRole.mention))
                    wr = open('activeNode.txt', 'w')
                    wr.seek(0)
                    wr.truncate()
                    wr.write('1')
                    wr.close()
                    for index in range(len(clusteredBots)):
                        print (str(index))
                        print ('VERBOSE: ' + clusteredBots[index])
                        try:
                            if str(client.get_server(controlServerID).get_member(clusteredBots[index]).status) == 'online':
                                print ('VERBOSE: ' + clusteredBots[index])
                                pass
                            elif str(client.get_server(controlServerID).get_member(clusteredBots[index]).status) != 'online':
                                botFile = serverMatch.get_botFile(clusteredBots[index])
                                for index in range(len(botDictionary)):
                                    #if botDictionary[index] in botFile:
                                    try:
                                        os.startfile (botFile)
                                        break
                                    except Exception as e:
                                        await client.send_message(client.get_channel(controlServerChannel), '{}'.format(alertRole.mention) + ' Unable to restart {}. Error has been logged to console.'.format(before.name))
                                        print('Unable to start bot file.')
                                        print(e)
                                        break
                                    #else:
                                    # print ('Unable to get bot from the ID.')
                            else:
                                await client.send_message(client.get_channel(controlServerChannel), '{}'.format(alertRole.mention) + ' Unable to find Bot {} based on the ID provided. Is the Bot properly set up in the cluster?'.format(before.name))
                        except Exception as e:        
                            print('A status or identification error has occurred.')
                            print(e)
                    await client.change_presence(game=discord.Game(name='Cluster status: Active Node', status=discord.Status.online))
                else:
                    print ('Iteration ' + str(index) + ' has been reached.')
                    await asyncio.sleep(3)
        # Rubert is on and the bot goes down? eh. Leave it. The other node should be handling it.
        elif client.get_server(controlServerID).get_member(robertID).status == 'online' and activeNode == '1':
            pass
        elif before.id == robertID and str(before.status) == 'online' and str(after.status) != 'online':
            await client.send_message(client.get_channel(controlServerChannel), '{} Robert node has gone offline.'.format(alertRole.mention))
            if activeNode != '1':
                for i in range (0,10):
                    if str(client.get_server(controlServerID).get_member(robertID).status) == 'online':
                        print ('Rubert node has came back online. Maintaining Failover status')
                        break
                    else:
                        print ('Iteration ' + str(i) + ' has been reached.')
                        await asyncio.sleep(3)
                    if i == 5:
                        await client.send_message(client.get_channel(controlServerChannel), '{} Rubert hasn''t returned online for a while. Taking over as active node.'.format(alertRole.mention))
                        wr = open('activeNode.txt', 'w')
                        wr.seek(0)
                        wr.truncate()
                        wr.write('1')
                        wr.close()
                        await client.change_presence(game=discord.Game(name='Cluster status: Active Node', status=discord.Status.online))
                        break
        # if the active node mode is 1, this bot is responsible for the uptime of the bots.    
        elif activeNode == '1' and str(before.status) == 'online' and str(after.status) != 'online':
            await client.send_message(client.get_channel(controlServerChannel), '{}'.format(alertRole.mention) + ' {} has went down. Attempting restart of bot.'.format(before.name))
            for index in range(len(clusteredBots)):
                print (str(index))
                print ('VERBOSE: ' + clusteredBots[index])
                try:
                    if str(client.get_server(controlServerID).get_member(clusteredBots[index]).status) == 'online':
                        print ('VERBOSE: ' + clusteredBots[index])
                        pass
                    elif str(client.get_server(controlServerID).get_member(clusteredBots[index]).status) != 'online':
                        botFile = serverMatch.get_botFile(clusteredBots[index])
                        for index in range(len(botDictionary)):
                            #if botDictionary[index] in botFile:
                            try:
                                os.startfile (botFile)
                                break
                            except Exception as e:
                                await client.send_message(client.get_channel(controlServerChannel), '{}'.format(alertRole.mention) + ' Unable to restart {}. Error has been logged to console.'.format(before.name))
                                print('Unable to start bot file.')
                                print(e)
                                break
                    else:
                        await client.send_message(client.get_channel(controlServerChannel), '{}'.format(alertRole.mention) + ' Unable to find Bot {} based on the ID provided. Is the Bot properly set up in the cluster?'.format(before.name))
                except Exception as e:        
                   print('A status or identification error has occurred.')
                   print(e)
        else:
            pass
    
# When the node starts, it will check the status of the bots it is responsible for.
# Check to see if the active node is on, if not then start bots and take over as active node.
# In the event that Rubert is down, it will wait 30 seconds before checking again.
# After about 10 iterations, it will start the bots on its own after checking their status.
# If Robert is online and everything is running, it will standby as failover waiting for the other node to go down.
@client.event
async def on_ready():
    global clusteredBots
    global botDictionary
    global controlServerID
    global controlServerChannel
    global robertID
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
    #print (str(client.get_server(controlServerID).get_member(robertID).status))
    print (activeNode)
    if str(client.get_server(controlServerID).get_member(robertID).status) == 'online' and str(activeNode) == '2':
        print ('Rubert is now ready\nFinished loadup in ' + time.strftime('%H hours, %M minutes, %S seconds', time.gmtime(loadupTime)) + '\nCluster Status: Standby as Failover')
        await client.send_message(client.get_channel('322466466479734784'), 'Rubert Node is now {}'.format(onlineRole.mention) + '\nStartup time: ' + time.strftime('%H hours, %M minutes, %S seconds', time.gmtime(loadupTime)) + '\nCluster Status: Standby as Failover')
        await client.change_presence(game=discord.Game(name='Cluster status: Failover Node', status=discord.Status.online))
    elif str(client.get_server(controlServerID).get_member(robertID).status) != 'online' and activeNode == '2':
        print ('Robert is now ready\nFinished loadup in ' + time.strftime('%H hours, %M minutes, %S seconds', time.gmtime(loadupTime)) + '\nCluster Status: Awaiting Robert node to come online...')
        await client.send_message(client.get_channel('322466466479734784'), 'Rubert Node is now {}'.format(onlineRole.mention) + '\nStartup time: ' + time.strftime('%H hours, %M minutes, %S seconds', time.gmtime(loadupTime)) + '\nCluster Status: Awaiting Robert node to come online...')
        for i in range (0,10):
            if str(client.get_server(controlServerID).get_member(robertID).status) == 'online':
                print ('Robert node is online, standing by as failover...')
                await client.send_message(client.get_channel('322466466479734784'), 'Robert node has come online. Setting status to failover.')
                await client.change_presence(game=discord.Game(name='Cluster status: Failover node', status=discord.Status.online))
                break
            else:
                print ('Iteration ' + str(i) + ' has been reached.')
                await asyncio.sleep(3)
            #if i == 4:
             #   await client.send_message(client.get_channel(controlServerChannel), '{} Unable to reach Rubert! I CANT REACH RUBERT! AAAAAAAAAAA!'.format(alertRole.mention)) 
            if i == 3:
                print ('Rubert node failed to respond. Attempting bot startup process...')
                await client.send_message(client.get_channel(controlServerChannel), '{} Failed to reach Rubert node. Checking for existing bot status...'.format(alertRole.mention))
                wr = open('activeNode.txt', 'w')
                wr.seek(0)
                wr.truncate()
                wr.write('1')
                wr.close()
                for index in range(len(clusteredBots)):
                    print (str(index))
                    print ('VERBOSE: ' + clusteredBots[index])
                    if str(client.get_server(controlServerID).get_member(clusteredBots[index]).status) == 'online':
                        print ('VERBOSE: ' + clusteredBots[index])
                        pass
                    elif str(client.get_server(controlServerID).get_member(clusteredBots[index]).status) != 'online':
                        botFile = serverMatch.get_botFile(clusteredBots[index])
                        for index in range(len(botDictionary)):
                            #if botDictionary[index] in botFile:
                            try:
                                os.startfile (botFile)
                                break
                            except:
                                print('Unable to start bot file.')
                                break
                            #else:
                            # print ('Unable to get bot from the ID.')
                    else:
                        print('Error bamboo. Something has gone terribly wrong.')
                print('Bot startup process is complete, or the bots are already online.')
                await client.change_presence(game=discord.Game(name='Cluster status: Active Node', status=discord.Status.online))
    elif activeNode == '1':
        print ('Rubert is now ready\nFinished loadup in ' + time.strftime('%H hours, %M minutes, %S seconds', time.gmtime(loadupTime)) + '\nCluster Status: Set as primary node. Running bots if they are not already online.')
        await client.send_message(client.get_channel('322466466479734784'), 'Rubert Node is now {}'.format(onlineRole.mention) + '\nStartup time: ' + time.strftime('%H hours, %M minutes, %S seconds', time.gmtime(loadupTime)) + '\nCluster Status: Set as active node.')
        for index in range(len(clusteredBots)):
            print (str(index))
            print ('VERBOSE: ' + clusteredBots[index])
            if str(client.get_server(controlServerID).get_member(clusteredBots[index]).status) == 'online':
                print ('VERBOSE: ' + clusteredBots[index])
                pass
            elif str(client.get_server(controlServerID).get_member(clusteredBots[index]).status) != 'online':
                botFile = serverMatch.get_botFile(clusteredBots[index])
                for index in range(len(botDictionary)):
                    #if botDictionary[index] in botFile:
                    try:
                        os.startfile (botFile)
                        break
                    except:
                        print('Unable to start bot file.')
                        break
                    #else:
                    # print ('Unable to get bot from the ID.')
            else:
                print('Error bamboo. Something has gone terribly wrong.')
        print('Bot startup process is complete, or the bots are already online.')
        await client.change_presence(game=discord.Game(name='Cluster status: Active Node', status=discord.Status.online))
    print('------')
client.run('NDYzMDk5NzE5NjkwODc4OTg3.DhyOxg.9JKHfYdIfswfr9EgPhepqc8RS1Y')