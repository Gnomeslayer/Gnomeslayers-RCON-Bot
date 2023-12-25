from discord import app_commands
from discord.ext import commands
import discord
import json

from lib.battlemetrics import Battlemetrics


class note_slashes(commands.Cog):
    def __init__(self, client):
        print("[Cog] Notes Slashes has been initiated")
        self.client = client

    with open("./json/config.json", "r") as f:
        config = json.load(f)

    bmapi = Battlemetrics(config['tokens']['battlemetrics_token'])
    
    roles = config['cogs']['notes_slashes']['allowed_roles']

    server_names = []
    ban_reasons = []

    for server in config['servers']:
        server_names.append(app_commands.Choice(
            name=f"{server['name']}", value=f"{server['id']}"))

    @ app_commands.command(name="addnote", description="Adds a note to a players BM profile")
    @ app_commands.checks.has_any_role(*roles)
    @ app_commands.guild_only()
    async def addnote(self, interaction: discord.Interaction, steamid: str, note: str):
        await interaction.response.defer(ephemeral=True)
        
        user_ids = await self.bmapi.player.match_identifiers(identifier=steamid, type="steamID")
        battlemetrics_id = user_ids['data'][0]['relationships']['player']['data']['id']
        
        response = await self.bmapi.notes.create(note=note, organization_id=self.config['additional']['organization_id'], player_id=battlemetrics_id, shared=True)
        
        if 'errors' in response:
            response = f"There was an error with that command!\n**RESPONSE**\n{response}"
            await interaction.followup.send(f"{interaction.user.mention} something went wrong:\n{response}")
        else:
            response = f"Successfully ran the command!\n**RESULTS**\n{response}"
            await interaction.followup.send(f"{response}")

    @ app_commands.command(name="viewnotes", description="Pulls all notes from a players profile")
    @ app_commands.checks.has_any_role(*roles)
    @ app_commands.guild_only()
    async def viewnotes(self, interaction: discord.Interaction, steamid: str, note: str):
        await interaction.response.defer(ephemeral=True)

        user_ids = await self.bmapi.player.match_identifiers(identifier=steamid, type="steamID")
        battlemetrics_id = user_ids['data'][0]['relationships']['player']['data']['id']

        response = await self.bmapi.notes.create(note=note, organization_id=self.config['additional']['organization_id'], player_id=battlemetrics_id, shared=True)

        if 'errors' in response:
            response = f"There was an error with that command!\n**RESPONSE**\n{response}"
            await interaction.followup.send(f"{interaction.user.mention} something went wrong:\n{response}")
        else:
            response = f"Successfully ran the command!\n**RESULTS**\n{response}"
            await interaction.followup.send(f"{response}")
            
    @addnote.error
    async def addnote_handler(self, ctx, error):
        if isinstance(error, app_commands.MissingAnyRole):
            await ctx.response.send_message(error, ephemeral=True)
        else:
            await ctx.response.send_message(error, ephemeral=True)
            
    @viewnotes.error
    async def viewnotes_handler(self, ctx, error):
        if isinstance(error, app_commands.MissingAnyRole):
            await ctx.response.send_message(error, ephemeral=True)
        else:
            await ctx.response.send_message(error, ephemeral=True)

async def setup(client):
    await client.add_cog(note_slashes(client))
