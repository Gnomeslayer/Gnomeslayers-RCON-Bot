from discord import app_commands
from discord.ext import commands
import discord
import json
from datetime import datetime
from lib.battlemetrics import Battlemetrics


class bans_slashes(commands.Cog):
    def __init__(self, client):
        print("[Cog] Bans Slashes has been initiated")
        self.client = client

    with open("./json/config.json", "r") as f:
        config = json.load(f)
    
    bmapi = Battlemetrics(config['tokens']['battlemetrics_token'])
    
    roles = config['cogs']['bans_slashes']['allowed_roles']
     
    server_names = []
    ban_reasons = []
    
    for server in config['servers']:
        server_names.append(app_commands.Choice(
            name=f"{server['name']}", value=f"{server['id']}"))
    for reason in config['ban_reasons']:
        ban_reasons.append(app_commands.Choice(
            name=f"{reason['reason']}", value=f"{reason['duration']}"))    

    @ app_commands.command(name="ban", description="Bans a person from the server.")
    @ app_commands.checks.has_any_role(*roles)
    @ app_commands.guild_only()
    @ app_commands.describe(server="Select a server")
    @ app_commands.choices(server=[*server_names])
    @ app_commands.describe(reason="Select a reason")
    @ app_commands.choices(reason=[*ban_reasons])
    async def rust_ban(self, interaction: discord.Interaction, steamid: str, server: app_commands.Choice[str], reason: app_commands.Choice[str], note: str, orgwide:bool=True):
        await interaction.response.defer(ephemeral=True)
        user_ids = await self.bmapi.player.match_identifiers(identifier=steamid, type="steamID")
        
        battlemetrics_id = user_ids['data'][0]['relationships']['player']['data']['id']
        player_info = await self.bmapi.player.info(battlemetrics_id)
        beguid = 0
        steamid = 0
        for i in player_info['included']:
            if i['type'] == "identifier":
                if i['attributes']['type'] == "BEGUID":
                    beguid = int(i['id'])
                if i['attributes']['type'] == "steamID":
                    steamid = int(i['id'])
        
        expires = reason.value
            
        response = await self.bmapi.bans.create(reason=reason.name, note=note, beguid_id=beguid, steamid_id=steamid, battlemetrics_id=battlemetrics_id,
                                       org_id=self.config['additional']['organization_id'], server_id=server.value,
                                       banlist=self.config['additional']['banlist'], expires=expires, orgwide=orgwide)

        if 'errors' in response:
            response = f"There was an error with that command!\n**RESPONSE**\n{response}"
            await interaction.followup.send(f"{interaction.user.mention} something went wrong:\n{response}")
        else:
            response = f"Successfully ran the command!\n**RESULTS**\n{response}"
            await interaction.followup.send(f"{response}")
            
    @ app_commands.command(name="listbans", description="Grabs all bans for the targeted user.")
    @ app_commands.checks.has_any_role(*roles)
    @ app_commands.guild_only()
    async def listbans(self, interaction: discord.Interaction, steamid: str, include_expired:bool):
        await interaction.response.defer(ephemeral=True)
        user_ids = await self.bmapi.player.match_identifiers(identifier=steamid, type="steamID")
        battlemetrics_id = user_ids['data'][0]['relationships']['player']['data']['id']
        user_bans = await self.bmapi.ban_list.search(player_id=battlemetrics_id, expired=include_expired, organization_id=self.config['additional']['organization_id'])
        ban_info = None
        for ban in user_bans['data']:
            # Convert the input string to a datetime object
            datetime_obj = datetime.strptime(ban['attributes']['timestamp'], "%Y-%m-%dT%H:%M:%S.%fZ")
            # Extract the timestamp from the datetime object and convert to integer
            timestamp = int(datetime_obj.timestamp())
            current_datetime = datetime.now()
            current_time = int(current_datetime.timestamp())
            if current_time > timestamp and include_expired:
                if ban_info:
                    ban_info += f"\n**[[{ban['id']}]](https://www.battlemetrics.com/rcon/bans/edit/{ban['attributes']['id']})** - EXPIRED: <t:{timestamp}>\n{ban['attributes']['reason']}"
                else:
                    ban_info = f"**[[{ban['id']}]](https://www.battlemetrics.com/rcon/bans/edit/{ban['attributes']['id']})** - EXPIRED: <t:{timestamp}>\n{ban['attributes']['reason']}"
            else:
                if ban_info:
                    ban_info += f"\n**[[{ban['id']}]](https://www.battlemetrics.com/rcon/bans/edit/{ban['attributes']['id']})** - EXPIRED: <t:{timestamp}>\n{ban['attributes']['reason']}"
                else:
                    ban_info = f"**[[{ban['id']}]](https://www.battlemetrics.com/rcon/bans/edit/{ban['attributes']['id']})** - EXPIRED: <t:{timestamp}>\n{ban['attributes']['reason']}"
        await interaction.followup.send(f"{ban_info}", ephemeral=True)
    
    @rust_ban.error
    async def rust_ban_handler(self, ctx, error):
        if isinstance(error, app_commands.MissingAnyRole):
            await ctx.response.send_message(error, ephemeral=True)
        else:
            await ctx.response.send_message(error, ephemeral=True)
    @listbans.error
    async def listbans_handler(self, ctx, error):
        if isinstance(error, app_commands.MissingAnyRole):
            await ctx.response.send_message(error, ephemeral=True)
        else:
            await ctx.response.send_message(error, ephemeral=True)

async def setup(client):
    await client.add_cog(bans_slashes(client))
