from lib.battlemetrics import Battlemetrics
import os
import json
import discord
from discord.ext import commands
from discord import app_commands


class clans_slashes(commands.Cog):
    def __init__(self, client):
        print("[Cog] Clans Slashes has been initiated")
        self.client = client

    with open("./json/config.json", "r") as f:
        config = json.load(f)
    
    bmapi = Battlemetrics(config['tokens']['battlemetrics_token'])

    roles = config['cogs']['clans_slashes']['allowed_roles']
    
    server_names = []
    ban_reasons = []

    for server in config['servers']:
        server_names.append(app_commands.Choice(
            name=f"{server['name']}", value=f"{server['id']}"))

    @ app_commands.command(name="clans_list", description="Lists all clans, their owners and their member-count")
    @ app_commands.checks.has_any_role(*roles)
    @ app_commands.guild_only()
    @ app_commands.describe(server="Select a server")
    @ app_commands.choices(server=[*server_names])
    async def clans_list(self, interaction: discord.Interaction, server: app_commands.Choice[str]):
        await interaction.response.defer(ephemeral=True)
        response = await self.bmapi.server.console_command(server_id=server['id'], command=f"clans list")
        response = response['data']['attributes']['result']
        with open(f"clans_list.txt", "w") as f:
            f.write(response)
            f.close()
        await interaction.followup.send(content=f"Clans response", file=discord.File(f"clans_list.txt"), ephemeral=False)
        os.remove(f"clans_list.txt")
    
    @ app_commands.command(name="clans_listx", description="Lists all clans, their owners/members and their on-line status")
    @ app_commands.checks.has_any_role(*roles)
    @ app_commands.guild_only()
    @ app_commands.describe(server="Select a server")
    @ app_commands.choices(server=[*server_names])
    async def clans_listx(self, interaction: discord.Interaction, server: app_commands.Choice[str]):
        await interaction.response.defer(ephemeral=True)
        response = await self.bmapi.server.console_command(server_id=server['id'], command=f"clans listx")
        response = response['data']['attributes']['result']
        with open(f"clans_listx.txt", "w") as f:
            f.write(response)
            f.close()
        await interaction.followup.send(content=f"Clans response", file=discord.File(f"clans_listx.txt"), ephemeral=False)
        os.remove(f"clans_listx.txt")
    
    @ app_commands.command(name="clans_show", description="lists the chosen clan ( or clan by user) and the members with status")
    @ app_commands.checks.has_any_role(*roles)
    @ app_commands.guild_only()
    @ app_commands.describe(server="Select a server")
    @ app_commands.choices(server=[*server_names])
    async def clans_show(self, interaction: discord.Interaction, tag: str, server: app_commands.Choice[str]):
        await interaction.response.defer(ephemeral=True)
        response = await self.bmapi.server.console_command(server_id=server['id'], command=f"clans show '{tag}'")
        response = response['data']['attributes']['result']
        with open(f"clans_show.txt", "w") as f:
            f.write(response)
            f.close()
        await interaction.followup.send(content=f"Clans response", file=discord.File(f"clans_show.txt"), ephemeral=False)
        os.remove(f"clans_show.txt")
        
    @ app_commands.command(name="clans_msg", description="Sends a clan message")
    @ app_commands.checks.has_any_role(*roles)
    @ app_commands.guild_only()
    @ app_commands.describe(server="Select a server")
    @ app_commands.choices(server=[*server_names])
    async def clans_msg(self, interaction: discord.Interaction, tag: str, message:str, server: app_commands.Choice[str]):
        await interaction.response.defer(ephemeral=True)
        response = await self.bmapi.server.console_command(server_id=server['id'], command=f"clans msg '{tag}' {message}")
        response = response['data']['attributes']['result']
        with open(f"clans_msg.txt", "w") as f:
            f.write(response)
            f.close()
        await interaction.followup.send(content=f"Clans response", file=discord.File(f"clans_msg.txt"), ephemeral=False)
        os.remove(f"clans_msg.txt")
    
    @ app_commands.command(name="clans_create", description="Creates a clan")
    @ app_commands.checks.has_any_role(*roles)
    @ app_commands.guild_only()
    @ app_commands.describe(server="Select a server")
    @ app_commands.choices(server=[*server_names])
    async def clans_create(self, interaction: discord.Interaction, tag: str, owner_steam_id: str, server: app_commands.Choice[str], desc: str = None):
        await interaction.response.defer(ephemeral=True)
        response = await self.bmapi.server.console_command(server_id=server['id'], command=f"clans create '{tag}' '{owner_steam_id}' '{desc}'")
        response = response['data']['attributes']['result']
        with open(f"clans_create.txt", "w") as f:
            f.write(response)
            f.close()
        await interaction.followup.send(content=f"Clans response", file=discord.File(f"clans_create.txt"), ephemeral=False)
        os.remove(f"clans_create.txt")
    
    @ app_commands.command(name="clans_reserve", description="Reserves a clan")
    @ app_commands.checks.has_any_role(*roles)
    @ app_commands.guild_only()
    @ app_commands.describe(server="Select a server")
    @ app_commands.choices(server=[*server_names])
    async def clans_reserve(self, interaction: discord.Interaction, tag: str, steam_id: str, server: app_commands.Choice[str], desc: str = None):
        await interaction.response.defer(ephemeral=True)
        response = await self.bmapi.server.console_command(server_id=server['id'], command=f"clans reserve '{tag}' '{steam_id}' ")
        response = response['data']['attributes']['result']
        with open(f"clans_reserve.txt", "w") as f:
            f.write(response)
            f.close()
        await interaction.followup.send(content=f"Clans response", file=discord.File(f"clans_reserve.txt"), ephemeral=False)
        os.remove(f"clans_reserve.txt")
    
    @ app_commands.command(name="clans_rename", description="Renames a clan")
    @ app_commands.checks.has_any_role(*roles)
    @ app_commands.guild_only()
    @ app_commands.describe(server="Select a server")
    @ app_commands.choices(server=[*server_names])
    async def clans_rename(self, interaction: discord.Interaction, old_tag: str, new_tag: str, server: app_commands.Choice[str]):
        await interaction.response.defer(ephemeral=True)
        response = await self.bmapi.server.console_command(server_id=server['id'], command=f"clans rename '{old_tag}' '{new_tag}' ")
        response = response['data']['attributes']['result']
        with open(f"clans_rename.txt", "w") as f:
            f.write(response)
            f.close()
        await interaction.followup.send(content=f"Clans response", file=discord.File(f"clans_rename.txt"), ephemeral=False)
        os.remove(f"clans_rename.txt")
    
    @ app_commands.command(name="clans_disband", description="Disbands a clan")
    @ app_commands.checks.has_any_role(*roles)
    @ app_commands.guild_only()
    @ app_commands.describe(server="Select a server")
    @ app_commands.choices(server=[*server_names])
    async def clans_disband(self, interaction: discord.Interaction, tag: str, server: app_commands.Choice[str]):
        await interaction.response.defer(ephemeral=True)
        response = await self.bmapi.server.console_command(server_id=server['id'], command=f"clans disband '{tag}'")
        response = response['data']['attributes']['result']
        with open(f"clans_disband.txt", "w") as f:
            f.write(response)
            f.close()
        await interaction.followup.send(content=f"Clans response", file=discord.File(f"clans_disband.txt"), ephemeral=False)
        os.remove(f"clans_disband.txt")
    
    @ app_commands.command(name="clans_join", description="Joins a player into a clan")
    @ app_commands.checks.has_any_role(*roles)
    @ app_commands.guild_only()
    @ app_commands.describe(server="Select a server")
    @ app_commands.choices(server=[*server_names])
    async def clans_join(self, interaction: discord.Interaction, tag: str, steam_id: str, server: app_commands.Choice[str]):
        await interaction.response.defer(ephemeral=True)
        response = await self.bmapi.server.console_command(server_id=server['id'], command=f"clans join '{tag}' '{steam_id}'")
        response = response['data']['attributes']['result']
        with open(f"clans_join.txt", "w") as f:
            f.write(response)
            f.close()
        await interaction.followup.send(content=f"Clans response", file=discord.File(f"clans_join.txt"), ephemeral=False)
        os.remove(f"clans_join.txt")
    
    @ app_commands.command(name="clans_kick", description="kicks a member from a clan | deletes an invite")
    @ app_commands.checks.has_any_role(*roles)
    @ app_commands.guild_only()
    @ app_commands.describe(server="Select a server")
    @ app_commands.choices(server=[*server_names])
    async def clans_kick(self, interaction: discord.Interaction, tag: str, steam_id: str, server: app_commands.Choice[str]):
        await interaction.response.defer(ephemeral=True)
        response = await self.bmapi.server.console_command(server_id=server['id'], command=f"clans kick '{tag}' '{steam_id}'")
        response = response['data']['attributes']['result']
        with open(f"clans_kick.txt", "w") as f:
            f.write(response)
            f.close()
        await interaction.followup.send(content=f"Clans response", file=discord.File(f"clans_kick.txt"), ephemeral=False)
        os.remove(f"clans_kick.txt")
    
    @ app_commands.command(name="clans_owner", description="Sets a new owner")
    @ app_commands.checks.has_any_role(*roles)
    @ app_commands.guild_only()
    @ app_commands.describe(server="Select a server")
    @ app_commands.choices(server=[*server_names])
    async def clans_owner(self, interaction: discord.Interaction, tag: str, steam_id: str, server: app_commands.Choice[str]):
        await interaction.response.defer(ephemeral=True)
        response = await self.bmapi.server.console_command(server_id=server['id'], command=f"clans owner '{tag}' '{steam_id}'")
        response = response['data']['attributes']['result']
        with open(f"clans_owner.txt", "w") as f:
            f.write(response)
            f.close()
        await interaction.followup.send(content=f"Clans response", file=discord.File(f"clans_owner.txt"), ephemeral=False)
        os.remove(f"clans_owner.txt")
    
    @ app_commands.command(name="clans_promote", description="Promotes a member (within the clan)")
    @ app_commands.checks.has_any_role(*roles)
    @ app_commands.guild_only()
    @ app_commands.describe(server="Select a server")
    @ app_commands.choices(server=[*server_names])
    async def clans_promote(self, interaction: discord.Interaction, tag: str, steam_id: str, server: app_commands.Choice[str]):
        await interaction.response.defer(ephemeral=True)
        response = await self.bmapi.server.console_command(server_id=server['id'], command=f"clans promote '{tag}' '{steam_id}'")
        response = response['data']['attributes']['result']
        with open(f"clans_promote.txt", "w") as f:
            f.write(response)
            f.close()
        await interaction.followup.send(content=f"Clans response", file=discord.File(f"clans_promote.txt"), ephemeral=False)
        os.remove(f"clans_promote.txt")
    
    @ app_commands.command(name="clans_demote", description="Demotes a member (within the clan)")
    @ app_commands.checks.has_any_role(*roles)
    @ app_commands.guild_only()
    @ app_commands.describe(server="Select a server")
    @ app_commands.choices(server=[*server_names])
    async def clans_demote(self, interaction: discord.Interaction, tag: str, steam_id: str, server: app_commands.Choice[str]):
        await interaction.response.defer(ephemeral=True)
        response = await self.bmapi.server.console_command(server_id=server['id'], command=f"clans demote '{tag}' '{steam_id}'")
        response = response['data']['attributes']['result']
        with open(f"clans_demote.txt", "w") as f:
            f.write(response)
            f.close()
        await interaction.followup.send(content=f"Clans response", file=discord.File(f"clans_demote.txt"), ephemeral=False)
        os.remove(f"clans_demote.txt")

    @clans_list.error
    async def clans_list_handler(self, ctx, error):
        if isinstance(error, app_commands.MissingAnyRole):
            await ctx.response.send_message(error, ephemeral=True)
        else:
            await ctx.response.send_message(error, ephemeral=True)
            
    @clans_listx.error
    async def clans_listx_handler(self, ctx, error):
        if isinstance(error, app_commands.MissingAnyRole):
            await ctx.response.send_message(error, ephemeral=True)
        else:
            await ctx.response.send_message(error, ephemeral=True)
            
    @clans_show.error
    async def clans_show_handler(self, ctx, error):
        if isinstance(error, app_commands.MissingAnyRole):
            await ctx.response.send_message(error, ephemeral=True)
        else:
            await ctx.response.send_message(error, ephemeral=True)
            
    @clans_msg.error
    async def clans_msg_handler(self, ctx, error):
        if isinstance(error, app_commands.MissingAnyRole):
            await ctx.response.send_message(error, ephemeral=True)
        else:
            await ctx.response.send_message(error, ephemeral=True)
            
    @clans_create.error
    async def clans_create_handler(self, ctx, error):
        if isinstance(error, app_commands.MissingAnyRole):
            await ctx.response.send_message(error, ephemeral=True)
        else:
            await ctx.response.send_message(error, ephemeral=True)
            
    @clans_reserve.error
    async def clans_reserve_handler(self, ctx, error):
        if isinstance(error, app_commands.MissingAnyRole):
            await ctx.response.send_message(error, ephemeral=True)
        else:
            await ctx.response.send_message(error, ephemeral=True)
            
    @clans_rename.error
    async def clans_rename_handler(self, ctx, error):
        if isinstance(error, app_commands.MissingAnyRole):
            await ctx.response.send_message(error, ephemeral=True)
        else:
            await ctx.response.send_message(error, ephemeral=True)
            
    @clans_disband.error
    async def clans_disband_handler(self, ctx, error):
        if isinstance(error, app_commands.MissingAnyRole):
            await ctx.response.send_message(error, ephemeral=True)
        else:
            await ctx.response.send_message(error, ephemeral=True)
            
    @clans_join.error
    async def clans_join_handler(self, ctx, error):
        if isinstance(error, app_commands.MissingAnyRole):
            await ctx.response.send_message(error, ephemeral=True)
        else:
            await ctx.response.send_message(error, ephemeral=True)
            
    @clans_kick.error
    async def clans_kick_handler(self, ctx, error):
        if isinstance(error, app_commands.MissingAnyRole):
            await ctx.response.send_message(error, ephemeral=True)
        else:
            await ctx.response.send_message(error, ephemeral=True)
            
    @clans_owner.error
    async def clans_owner_handler(self, ctx, error):
        if isinstance(error, app_commands.MissingAnyRole):
            await ctx.response.send_message(error, ephemeral=True)
        else:
            await ctx.response.send_message(error, ephemeral=True)
            
    @clans_promote.error
    async def clans_promote_handler(self, ctx, error):
        if isinstance(error, app_commands.MissingAnyRole):
            await ctx.response.send_message(error, ephemeral=True)
        else:
            await ctx.response.send_message(error, ephemeral=True)
            
    @clans_demote.error
    async def clans_demote_handler(self, ctx, error):
        if isinstance(error, app_commands.MissingAnyRole):
            await ctx.response.send_message(error, ephemeral=True)
        else:
            await ctx.response.send_message(error, ephemeral=True)
            
            
async def setup(client):
    await client.add_cog(clans_slashes(client))
