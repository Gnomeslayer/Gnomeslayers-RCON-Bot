from discord import app_commands
from discord.ext import commands
import discord
import json
import os

import lib.functions as func
from lib.battlemetrics import Battlemetrics

class Profile(commands.Cog):
    def __init__(self, client):
        print("[Cog] Profile has been initiated")
        self.client = client

    with open("./json/config.json", "r") as f:
        config = json.load(f)
        
    bmapi = Battlemetrics(config['tokens']['battlemetrics_token'])

    roles = config['cogs']['profile']['allowed_roles']

    server_names = []
    ban_reasons = []

    for server in config['servers']:
        server_names.append(app_commands.Choice(
            name=f"{server['name']}", value=f"{server['id']}"))

    @ app_commands.command(name="profile", description="Retrieves a players profile for review.")
    @ app_commands.checks.has_any_role(*roles)
    @ app_commands.guild_only()
    async def profile(self, interaction: discord.Interaction, steam_id_or_url:str):
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send("Give me a moment to grab all the information. If the user has been very active it may take a moment to grab all their kill data.", ephemeral=True)
        
        player_ids = await func.get_player_ids(steam_id_or_url)
        
        if not player_ids.bmid:
            await interaction.followup.send("Unable to locate that user. You sure they're on your server?", ephemeral=True)
            return
        player_profile = await func.get_player_info(player_id=player_ids.bmid)
        activity_logs = await func.activity_logs(steamid=player_ids.steamid)
        player_stats = await func.player_stats(bmid=player_ids.bmid)
        embed = discord.Embed(title=f"Displaying player information.",
                              description=f"# {player_profile.player_name}\nSteam ID: [{player_ids.steamid}]({player_profile.profile_url})", color=int(self.config['cogs']['color'], base=16)) 
        embed.set_footer(text="Created by Gnomeslayer#5551",
                         icon_url="https://cdn.discordapp.com/attachments/1072438897847586837/1086533712881139765/RAH_LOGO.png")
        embed.set_thumbnail(url=player_profile.avatar_url)
        embed.add_field(
            name="Hours", value=f"Total Time Played: {player_profile.playtime}\nTraining time:{player_profile.playtime_training}\nActual Servers: {player_profile.playtime - player_profile.playtime_training}", inline=True)

        

        if player_profile.notes:
            embed.add_field(name="Notes", value=f"{len(player_profile.notes)} note(s) on profile.", inline=True)
        else:
            embed.add_field(name="Notes", value="No notes on profile.", inline=True)
        
        embed.add_field(name="Stats (1 week period)",
                        value=f"Total kills/deaths today: {player_stats.kills_day}/{player_stats.deaths_day}\nTotal kills/deaths this week: {player_stats.kills_week}/{player_stats.deaths_week}", inline=False)

        embed.add_field(name="Limited",
                        value=f"```{player_profile.limited}```", inline=False)

        def filter_reason(reason):
            reason = reason.replace("}", "")
            reason = reason.replace("{", "")
            reason = reason.replace("]", "")
            reason = reason.replace("[", "")
            reason = reason.replace("|", "")
            reason = reason.replace("discord.gg", "discordlink")
            reason = reason.replace("https://", "")
            reason = reason.replace("http://", "")
            return reason
        bancount = 0
        serverbans = None
        if player_profile.server_bans:
            for serverban in player_profile.server_bans:
                serverban.banreason = filter_reason(serverban.banreason)
                if bancount <= 5:
                    if serverbans:
                        serverbans += f"\n➣ [{serverban.banreason}](https://www.battlemetrics.com/rcon/bans/edit/{serverban.banid})"
                        bancount += 1
                    else:
                        serverbans = f"➣ [{serverban.banreason}](https://www.battlemetrics.com/rcon/bans/edit/{serverban.banid})"
                        bancount += 1
                else:
                    break

        if not serverbans:
            embed.add_field(name=f"Server Bans - Total: 0, Showing: 0",
                                value=f"No serverbans on this users profile.", inline=False)
        else:
            embed.add_field(name=f"Server Bans - Total: {len(player_profile.server_bans)}, Showing: {bancount}",
                                value=f"{serverbans}", inline=False)

        rustbanned_msg = "Rustbans: Not rustbanned."
        if player_profile.rustbanned:
            rustbanned_msg = f"Rustbans: {player_profile.rustbancount} | {player_profile.banned_days_ago} days ago"

        community_msg = "Community bans: No community Bans"
        if player_profile.community_banned:
            community_msg = f"Community Bans: {player_profile.game_ban_count}"
        vac_msg = "VAC Bans: No VAC bans"
        if player_profile.vac_banned:
            vac_msg = f"VAC Bans: {player_profile.vacban_count}"

        lastban = "Days since last non rust ban: Never"
        if player_profile.vac_banned or player_profile.community_banned:
            lastban = f"Days since last non rust ban: {player_profile.last_ban}"
        embed.add_field(name="Rustbans, community bans and other bans",
                        value=f"{rustbanned_msg}\n{community_msg}\n{vac_msg}\n{lastban}", inline=False)

        content = None
        if player_profile.limited:
            content = "**THIS IS A LIMITED ACCOUNT.**"
        
        pfb = ProfileButtons()
        pfb.notes = player_profile.notes
        pfb.serverbans  = player_profile.server_bans
        pfb.combatlog = activity_logs['combatlog']
        pfb.teaminfo = activity_logs['teaminfo']
        pfb.playerprofile = player_profile
        await interaction.followup.send(content=content, embed=embed, view=pfb, ephemeral=True)

    @profile.error
    async def profile_handler(self, ctx, error):
        if isinstance(error, app_commands.MissingAnyRole):
            await ctx.response.send_message(error, ephemeral=True)
        else:
            await ctx.response.send_message(error, ephemeral=True)
            
