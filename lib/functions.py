# Third-party imports
import asyncio
import aiohttp
import json
import validators

from dataclasses import dataclass
# Standard library imports
from datetime import datetime, timezone, timedelta
from unicodedata import name

from lib.battlemetrics import Battlemetrics

with open("./json/config.json", "r") as config_file:
    config = json.load(config_file)


@dataclass
class Playerids():
    _id: int = None
    steamid: str = None
    bmid: int = None


@dataclass
class Playerstats():
    _id: int = None
    steamid: str = None
    bmid: int = None
    kills_day: int = 0
    kills_week: int = 0
    kills_two_weeks: int = 0
    deaths_day: int = 0
    deaths_week: int = 0
    deaths_two_weeks: int = 0


@dataclass
class Notes():
    _id: int = None
    noteid: int = None
    bmid: int = None
    orgid: int = None
    notemakerid: int = None
    orgname: str = None
    note: str = None
    notemakername: str = None


@dataclass
class Serverbans():
    _id: int = None
    bmid: int = None
    steamid: str = None
    bandate: str = None
    expires: str = None
    banid: int = None
    bannote: str = None
    serverid: int = None
    servername: str = None
    banner: str = None
    banreason: str = None
    uuid: str = None
    orgid: int = None


@dataclass
class Player():
    _id: int = None
    battlemetrics_id: int = None
    steam_id: int = None
    profile_url: str = None
    avatar_url: str = None
    player_name: str = None
    names: list = None
    account_created: str = None
    playtime: int = None
    playtime_training: int = None
    rustbanned: bool = None
    rustbancount: int = None
    banned_days_ago: int = None
    flags: str = None
    notes: list = None
    server_bans: list = None
    related_players: list = None
    limited: bool = None
    community_banned: bool = False
    game_ban_count: int = 0
    vac_banned: bool = False
    vacban_count: int = 0
    last_ban: int = 0


battlemetrics_token = config['tokens']['battlemetrics_token']

api = Battlemetrics(battlemetrics_token)


async def get_player_info(player_id):
    
    player = await api.player.info(player_id)
    if not player:
        return
    player = await sort_player(player)
    await asyncio.sleep(0.1)  # Slight sleep so we don't get rate limited.
    player_flags = await api.player.flags(player_id)
    if player_flags:
        player.flags = await sort_flags(player_flags)
    else:
        player.flags = None
    await asyncio.sleep(0.1)  # Slight sleep so we don't get rate limited.
    await api.notes.list()
    player_notes = await api.player.notes(player_id)
    if player_notes:
        if player_notes['data']:
            player.notes = await sort_notes(player_notes)
    else:
        player.notes = None
    await asyncio.sleep(0.1)  # Slight sleep so we don't get rate limited.
    
    player_server_bans = await api.ban_list.search(player_id=player_id)
    if player_server_bans:
        if player_server_bans.get('meta'):
            if player_server_bans['meta']['total']:
                player.server_bans = await sort_server_bans(player_server_bans)
        else:
            player.server_bans = None
    else:
        player.server_bans = None

    # for name in player.names:
    #    await db.save_name(bmid=player.battlemetrics_id, playername=name)
    return player


