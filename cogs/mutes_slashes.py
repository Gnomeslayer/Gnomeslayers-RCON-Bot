from discord import app_commands
from discord.ext import commands
import discord
import json
from lib.battlemetrics import Battlemetrics

class mutes_slashes(commands.Cog):
    def __init__(self, client):
        print("[Cog] Mutes Slashes has been initiated")
        self.client = client

    with open("./json/config.json", "r") as f:
        config = json.load(f)

    bmapi = Battlemetrics(config['tokens']['battlemetrics_token'])
    
    roles = config['cogs']['mutes_slashes']['allowed_roles']
    
    server_names = []
    mute_reasons = []

    for server in config['servers']:
        server_names.append(app_commands.Choice(
            name=f"{server['name']}", value=f"{server['id']}"))
    for reason in config['mute_reasons']:
        mute_reasons.append(app_commands.Choice(
            name=f"{reason['reason']}", value=f"{reason['duration']}"))

    @ app_commands.command(name="mute", description="Mutes a person on the server.")
    @ app_commands.checks.has_any_role(*roles)
    @ app_commands.guild_only()
    @ app_commands.describe(server="Select a server")
    @ app_commands.choices(server=[*server_names])
    @ app_commands.describe(reason="Select a reason")
    @ app_commands.choices(reason=[*mute_reasons])
    async def rust_mute(self, interaction: discord.Interaction, steamid: str, server: app_commands.Choice[str], reason: app_commands.Choice[str]):
        await interaction.response.defer(ephemeral=True)
        
        response = await self.bmapi.server.console_command(server_id=server.value, command=f"mute {steamid} {reason.value} \"{reason.name}\"")
                
        if 'errors' in response:
            response = f"There was an error with that command!\n**RESPONSE**\n{response['errors'][0]['detail']}"
            await interaction.followup.send(f"{interaction.user.mention} something went wrong:\n{response}")
        else:
            response = f"Successfully ran the command!\n**RESULTS**\n{response['data']['attributes']['result']}"
            await interaction.followup.send(f"{response}")

    @ app_commands.command(name="unmute", description="Unmutes a person on the server.")
    @ app_commands.checks.has_any_role(*roles)
    @ app_commands.guild_only()
    @ app_commands.describe(server="Select a server")
    @ app_commands.choices(server=[*server_names])
    async def rust_unmute(self, interaction: discord.Interaction, steamid: str, server: app_commands.Choice[str]):
        await interaction.response.defer(ephemeral=True)
        
        response = await self.bmapi.server.console_command(server_id=server.value, command=f"unmute {steamid}")

        if 'errors' in response:
            response = f"There was an error with that command!\n**RESPONSE**\n{response['errors'][0]['detail']}"
            await interaction.followup.send(f"{interaction.user.mention} something went wrong:\n{response}")
        else:
            response = f"Successfully ran the command!\n**RESULTS**\n{response['data']['attributes']['result']}"
            await interaction.followup.send(f"{response}")


    @ app_commands.command(name="bojack_mute", description="mutes a player")
    @ app_commands.checks.has_any_role(*roles)
    @ app_commands.guild_only()
    @app_commands.choices(server=[*server_names])
    async def bojack_mute(self, interaction: discord.Interaction, server: app_commands.Choice[str], steamid: str, time: str, reason: str):
        await interaction.response.defer()
                
        #Setup the BMAPI code
        
        
        #Setup the command and send it
        server_id = server.value
        command = f"mute {steamid} {time} {reason}"
        response = await self.bmapi.server.console_command(server_id=server_id, command=command)
        
        #Grab log channel
        logchannel = self.client.get_channel(self.config['additional']['logchannel'])
        
        #Setup the embed
        embed = discord.Embed(title="Mute Logging", url="", description="A player has been muted.ㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤ")
        embed.add_field(name="Steam ID", value=f"[{steamid}](https://steamcommunity.com/profiles/{steamid})", inline=False)
        embed.add_field(name="Reason", value=f"{reason}", inline=False)
        embed.add_field(name="Length", value=f"{time}", inline=False)
        embed.add_field(name="Requested By", value=f"{interaction.user}", inline=False)
        embed.set_thumbnail(url="https://i.imgur.com/Q7K3dGR.png")
        
        #Send to channels
        await logchannel.send(embed=embed)
        if 'errors' in response:
            response = f"There was an error with that command!\n**RESPONSE**\n{response['errors'][0]['detail']}"
            await interaction.followup.send(f"{interaction.user.mention} something went wrong:\n{response}")
        else:
            response = f"Successfully ran the command!\n**RAW Command**: {response['data']['attributes']['data']['raw']}\n**Result**: {response['data']['attributes']['result']}\n**Success**: {response['data']['attributes']['success']}"
        
        await interaction.followup.send(f"# Command Usage \n{response}")
        
    @rust_mute.error
    async def rust_mute_handler(self, ctx, error):
        if isinstance(error, app_commands.MissingAnyRole):
            await ctx.response.send_message(error, ephemeral=True)
        else:
            await ctx.response.send_message(error, ephemeral=True)
            
    @rust_unmute.error
    async def rust_unmute_handler(self, ctx, error):
        if isinstance(error, app_commands.MissingAnyRole):
            await ctx.response.send_message(error, ephemeral=True)
        else:
            await ctx.response.send_message(error, ephemeral=True)
            
    @bojack_mute.error
    async def bojack_mute_handler(self, ctx, error):
        if isinstance(error, app_commands.MissingAnyRole):
            await ctx.response.send_message(error, ephemeral=True)
        else:
            await ctx.response.send_message(error, ephemeral=True)
async def setup(client):
    await client.add_cog(mutes_slashes(client))