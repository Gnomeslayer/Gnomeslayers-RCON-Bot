from discord import app_commands
from discord.ext import commands
import discord
import json
from datetime import datetime

from lib.battlemetrics import Battlemetrics


class server_slashes(commands.Cog):
    def __init__(self, client):
        print("[Cog] Server Slashes has been initiated")
        self.client = client

    with open("./json/config.json", "r") as f:
        config = json.load(f)

    bmapi = Battlemetrics(config['tokens']['battlemetrics_token'])
    
    roles = config['cogs']['server_slashes']['allowed_roles']
    
    server_names = []
    ban_reasons = []

    for server in config['servers']:
        server_names.append(app_commands.Choice(
            name=f"{server['name']}", value=f"{server['id']}"))
    
    
    @ app_commands.command(name="server_info", description="Requests the server information")
    @ app_commands.checks.has_any_role(*roles)
    @ app_commands.guild_only()
    @ app_commands.describe(server="Select a server")
    @ app_commands.choices(server=[*server_names])
    async def server_info(self, interaction: discord.Interaction, server: app_commands.Choice[str]):
        await interaction.response.defer(ephemeral=False)
        
        server_id = server.value
        
        
        server_info = await self.bmapi.server.info(server_id=server_id)
        server_name = server_info['data']['attributes']['name']
        server_ip = server_info['data']['attributes']['ip']
        server_port = server_info['data']['attributes']['port']
        server_players = server_info['data']['attributes']['players']
        server_maxplayers = server_info['data']['attributes']['maxPlayers']
        server_rank = server_info['data']['attributes']['rank']
        server_status = server_info['data']['attributes']['status']
        
        server_type = server_info['data']['attributes']['details']['rust_type']
        server_map = server_info['data']['attributes']['details']['map']
        server_fps = server_info['data']['attributes']['details']['rust_fps']
        server_image = server_info['data']['attributes']['details']['rust_headerimage']
        server_website = server_info['data']['attributes']['details']['rust_url']
        server_map_size = server_info['data']['attributes']['details']['rust_world_size']
        server_description = server_info['data']['attributes']['details']['rust_description']
        server_queued_players = server_info['data']['attributes']['details']['rust_queued_players']
        server_last_wipe = server_info['data']['attributes']['details']['rust_last_wipe']
        
        timestamp_dt = datetime.strptime(server_last_wipe, "%Y-%m-%dT%H:%M:%S.%fZ")
        
        epoch_time = int(timestamp_dt.timestamp())
        
        player_list = []
        for i in server_info['included']:
            if i['type'] == "player":
                player = {
                    'name': i['attributes']['name'],
                    'bmid': i['attributes']['id'],
                    'steamid': 0
                }
                player_list.append(player)
                
        for player in player_list:
            bmid = player['bmid']
            for i in server_info['included']:
                if i['type'] == "identifier":
                    if i['attributes']['type'] == "steamID":
                        if str(i['relationships']['player']['data']['id']) == str(bmid):
                            player['steamid'] = i['attributes']['identifier']
                            
        embed = discord.Embed(title=f"{server_name}", description=f"**Server IP**\n# {server_ip}:{server_port}")
        #embed.add_field(name="Server Name", value=f"{server_name}")
        #embed.add_field(name="Server IP", value=f"{server_ip}:{server_port}", inline=True)
        embed.add_field(name="Server Players", value=f"{server_players}/{server_maxplayers} - Queued: {server_queued_players}")
        embed.add_field(name="Server Rank", value=f"{server_rank}")
        embed.add_field(name="Server Status", value=f"{server_status}")
        embed.add_field(name="Server Type", value=f"{server_type}")
        embed.add_field(name="Server Map", value=f"{server_map}")
        embed.add_field(name="Server FPS", value=f"{server_fps}")
        embed.add_field(name="Server Website", value=f"[Website]({server_website})")
        embed.add_field(name="Server Map Size", value=f"{server_map_size}")
        embed.add_field(name="Server Last Wipe", value=f"<t:{epoch_time}:R>")
        
        #embed.add_field(name="Server Player List", value=f"{player_list}")
        #embed.set_thumbnail(url=server_image)
        
        embed.set_image(url=server_image)
        await interaction.followup.send(embed=embed)
        
    @server_info.error
    async def server_info_handler(self, ctx, error):
        if isinstance(error, app_commands.MissingAnyRole):
            await ctx.response.send_message(error, ephemeral=True)
        else:
            await ctx.response.send_message(error, ephemeral=True)
        
    

async def setup(client):
    await client.add_cog(server_slashes(client))
