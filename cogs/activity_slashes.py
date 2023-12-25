from discord import app_commands
from discord.ext import commands
import discord
import json
import os

from lib.battlemetrics import Battlemetrics


class activity_slashes(commands.Cog):
    def __init__(self, client):
        print("[Cog] Activity Slashes has been initiated")
        self.client = client

    with open("./json/config.json", "r") as f:
        config = json.load(f)

    bmapi = Battlemetrics(config['tokens']['battlemetrics_token'])
    
    roles = config['cogs']['activity_slashes']['allowed_roles']
    
    server_names = []
    ban_reasons = []

    for server in config['servers']:
        server_names.append(app_commands.Choice(
            name=f"{server['name']}", value=f"{server['id']}"))

    @app_commands.command(name="teaminfo", description="Retrieves a players team information.")
    @app_commands.checks.has_any_role(*roles)
    @app_commands.guild_only()
    @ app_commands.describe(server="Select a server")
    @ app_commands.choices(server=[*server_names])
    async def teaminfo(self, interaction: discord.Interaction, steamid: str, server: app_commands.Choice[str]):
        await interaction.response.defer(ephemeral=True)
        response = await self.bmapi.server.console_command(server_id=server.value, command=f"teaminfo {steamid}")
        if 'error' in response:
            await interaction.followup.send(f"Something went wrong while running the command\n{response}")
        if not response['data']['attributes']['success']:
            await interaction.followup.send("Command failed to execute.")
        elif response['data']['attributes']['result'] == "Player is not in a team":
            await interaction.followup.send(response['data']['attributes']['result'])
        else:
            embed = discord.Embed()
            test = response['data']['attributes']['result'].split()
            team_links = None
            for t in test:
                if t.isnumeric():
                    if len(t) == 17:
                        user_ids = await self.bmapi.player.match_identifiers(identifier=t, type="steamID")
                        battlemetrics_id = user_ids['data'][0]['relationships']['player']['data']['id']
                        if team_links:
                            team_links += f"\n[Battlemetrics](https://www.battlemetrics.com/rcon/players/{battlemetrics_id}) - [Steam](http://steamcommunity.com/profiles/{t}) - {user_ids['data'][0]['attributes']['metadata']['profile']['personaname']}"
                        else:
                            team_links = f"[Battlemetrics](https://www.battlemetrics.com/rcon/players/{battlemetrics_id}) - [Steam](http://steamcommunity.com/profiles/{t}) - {user_ids['data'][0]['attributes']['metadata']['profile']['personaname']}"
            if team_links:
                embed.description = f"# Team information for: {steamid} \n```perl\n{response['data']['attributes']['result']}```\n**Player team links in order**\n{team_links}"
            else:
                embed.description = f"# Team information for: {steamid} \n```perl\n{response['data']['attributes']['result']}```"
            await interaction.followup.send(embed=embed)
    
    
    
    @ app_commands.command(name="combatlog", description="Requests a player's combat log")
    @ app_commands.checks.has_any_role(*roles)
    @ app_commands.guild_only()
    @ app_commands.describe(server="Select a server")
    @ app_commands.choices(server=[*server_names])
    async def combatlog(self, interaction: discord.Interaction, steamid: str, server: app_commands.Choice[str] = "0", raw_response:bool = False):
        await interaction.response.defer(ephemeral=True)
        
        if server == "0":
            await interaction.followup.send("No server supplied. Will scan servers in order and return the first result.")
            response = None
            for server in self.config['servers']:
                response = await self.bmapi.server.console_command(server_id=server['id'], command=f"combatlog {steamid}")
                if not 'invalid player' in response:
                    break
            if not response or 'invalid player' in response:
                await interaction.followup.send("Unable to locate that user.")
        else:
            response = await self.bmapi.server.console_command(server_id=server.value,command=f"combatlog {steamid}")
            if 'invalid player' in response:
                await interaction.followup.send(f"Unable to locate the user on the supplied server. Will scan all servers and return the first result.")
                for server in self.config['servers']:
                    response = await self.bmapi.server.console_command(server_id=server['name'], command=f"combatlog {steamid}")
                    if not 'invalid player' in response:
                        break
                if not response or 'invalid player' in response:
                    await interaction.followup.send("Unable to locate that user.")
        
        if not response.get('data'):
            await interaction.followup.send("You do not have permission to retrieve data from that server.", ephemeral=True)
            return
        
        #Create a dictionary 
        data = response['data']['attributes']['result']
        lines = data.strip().split('\n')
        header = lines[0].split()

        result_dict = []
        for line in lines[1:]:
            values = line.split()
            entry = {}
            count = 0
            if values[0] == "+":
                break
            for i in values:
                entry[header[count]] = i
                count += 1
            result_dict.append(entry)
        if not raw_response:
            
            player_details = {}
            embed_description = None
            sent_responses = 0
            for item in result_dict:
                time = item['time']
                attacker = None
                target = None
                id = item['id']
                if item['attacker'] == "you":
                    attacker = f"[You](https://steamcommunity.com/profiles/{steamid})"
                else:
                    if item['attacker'] == "player":
                        if id in player_details:
                            attacker = f"[{id}](https://www.battlemetrics.com/rcon/players/{player_details[id]['bmid']})"
                        else:
                            bmprofile = await self.bmapi.activity_logs(filter_search=id)
                            player_details[id] = {}
                            try:
                                player_details[id]['bmid'] = bmprofile['data'][0]['relationships']['players']['data'][0]['id']
                            except:
                                player_details[id]['bmid'] = 0
                            if player_details[id]['bmid']:
                                attacker = f"[{id}](https://www.battlemetrics.com/rcon/players/{player_details[id]['bmid']})"
                            else:
                                attacker = f"{id}"
                
                if item['target'] == "you":
                    target = f"[You](https://steamcommunity.com/profiles/{steamid})"
                else:
                    if item['target'] == "player":
                        if id in player_details:
                            if player_details[id]['bmid']:
                                target = f"[{id}](https://www.battlemetrics.com/rcon/players/{player_details[id]['bmid']})"
                            else:
                                target = f"{id}"
                        else:
                            
                            bmprofile = await self.bmapi.activity_logs(filter_search=id)
                            
                            player_details[id] = {}
                            try:
                                player_details[id]['bmid'] = bmprofile['data'][0]['relationships']['players']['data'][0]['id']
                            except:
                                player_details[id]['bmid'] = 0
                            if player_details[id]['bmid']:
                                target = f"[{id}](https://www.battlemetrics.com/rcon/players/{player_details[id]['bmid']})"
                            else:
                                target = f"{id}"
                        
                weapon = "weapon"
                ammo = item['ammo']
                area = item['area']
                distance = item['distance']
                hp_change = f"{item['old_hp']} > {item['new_hp']}"
                if target:
                    if not embed_description:
                        embed_description = f"{time} - {attacker} - {target} - {weapon} - {ammo} - {area} - {distance} - {hp_change}"
                    else:
                        embed_description += f"\n{time} - {attacker} - {target} - {weapon} - {ammo} - {area} - {distance} - {hp_change}"
                    if len(embed_description) >= 3500:
                        embed = discord.Embed(description=embed_description, title=f"Displaying combatlog for {steamid}")
                        await interaction.followup.send(content="Part of combatlog", embed=embed, ephemeral=True)
                        embed_description = None
                        sent_responses += 1
            if embed_description:
                embed = discord.Embed(description=embed_description, title=f"Displaying combatlog for {steamid}")
                await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                if not sent_responses:
                    await interaction.followup.send(content="Combatlogs found, but nothing in recent attacks were related to PVP.")
        else:
            response = response['data']['attributes']['result']
            with open(f"{steamid}.txt", "w") as f:
                f.write(response)
                f.close()
            await interaction.followup.send(content=f"combatlog scan of <https://steamcommunity.com/profiles/{steamid}>", file=discord.File(f"{steamid}.txt"), ephemeral=False)
            os.remove(f"{steamid}.txt")
            
    
    @ app_commands.command(name="say", description="Sends a message in the given rust server chat")
    @ app_commands.checks.has_any_role(*roles)
    @ app_commands.guild_only()
    @ app_commands.describe(server="Select a server")
    @ app_commands.choices(server=[*server_names])
    async def say(self, interaction: discord.Interaction, message:str,server: app_commands.Choice[str], send_anon:bool = False):
        await interaction.response.defer(ephemeral=True)
        
        server = server.value
        if send_anon:
            member = "Server"
        else:
            member = interaction.user.name
        response = await self.bmapi.server.send_chat(server_id=server,message=message,sender_name=member)
        
        await interaction.followup.send(f"```{response}```")
            
        
    @teaminfo.error
    async def teaminfo_handler(self, ctx, error):
        if isinstance(error, app_commands.MissingAnyRole):
            await ctx.response.send_message(error, ephemeral=True)
        else:
            await ctx.response.send_message(error, ephemeral=True)
            
    @combatlog.error
    async def combatlog_handler(self, ctx, error):
        if isinstance(error, app_commands.MissingAnyRole):
            await ctx.response.send_message(error, ephemeral=True)
        else:
            await ctx.response.send_message(error, ephemeral=True)
        
    

async def setup(client):
    await client.add_cog(activity_slashes(client))
