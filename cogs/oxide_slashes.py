from discord import app_commands
from discord.ext import commands
import discord
import json
import os

from lib.battlemetrics import Battlemetrics


class oxide_slashes(commands.Cog):
    def __init__(self, client):
        print("[Cog] Oxide Slashes has been initiated")
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
    
    #oxide.show groups
    #oxide.show perms {group}
    #oxide.group add {group}
    #oxide.group remove {group}
    #oxide.grant group {group} {permission} -> example: oxide.grant group admin vanish.allow
    #oxide.usergroup add {name or id} {group} -> oxide.usergroup add {steamid} {group}
    #oxide.usergroup remove {name or id} {group} -> oxide.usergroup remove {steamid} {group}
    
    #oxide.grant {name or id} {permission}
    #oxide.revoke user {name or id} {permission}
    #oxide.show user {name or id}
    #oxide.show perm {permission}
    #oxide.show perms
    

    @app_commands.command(name="oxide_show_groups", description="Grabs the oxide groups")
    @app_commands.checks.has_any_role(*roles)
    @app_commands.guild_only()
    @ app_commands.describe(server="Select a server")
    @ app_commands.choices(server=[*server_names])
    async def teaminfo(self, interaction: discord.Interaction, server: app_commands.Choice[str]):
        await interaction.response.defer(ephemeral=True)
        #oxide.show groups
        
        
    

async def setup(client):
    await client.add_cog(oxide_slashes(client))
