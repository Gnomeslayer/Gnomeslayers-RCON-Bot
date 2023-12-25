import json

import discord
from discord import app_commands
from discord.ext import commands
from discord.utils import get

from lib.battlemetrics import Battlemetrics

class RCON(commands.Cog):
    def __init__(self, client):
        print("[Cog] RCON has been initiated")
        self.client = client
        self.users = []
    
    with open("./json/config.json", "r") as f:
        config = json.load(f)

    bmapi = Battlemetrics(config['tokens']['battlemetrics_token'])
    
    roles = config['cogs']['rcon']['allowed_roles']
            
    server_names = []
    for server in config['servers']:
        server_names.append(app_commands.Choice(
            name=f"{server['name']}", value=f"{server['id']}"))
        
        
    @ app_commands.command(name="rcon_command", description="Sends an RCON command")
    @ app_commands.checks.has_any_role(*roles)
    @ app_commands.guild_only()
    @ app_commands.choices(server=[*server_names])
    async def rcon_command(self, interaction: discord.Interaction, server: app_commands.Choice[str], command:str):
        await interaction.response.defer(ephemeral=True)
        response = await self.bmapi.server.console_command(server_id=server.value, command=command)

        if 'errors' in response:
            response = f"There was an error with that command!\n**RESPONSE**\n{response['errors'][0]['detail']}"
            await interaction.followup.send(f"{interaction.user.mention} something went wrong:\n{response}")
        else:
            response = f"Successfully ran the command!\n**RESULTS**\n{response['data']['attributes']['result']}"
            await interaction.followup.send(f"{response}")

    @rcon_command.error
    async def rcon_command_handler(self, ctx, error):
        if isinstance(error, app_commands.MissingAnyRole):
            await ctx.response.send_message(error, ephemeral=True)
        else:
            await ctx.response.send_message(error, ephemeral=True)
            
async def setup(client):
    await client.add_cog(RCON(client))