class ProfileButtons(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.notes = None
        self.serverbans = None
        self.combatlog = None
        self.teaminfo = None
        self.playerprofile = None
    with open('./json/config.json', 'r') as f:
        config = json.load(f)

    @discord.ui.button(label="View Notes", style=discord.ButtonStyle.blurple, row=1)
    async def view_notes(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.notes:
            embed = self.set_notes_embed()
            note_buttons = NotesButtons()
            note_buttons.notes = self.notes
            await interaction.response.send_message(f"Viewing note 1 of {len(self.notes)}", view=note_buttons, embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message("No notes to show. Such a shame.", ephemeral=True)

    @discord.ui.button(label="View Serverbans", style=discord.ButtonStyle.green, row=1)
    async def view_serverbans(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.serverbans:
            embed = self.set_serverbans_embed()
            serverban_buttons = ServerBansButtons()
            serverban_buttons.serverbans = self.serverbans
            await interaction.response.send_message(f"Viewing serverban 1 of {len(self.serverbans)}", embed=embed, view=serverban_buttons, ephemeral=True)
        else:
            await interaction.response.send_message("There are no serverbans to display", ephemeral=True)
            
    @discord.ui.button(label="View Combatlog", style=discord.ButtonStyle.green, row=1)
    async def view_combatlog(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send("Retrieving combatlog information and links. Give me a moment.", ephemeral=True)
        if self.combatlog:
            embed = await self.set_combatlog_embed()
            with open(f"{self.playerprofile.steam_id}.txt", "w") as f:
                f.write(self.combatlog)
                f.close()
            await interaction.followup.send(content=f"combatlog scan of <https://steamcommunity.com/profiles/{self.playerprofile.steam_id}>", file=discord.File(f"{self.playerprofile.steam_id}.txt"), embed=embed, ephemeral=True)
            os.remove(f"{self.playerprofile.steam_id}.txt")
        else:
            await interaction.followup.send("There is no combatlog to display", ephemeral=True)
            
    @discord.ui.button(label="View Teaminfo", style=discord.ButtonStyle.green, row=1)
    async def view_teaminfo(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send("Retrieving team information and links. Give me a moment.", ephemeral=True)
        
        if self.teaminfo:
            embed = await self.set_teaminfo_embed()
            await interaction.followup.send(embed=embed, ephemeral=True)
        else:
            await interaction.followup.send("There is no team information to display.", ephemeral=True)

    async def set_combatlog_embed(self):
        data = self.combatlog
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
        result_dict.reverse()
        player_details = {}
        embed_description = None

        combatlog_fields = 0
        for item in result_dict:
            if combatlog_fields == 2:
                break
            time = item['time']
            attacker = None
            target = None
            id = item['id']
            if item['attacker'] == "you":
                attacker = f"[You](https://steamcommunity.com/profiles/{self.playerprofile.steam_id})"
            else:
                if item['attacker'] == "player":
                    if id in player_details:
                        if not player_details[id]['bmid'] == 0:
                            attacker = f"[{id}](https://www.battlemetrics.com/rcon/players/{player_details[id]['bmid']})"
                        else:
                            attacker = f"{id}"
                    else:
                        bmprofile = await func.activity_logs_search(search=id)
                        player_details[id] = {}
                        try:
                            player_details[id]['bmid'] = int(
                                bmprofile['data'][0]['relationships']['players']['data'][0]['id'])
                        except:
                            player_details[id]['bmid'] = 0

                        if player_details[id]['bmid']:
                            attacker = f"[{id}](https://www.battlemetrics.com/rcon/players/{player_details[id]['bmid']})"
                        else:
                            attacker = f"{id}"

            if item['target'] == "you":
                target = f"[You](https://steamcommunity.com/profiles/{self.playerprofile.steam_id})"
            else:
                if item['target'] == "player":
                    if id in player_details:
                        if not player_details[id]['bmid'] == 0:
                            target = f"[{id}](https://www.battlemetrics.com/rcon/players/{player_details[id]['bmid']})"
                        else:
                            target = f"{id}"
                    else:
                        bmprofile = await func.activity_logs_search(search=id)
                        player_details[id] = {}
                        try:
                            player_details[id]['bmid'] = int(
                                bmprofile['data'][0]['relationships']['players']['data'][0]['id'])
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
                    break
                
        embed = discord.Embed(
            title=f"Combatlog for {self.playerprofile.player_name}", description=embed_description)
        return embed
    
    async def set_teaminfo_embed(self):
        team = self.teaminfo.split()
        team_links = None
        teammate_count = 0
        embed = discord.Embed(
            title=f"Team information for {self.playerprofile.player_name}")
        for teammate in team:
            if teammate.isnumeric():
                if len(teammate) == 17:
                    bmapi = Battlemetrics(self.config['tokens']['battlemetrics_token'])
                    user_ids = await bmapi.player.match_identifiers(identifier=teammate, type="steamID")
                    battlemetrics_id = user_ids['data'][0]['relationships']['player']['data']['id']
                    if teammate_count == 4:
                        embed.add_field(
                            name=f"Team Links", value=f"\n{team_links[:1020]}", inline=False)
                        team_links = None
                    teammate_count += 1
                    if team_links:
                        team_links += f"\n[Battlemetrics](https://www.battlemetrics.com/rcon/players/{battlemetrics_id}) - [Steam](http://steamcommunity.com/profiles/{teammate}) - {user_ids['data'][0]['attributes']['metadata']['profile']['personaname']}"
                    else:
                        team_links = f"[Battlemetrics](https://www.battlemetrics.com/rcon/players/{battlemetrics_id}) - [Steam](http://steamcommunity.com/profiles/{teammate}) - {user_ids['data'][0]['attributes']['metadata']['profile']['personaname']}"
        
        if team_links:
            embed.add_field(name=f"Team Links",
                            value=f"{team_links[:1020]}", inline=False)
        else:
            embed.add_field(name=f"Team Links",
                            value=f"Player is not in a team.", inline=False)
        embed.add_field(
            name=f"Raw Team Information", value=f"```perl\n{self.teaminfo}```", inline=False)
        return embed
        
    
    def set_notes_embed(self):
        note = self.notes[0]
        embed = discord.Embed(title=f"Displaying player notes information.",
                              description=f" :warning: **This information is not to be shared, if you share this information with an unauthorized user your access may be revoked.** :warning:", color=int(self.config['cogs']['color'], base=16))
        embed.set_footer(text="Created by Gnomeslayer#5551",
                         icon_url="https://cdn.discordapp.com/attachments/1072438897847586837/1086533712881139765/RAH_LOGO.png")
        embed.add_field(
            name="Note ID",
            value=f"{note.noteid}",
            inline=True,
        )
        embed.add_field(
            name="Organization info",
            value=f"org id: {note.orgid}\nOrg Name: {note.orgname}", inline=True,
        )
        embed.add_field(
            name="Note Maker",
            value=f"{note.notemakername}",
            inline=True,
        )
        note_msg = note.note
        if len(note_msg) >= 900:
            note_msg = note_msg[:250]
            note_msg += "...(Truncated)"
        embed.add_field(name="Note", value=f"```{note_msg}```", inline=False)
        return embed

    def set_serverbans_embed(self):
        ban = self.serverbans[0]
        embed = discord.Embed(title=f"Displaying player serverban information.",
                              description=f" :warning: **This information is not to be shared, if you share this information with an unauthorized user your access may be revoked.** :warning:", color=int(self.config['cogs']['color'], base=16))
        embed.set_footer(text="Created by Gnomeslayer#5551",
                         icon_url="https://cdn.discordapp.com/attachments/1072438897847586837/1086533712881139765/RAH_LOGO.png")
        embed.add_field(
            name="Banner",
            value=f"{ban.banner}",
            inline=True,
        )
        embed.add_field(
            name="Links",
            value=f"[Ban](https://www.battlemetrics.com/rcon/bans/edit/{ban.banid})\n[Server](https://www.battlemetrics.com/servers/rust/{ban.serverid})",
            inline=True,
        )
        embed.add_field(
            name="Dates",
            value=f"```Issued: {ban.bandate}\nExpires: {ban.expires}```", inline=False,
        )

        embed.add_field(
            name="Ban reason",
            value=f"```{ban.banreason}```",
            inline=False,
        )
        ban_msg = ban.bannote
        if ban_msg:
            if len(ban_msg) >= 900:
                ban_msg = ban_msg[:500]
                ban_msg += "...(Truncated)"
        else:
            ban_msg = "No note"
        embed.add_field(name="Note", value=f"```{ban_msg}```", inline=False)
        return embed

class ServerBansButtons(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.serverbans = None
        self.page_number = 0

    with open('./json/config.json', 'r') as f:
        config = json.load(f)

    @discord.ui.button(label="Previous Ban", style=discord.ButtonStyle.red)
    async def previous_ban(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.page_number == 0:
            self.page_number = len(self.serverbans) - 1
        else:
            self.page_number -= 1
        embed = self.set_serverbans_embed(self.page_number)
        await interaction.response.edit_message(content=f"Viewing serverban {self.page_number + 1} of {len(self.serverbans)}", embed=embed, view=self)

    @discord.ui.button(label="Send as file", style=discord.ButtonStyle.blurple)
    async def send_file(self, interaction: discord.Interaction, button: discord.ui.Button):
        theban = self.serverbans[self.page_number]
        theban = {
            "bmid": theban.bmid,
            "steamid": theban.steamid,
            "bandate": theban.bandate,
            "expires": theban.expires,
            "banid": theban.banid,
            "serverid": theban.serverid,
            "servername": theban.servername,
            "banner": theban.banner,
            "banreason": theban.banreason,
            "uuid": theban.uuid,
            "bannote": theban.bannote

        }

        with open(f"{interaction.user.id}_serverbans_file.json", "w") as f:
            f.write(json.dumps(theban, indent=4))
        await interaction.response.send_message(file=discord.File(f"{interaction.user.id}_serverbans_file.json"), ephemeral=True)
        os.remove(f"{interaction.user.id}_serverbans_file.json")

    @discord.ui.button(label="Next Ban", style=discord.ButtonStyle.green)
    async def next_ban(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.page_number >= (len(self.serverbans) - 1):
            self.page_number = 0
        else:
            self.page_number += 1
        embed = self.set_serverbans_embed(self.page_number)
        await interaction.response.edit_message(content=f"Viewing serverban {self.page_number + 1} of {len(self.serverbans)}", embed=embed, view=self)

    def set_serverbans_embed(self, page_number: int):
        ban = self.serverbans[page_number]
        embed = discord.Embed(title=f"Displaying player serverban information.",
                              description=f" :warning: **This information is not to be shared, if you share this information with an unauthorized user your access may be revoked.** :warning:", color=int(self.config['cogs']['color'], base=16))
        embed.set_footer(text="Created by Gnomeslayer#5551",
                         icon_url="https://cdn.discordapp.com/attachments/1072438897847586837/1086533712881139765/RAH_LOGO.png")
        embed.add_field(
            name="Banner",
            value=f"{ban.banner}",
            inline=True,
        )
        embed.add_field(
            name="Links",
            value=f"[Ban](https://www.battlemetrics.com/rcon/bans/edit/{ban.banid})\n[Server](https://www.battlemetrics.com/servers/rust/{ban.serverid})",
            inline=True,
        )
        embed.add_field(
            name="Dates",
            value=f"```Issued: {ban.bandate}\nExpires: {ban.expires}```", inline=False,
        )

        embed.add_field(
            name="Ban reason",
            value=f"```{ban.banreason}```",
            inline=False,
        )
        ban_msg = ban.bannote
        if ban_msg:
            if len(ban_msg) >= 900:
                ban_msg = ban_msg[:500]
                ban_msg += "...(Truncated)"
        else:
            ban_msg = "No note"
        embed.add_field(name="Note", value=f"```{ban_msg}```", inline=False)
        return embed


class NotesButtons(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.notes = None
        self.page_number = 0
    with open('./json/config.json', 'r') as f:
        config = json.load(f)

    @discord.ui.button(label="Previous Note", style=discord.ButtonStyle.red)
    async def previous_note(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.page_number == 0:
            self.page_number = len(self.notes) - 1
        else:
            self.page_number -= 1
        embed = self.set_notes_embed(self.page_number)
        await interaction.response.edit_message(content=f"Viewing note {self.page_number + 1} of {len(self.notes)}", embed=embed, view=self)

    @discord.ui.button(label="Send as file", style=discord.ButtonStyle.blurple)
    async def send_file(self, interaction: discord.Interaction, button: discord.ui.Button):
        thenote = self.notes[self.page_number]
        thenote = {
            "noteid": thenote.noteid,
            "bmid": thenote.bmid,
            "orgid": thenote.orgid,
            "notemakerid": thenote.notemakerid,
            "orgname": thenote.orgname,
            "notemakername": thenote.notemakername,
            "note": thenote.note
        }

        with open(f"{interaction.user.id}_note_file.json", "w") as f:
            f.write(json.dumps(thenote, indent=4))
        await interaction.response.send_message(file=discord.File(f"{interaction.user.id}_note_file.json"), ephemeral=True)
        os.remove(f"{interaction.user.id}_note_file.json")

    @discord.ui.button(label="Next Note", style=discord.ButtonStyle.green)
    async def next_note(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.page_number >= (len(self.notes) - 1):
            self.page_number = 0
        else:
            self.page_number += 1
        embed = self.set_notes_embed(self.page_number)
        await interaction.response.edit_message(content=f"Viewing note {self.page_number + 1} of {len(self.notes)}", embed=embed, view=self)

    def set_notes_embed(self, page_number: int):
        note = self.notes[page_number]
        embed = discord.Embed(title=f"Displaying player notes information.",
                              description=f" :warning: **This information is not to be shared, if you share this information with an unauthorized user your access may be revoked.** :warning:", color=int(self.config['cogs']['color'], base=16))
        embed.set_footer(text="Created by Gnomeslayer#5551",
                         icon_url="https://cdn.discordapp.com/attachments/1072438897847586837/1086533712881139765/RAH_LOGO.png")
        embed.add_field(
            name="Note ID",
            value=f"{note.noteid}",
            inline=True,
        )
        embed.add_field(
            name="Organization info",
            value=f"org id: {note.orgid}\nOrg Name: {note.orgname}", inline=True,
        )
        embed.add_field(
            name="Note Maker",
            value=f"{note.notemakername}",
            inline=True,
        )
        note_msg = note.note
        if len(note_msg) >= 900:
            note_msg = note_msg[:900]
            note_msg += "...(Truncated)"
        embed.add_field(name="Note", value=f"```{note_msg}```", inline=False)
        return embed


async def setup(client):
    await client.add_cog(Profile(client))