async def sort_server_bans(player_server_bans: dict) -> list:
    server_bans = []

    for data in player_server_bans['data']:
        if str(data['relationships']['organization']['data']['id']) == str(config['additional']['organization_id']):
            server_ban = Serverbans()
            server_ban.bandate = data['attributes']['timestamp']
            server_ban.banid = data['id']
            server_ban.bannote = data['attributes']['note']
            server_ban.banreason = data['attributes']['reason']
            server_ban.bmid = data['relationships']['player']['data']['id']
            if data['relationships'].get('server'):
                server_ban.serverid = data['relationships']['server']['data']['id']
            else:
                server_ban.serverid = 0

            server_ban.orgid = data['relationships']['organization']['data']['id']
            server_ban.uuid = data['attributes']['uid']
            if data['attributes']['expires']:
                server_ban.expires = data['attributes']['expires']
            else:
                server_ban.expires = "Never"
            banner_id = 0
            if data['relationships'].get('user'):
                banner_id = data['relationships']['user']['data']['id']
            else:
                server_ban.banner = "Server Ban"
            for identifier in data['attributes']['identifiers']:
                if identifier['type'] == "steamID":
                    if identifier.get('metadata'):
                        server_ban.steamid = identifier['metadata']['profile']['steamid']
                    else:
                        server_ban.steamid = identifier['identifier']

            for included in player_server_bans['included']:
                if included['type'] == "server":
                    if included['id'] == server_ban.serverid:
                        server_ban.servername = included['attributes']['name']
                if included['type'] == "user":
                    if included['id'] == banner_id:
                        server_ban.banner = included['attributes']['nickname']
            server_bans.append(server_ban)
    return server_bans


async def sort_notes(player_notes: dict) -> list:
    notes = []
    for data in player_notes['data']:
        if data['relationships'].get('user'):
            note = Notes(
                noteid=data['id'],
                bmid=data['relationships']['player']['data']['id'],
                orgid=data['relationships']['organization']['data']['id'],
                notemakerid=data['relationships']['user']['data']['id'],
                note=data['attributes']['note'],
                notemakername="Unknown"
            )
        else:
            note = Notes(
                noteid=data['id'],
                bmid=data['relationships']['player']['data']['id'],
                orgid=data['relationships']['organization']['data']['id'],
                notemakerid=data['relationships']['organization']['data']['id'],
                note=data['attributes']['note'],
                notemakername="Unknown"
            )
        for included in player_notes['included']:
            if included['type'] == "user":
                if included['id'] == note.notemakerid:

                    note.notemakername = included['attributes']['nickname']
            if included['type'] == "organization":
                if included['id'] == note.orgid:
                    note.orgname = included['attributes']['name']
        
        if str(note.orgid) == str(config['additional']['organization_id']):
            notes.append(note)
    return notes


async def sort_flags(player_flags: dict) -> str:
    flags = {}
    for included in player_flags['included']:
        if str(included['relationships']['organization']['data']['id']) == str(config['additional']['organization_id']):
            org_id = str(included['relationships']['organization']['data']['id'])
            flag_id = str(included['id'])

            if org_id in flags:
                flags[org_id]['flags'].append(included['attributes']['name'])
            else:
                flags[org_id] = {}
                flags[org_id] = {
                    'flags': [included['attributes']['name']],
                    'flag_id': flag_id
                }
    return flags


