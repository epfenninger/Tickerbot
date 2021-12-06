import discord
import nasdaq
import tableImage as ti
import traceback

client = discord.Client()
myid = ""

def tableToPicture(df):
  f = ti.render_mpl_table(df,header_columns=0, col_width=2.0) 
  picture = discord.File(f, filename="table.png")
  return picture




@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$'):
      try:
        orig = message
        #Gets rid of the $ sign
        orig = orig.content.replace('$','')
        print(orig)
        
        if orig == 'help':
          help = '$ticker - Gets most recent price \n $ticker ratio - gets the Put/Call ratios for OI and Volume \n $ticker tutes - gets institutional holders \n $ticker major - gets major holders \n $ticker analyst - gets analyst positions \n $ticker chain - gets the options chain'
          await message.channel.send(help)
        elif ' ' in orig:
          orig = orig.split(' ')
          if orig[1] == 'ratio':
            await message.channel.send("OI PC Ratio is: " + str(nasdaq.pc_ratio_oi(orig[0])) + " Volume PC Ratio is: " + str(nasdaq.pc_ratio_volume(orig[0])))
          elif orig[1] == 'tutes':
            await message.channel.send(nasdaq.tuteHolders(orig[0]))
          elif orig[1] == 'major':
            await message.channel.send(nasdaq.majorHolders(orig[0]))
          elif orig[1] == 'analyst':
            await message.channel.send(nasdaq.analysts(orig[0]))
          elif orig[1] == 'chain':
            await message.channel.send(file=tableToPicture(nasdaq.getChain(orig[0],1)))
        else:        
         await message.channel.send(nasdaq.getTicker(orig))
      except KeyError as err:
        print(err)
        print("KeyError - That isn't a ticker (I Think). If I'm wrong talk to @Dekkars")
      except Exception as e:
        await message.channel.send(e + " That isn't a valid ticker. If i'm wrong talk to " + myid+". Type $help for help")

client.run('secrets!')
