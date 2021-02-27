import configparser
from api import API
import discord
from discord.ext import commands
import random
import datetime


def getRoom(id):
    for room in rooms:
        if room.id == int(id):
            return room
    return -1 

def getNewNumber(ids, min, max):
    id = random.randint(min,max)
    while id in ids:
        id = random.randint(min,max)
    return id


class Player:
    def __init__(self, user):
        self.user = user
        self.champion = 0
        self.reroll_count = 2

class Room:
    def __init__(self):
        self.id = getNewNumber([room.id for room in rooms], 1000, 10000)
        self.players = [[],[]]
        self.player_count = 0
        self.champions = []

    def join(self, player, team):
        if  player.user.id in [p.user.id for t in self.players for p in t]:
            player.champion = [p.champion for t in self.players for p in t if p.user.id == player.user.id][0]
            self.players = [[p for p in t if p.user.id != player.user.id] for t in self.players] 
            self.player_count -= 1
             
        else:
            champ = getNewNumber(self.champions, 0, len(api.champions))
            player.champion = champ
            self.champions.append(champ)

        self.players[team].append(player)
        self.player_count += 1


bot = commands.Bot(command_prefix='$', description="Almog's Leauge Bot", help_command=None)
rooms = []

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))

@bot.command()
async def create(ctx):
    room_ = Room()
    rooms.append(room_)    

    await ctx.send(f"room created, id: {room_.id}")
    await ShowRoom(ctx, room_.id)


@bot.command()
async def help(ctx):
    embed = discord.Embed(title=f"Help - Commands", description="---------------", timestamp=datetime.datetime.utcnow(), color=discord.Color.blue())
    
    embed.add_field(name="$create",value=f"create a room", inline=False)
    embed.add_field(name="$join <room_id> <team>",value="join room and team", inline=False)
    embed.add_field(name="$room <room_id>",value=f"shows the teams and the champions in a room", inline=False)

    await ctx.send(embed=embed)
    
@bot.command()
async def join(ctx, room_id, team):
    room_ = getRoom(room_id)
    if room_ != -1:
        player = Player(user=ctx.message.author)
        if room_.player_count == 10:
            await ctx.send(f"Room {room_id} is full")
        else:
            if int(team)>2 or int(team)<1:
                await ctx.send("Team number out of range")
            else:
                room_.join(player=player, team=int(team)-1)
                await ctx.send(f"{player.user.mention} joined room {room_id}")
                await ShowRoom(ctx, room_id)
    else:
        await ctx.send(f"Room {room_id} does not exist")


@bot.command()
async def ShowRoom(ctx, room_id):
    room = getRoom(room_id)
    if room != -1:
        embed = discord.Embed(title=f"Room {room_id}", description="---------------", timestamp=datetime.datetime.utcnow(), color=discord.Color.blue())
        
        data = "none" if len(room.players[0]) == 0 else '\n'.join([f"{player.user.mention}-{api.champions[player.champion]}-{player.reroll_count}" for player in room.players[0]])
        embed.add_field(name="Team 1",value=f"{data}\n", inline=True)
        
        data = "none" if  len(room.players[1]) == 0 else '\n'.join([f"{player.user.mention}-{api.champions[player.champion]}-{player.reroll_count}" for player in room.players[1]])
        embed.add_field(name="Team 2",value=f"{data}\n", inline=True)
        
        await ctx.send(embed=embed)
    
    else:
        await ctx.send(f"Room {room_id} does not exist")


@bot.command()
async def reroll(ctx):
    if ctx.message.author.id in [player.user.id for r in rooms for team in r.players for player in team]:
            for r in rooms:
                for team in r.players:
                    for player in team:
                        if player.user.id == ctx.message.author.id and player.reroll_count > 0:
                            champ = getNewNumber(r.champions, 0, len(api.champions))
                            r.champions.remove(player.champion)
                            
                            player.champion = champ
                            r.champions.append(champ)
                            player.reroll_count -= 1

                            await ShowRoom(ctx, r.id)


if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read('config.ini')

    api = API(config['League of Legends API']['token'])
    bot.run(config['Discord']['token'])