async def sort_player(player: dict) -> Player:
    player_data = {}
    player_data['battlemetrics_id'] = player['data']['id']
    player_data['player_name'] = player['data']['attributes']['name']
    player_data['playtime'] = 0
    player_data['playtime_training'] = 0
    player_data['names'] = []

    vacban_count = 0
    vac_banned = False
    last_ban = 0
    community_banned = False
    game_ban_count = 0

    for included in player['included']:
        if included['type'] == "identifier":
            if included['attributes']['type'] == "steamID":
                player_data['steam_id'] = included['attributes']['identifier']
                if included['attributes'].get('metadata'):
                    if included['attributes']['metadata'].get('profile'):
                        player_data['avatar_url'] = included['attributes']['metadata']['profile']['avatarfull']
                        # player_data['account_created'] = included['attributes']['metadata']['profile']['timecreated']
                        player_data['limited'] = False
                        if included['attributes']['metadata']['profile'].get('isLimitedAccount'):
                            player_data['limited'] = included['attributes']['metadata']['profile']['isLimitedAccount']
                        player_data['profile_url'] = included['attributes']['metadata']['profile']['profileurl']
                    if included['attributes']['metadata'].get('rustBans'):
                        player_data['rustbanned'] = included['attributes']['metadata']['rustBans']['banned']
                        player_data['rustbancount'] = included['attributes']['metadata']['rustBans']['count']
                        given_time = datetime.strptime(
                            f"{included['attributes']['metadata']['rustBans']['lastBan']}", "%Y-%m-%dT%H:%M:%S.%fZ")
                        current_time = datetime.utcnow()
                        player_data['banned_days_ago'] = (
                            current_time - given_time).days

            if included['attributes']['type'] == "name":
                player_data['names'].append(
                    included['attributes']['identifier'])

        if included['type'] == "server":
            training_names = ["rtg", "aim", "ukn", "arena",
                              "combattag", "training", "aimtrain", "train", "arcade", "bedwar", "bekermelk", "escape from rust"]
            for name in training_names:
                if name in included['attributes']['name']:
                    player_data['playtime_training'] += included['meta']['timePlayed']
            player_data['playtime'] += included['meta']['timePlayed']
    player_data['playtime'] = player_data['playtime'] / 3600
    player_data['playtime'] = round(player_data['playtime'], 2)
    player_data['playtime_training'] = player_data['playtime_training'] / 3600
    player_data['playtime_training'] = round(
        player_data['playtime_training'], 2)
    player_data['last_ban'] = last_ban
    player_data['community_banned'] = community_banned
    player_data['game_ban_count'] = game_ban_count
    player_data['vac_banned'] = vac_banned
    player_data['vacban_count'] = vacban_count
    myplayer = Player(**player_data)
    return myplayer

async def get_id_from_steam(url: str) -> int:
    """Takes the URL (well part of it) and returns a steam ID"""
    url = (
        f"https://api.steampowered.com/ISteamUser/ResolveVanityURL/v1/?format=json&"
        f"key={config['tokens']['steam_token']}&vanityurl={url}&url_type=1"
    )
    async with aiohttp.ClientSession(
        headers={"Authorization": config['tokens']['steam_token']}
    ) as session:
        async with session.get(url=url) as r:
            response = await r.json()
    if response['response'].get('steamid'):
        return response["response"]["steamid"] if response["response"]["steamid"] else 0
    else:
        return 0


async def get_player_ids(submittedtext: str) -> Playerids or None:
    steamid = 0
    if validators.url(submittedtext):
        mysplit = submittedtext.split("/")
        if mysplit[3] == "id":
            steamid = await get_id_from_steam(mysplit[4])
        if mysplit[3] == "profiles":
            steamid = mysplit[4]
    else:
        if len(submittedtext) != 17:
            return None
        steamid = submittedtext

    if not steamid:
        return None
    
    playerids = Playerids()
    if steamid:
        playerids.steamid = steamid
        results = await api.player.match_identifiers(identifier=steamid, type="steamID")
        if results.get('data'):
            playerids.bmid = results['data'][0]['relationships']['player']['data']['id']
        else:
            playerids.bmid = 0
    return playerids

async def kda_two_weeks(bmid: int) -> dict:
    weekago = datetime.now(
        timezone.utc) - timedelta(hours=168)
    weekago = str(weekago).replace("+00:00", "Z:")
    weekago = weekago.replace(" ", "T")
    url = "https://api.battlemetrics.com/activity"
    params = {
        "version": "^0.1.0",
        "tagTypeMode": "and",
        "filter[timestamp]": str(weekago),
        "filter[types][whitelist]": "rustLog:playerDeath:PVP",
        "filter[players]": f"{bmid}",
        "include": "organization,user",
        "page[size]": "100"
    }
    return await api.helpers._make_request(method="GET", url=url, data=params)


async def player_stats(bmid: int) -> Playerstats or None:
    kda_results = await kda_two_weeks(bmid)
    stats = Playerstats()
    if kda_results:
        if kda_results.get('data'):
            for stat in kda_results['data']:
                mytimestamp = stat['attributes']['timestamp'][:10]
                mytimestamp = datetime.strptime(mytimestamp, '%Y-%m-%d')
                days_ago = (datetime.now() - mytimestamp).days
                if stat['attributes']['data'].get('killer_id'):
                    if stat['attributes']['data']['killer_id'] == int(bmid):
                        if days_ago <= 1:
                            stats.kills_day += 1
                        if days_ago <= 7:
                            stats.kills_week += 1
                        if days_ago <= 14:
                            stats.kills_two_weeks += 1
                    else:
                        if days_ago <= 1:
                            stats.deaths_day += 1
                        if days_ago <= 7:
                            stats.deaths_week += 1
                        if days_ago <= 14:
                            stats.deaths_two_weeks += 1
    if kda_results:
        if kda_results.get('links'):
            while kda_results["links"].get("next"):
                myextension = kda_results["links"]["next"]
                kda_results = await api.helpers._make_request(method="GET", url=myextension)
                if kda_results:
                    for stat in kda_results['data']:
                        mytimestamp = stat['attributes']['timestamp'][:10]
                        mytimestamp = datetime.strptime(
                            mytimestamp, '%Y-%m-%d')
                        days_ago = (datetime.now() - mytimestamp).days
                        if stat['attributes']['data'].get('killer_id'):
                            if stat['attributes']['data']['killer_id'] == int(bmid):
                                if days_ago <= 1:
                                    stats.kills_day += 1
                                if days_ago <= 7:
                                    stats.kills_week += 1
                                if days_ago <= 14:
                                    stats.kills_two_weeks += 1
                            else:
                                if days_ago <= 1:
                                    stats.deaths_day += 1
                                if days_ago <= 7:
                                    stats.deaths_week += 1
                                if days_ago <= 14:
                                    stats.deaths_two_weeks += 1
    return stats


async def activity_logs(steamid:str):
    combatlog = None
    teaminfo = None
    for server in config['servers']:
        combatlog = await api.server.console_command(server_id=server['id'], command=f"combatlog {steamid}")
                
        if combatlog.get('errors'):
            print("\n")
            print(f"Unable to grab combatlog. Server information: ID: {server['id']}, Name: {server['name']}, IP: {server['ip']}")
            combatlog = None
            continue
        elif not combatlog.get('data'):
            print("\nSomething went critically wrong. Review this data to determine the cause of the issue.\n")
            print("Response from server:")
            print(json.dumps(combatlog, indent=4))
            print("\n")
            print("Server attempted to grab data from:")
            print(f"Server information: ID: {server['id']}, Name: {server['name']}, IP: {server['ip']}")
            combatlog = None
            continue
        
        combatlog = combatlog['data']['attributes']['result']
        if 'invalid player' in combatlog.lower():
            combatlog = None
            continue
    
    for server in config['servers']:
        teaminfo = await api.server.console_command(server_id=server['id'], command=f"teaminfo {steamid}")
        if teaminfo.get('errors'):
            print("\n")
            print(f"Unable to grab teaminfo. Server information: ID: {server['id']}, Name: {server['name']}, IP: {server['ip']}")
            teaminfo = None
            continue
        elif not teaminfo.get('data'):
            print("\nSomething went critically wrong. Review this data to determine the cause of the issue.\n")
            print("Response from server:")
            print(json.dumps(teaminfo, indent=4))
            print("\n")
            print("Server attempted to grab data from:")
            print(f"Server information: ID: {server['id']}, Name: {server['name']}, IP: {server['ip']}")
            teaminfo = None
            continue
        teaminfo = teaminfo['data']['attributes']['result']
        if not "player is not in a team" in teaminfo.lower():
            break
        else:
            teaminfo = None
              
    response = {}
    response['combatlog'] = combatlog
    response['teaminfo'] = teaminfo
    return response


async def activity_logs_search(search:str):
    return await api.activity_logs(filter_search=search)
