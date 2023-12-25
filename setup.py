
import lib.battlemetrics as bm
import json
import asyncio


print("Welcome to the setup! If you wish to skip this process and get a blank template JSON file now so you can quickly put the data in yourself, type: skip, otherwise, type anything else you feel like. I prefer Penelope.")
user_choice = input("Put your input here: ")

if user_choice.lower() == "skip":
    print(f"You put: {user_choice}")
    print("\nAlright we're all done. Config file has been created. Go check it out! it's here: ./json/config.json")
    input("Press enter to exit.\n")
    
    
    config = {
        "tokens": {
            "discord_token": f"Discord token here",
            "battlemetrics_token": f"Battlemetrics token here",
            "steam_token": f"steam token here"
        },
        "additional": {
            "prefix": "thisdoesntevenwork",
            "application_id": 1234,
            "organization_id": 2134,
            "logchannel": 1234,
            "banlist": "Banlist ID here"
        },
        "cogs": {
            "color": "0x9b59b6",
            "activity_slashes": {
                "allowed_roles": [1234,1234]
            },
            "bans_slashes": {
                "allowed_roles": [1234,1234]
            },
            "clans_slashes": {
                "allowed_roles": [1234,1234]
            },
            "mutes_slashes": {
                "allowed_roles": [1234,1234]
            },
            "notes_slashes": {
                "allowed_roles": [1234,1234]
            },
            "profile": {
                "allowed_roles": [1234,1234]
            },
            "rcon": {
                "allowed_roles": [1234,1234]
            },
            "server_slashes": {
                "allowed_roles": [1234,1234]
            }
        },
        "servers": [
                    {
            'id': 1234,
            'name': "Server name here",
            'ip': "123.45.67.89:1234",
            'status': "Online",
            'active': "Active"
        },
                    {
            'id': 1234,
            'name': "Server name here",
            'ip': "123.45.67.89:1234",
            'status': "Online",
            'active': "Active"
        }],
        "ban_reasons": [
                        {
        "reason": "Reason here",
        "duration": "1d"
    },
                        {
        "reason": "Reason here",
        "duration": "1d"
    }],
        "mute_reasons": [
                        {
        "reason": "Reason here",
        "duration": "1d"
    },
                        {
        "reason": "Reason here",
        "duration": "1d"
    }]
    }

    with open("./json/config.json", "w") as f:
        f.write(json.dumps(config, indent=4))
    
    

else:

    print("Hey! you'll need to visit this site: https://www.battlemetrics.com/developers and create a new token. Just enable everything. you'll want it.")
    battlemetrics_token = input("Submit your token here once created: ")
    print("\n")

    print("Now you'll need a steam token: https://steamcommunity.com/dev")
    steam_token = input("Submit your steam token here: ")
    print("\n")

    print("Now for the fun part, we need to setup your discord bot! Visit this site: https://discord.com/developers/applications")
    print("Create a new application, call it whatever you want, this is what will display for users. Give it a neat image.")
    application_id = int(input("Go ahead and copy the application ID and submit it here: "))
    print("\n")

    print("Now go ahead and click \"BOT\" on the left side navigation. Click the shiny \"Add Bot\" button.\nGrab yourself the discord token.")
    print("Make sure you have the following gateways enabled, it'll save time and hassle later: Authorization Flow, Presence Intent, Server Members Intent, Message Content Intent")
    discord_token = input("Go ahead and plop that bad boy right here: ")
    print("\n")

    print("Go over to OAUTH2 and click \"URL GENERATOR\"\n click \"Bot\" in the list. and select \"Administrator\" from the bot permissions.\nIt's your bot so it's fine.\nNow invite the bot to your server.")
    print("Now we need to retrieve your servers. Make sure discovery is ON for your servers because we're about to do a quick API search to retrieve them.")
    print("The easiest way to find your organization ID is to go to this URL: https://www.battlemetrics.com/rcon/orgs, select your organization, and take the numbers at the end of that URL.")
    organization_id = int(input("Please submit your organization ID: "))
    print("\n")

    print("We're going to need a banlist for when we ban users. So visit this page: https://www.battlemetrics.com/rcon/ban-lists and find the banlist you want to use.")
    print("Click 'View Bans' and in the URL, copy the part that looks like this: '13fff440-0a43-11eb-ae97-3752e91a48dc' (It won't match exactly, since this is mine)")
    banlist = input("Put the banlist here: ")

    api = bm
    asyncio.run(api.setup(token=battlemetrics_token))

    organization_servers = asyncio.run(api.server_list(organization=organization_id))


    servers = []

    for server in organization_servers['data']:
        new_server = {}
        if not server['attributes']['status'] == "dead" and not server['attributes']['rconActive'] == False:
            new_server = {
                'id': server['id'],
                'name': server['attributes']['name'],
                'ip': server['attributes']['ip'],
                'status': server['attributes']['status'],
                'active': server['attributes']['rconActive']
            }
        if new_server:
            servers.append(new_server)

    if not servers:
        print("For some reason I couldn't retrieve any servers. Not to worry. I've put down a basic template for you and you can manually add them yourself! :D")
        new_server = {
                'id': 1234,
                'name': "Server Name",
                'ip': "12.34.56.78:910",
                'status': "Active",
                'active': True
            }
        servers.append(new_server)

    print("Alright I've retrieved your servers. We're almost done!, we'll need a few sample ban reasons and mute reasons, at least 1 of each is required. You can add more manually later!")

    ban_reasons = []

    while True:
        ban_reason = input("Ban Reason: ")
        ban_duration = input("Ban duration (1d, 5d, etc): ")
        ban_reason = {
            "reason": ban_reason,
            "duration": ban_duration
        }
        
        ban_reasons.append(ban_reason)
        add_more = input("Add more? (yes or no): ")
        if add_more.lower() == "no":
            break
        
    print("Now for some mute reasons")

    mute_reasons = []

    while True:
        mute_reason = input("Mute Reason: ")
        mute_duration = input("Mute duration (1m, 1h, etc): ")
        mute_reason = {
            "reason": mute_reason,
            "duration": mute_duration
        }

        mute_reasons.append(mute_reason)
        
        add_more = input("Add more? (yes or no): ")
        if add_more.lower() == "no":
            break
        
    print("Now for some security on the commands! You will need to get the role ID for this part. Right click the role -> Copy ID")
    print("This will restrict each category/command to a specific role. You can manually add/remove/modify later. For now, lets set a default.")
    print("Set to 0/1 to disable. These commands can still be seen (if you didn't delete the respective file) but cannot be used.")
    print("Alternatively you can just delete the file associated with the specific commands.")
    activity_slashes = int(input("Allowed role ID for activity commands: "))
    bans_slashes = int(input("Initial allowed role ID for ban commands: "))
    clans_slashes = int(input("Initial allowed role ID for clan commands: "))
    mutes_slashes = int(input("Initial allowed role ID for mute commands: "))
    notes_slashes = int(input("Initial allowed role ID for notes commands: "))
    profile = int(input("Initial allowed role ID for profile commands: "))
    rcon = int(input("Initial allowed role ID for (raw) RCON commands: "))
    server_slashes = int(input("Initial allowed role ID for server commands: "))

    print("\nAnd finally. This is the last thing. I swears it! The channel where you want logs to go. This is specifically logs for whenever a command is used.")
    print("Right click a channel and copy the ID and paste it below.")
    logchannel = int(input("Log Channel ID: "))

    config = {
        "tokens": {
            "discord_token": f"{discord_token}",
            "battlemetrics_token": f"{battlemetrics_token}",
            "steam_token": f"{steam_token}"
        },
        "additional": {
            "prefix": "thisdoesntevenwork",
            "application_id": application_id,
            "organization_id": organization_id,
            "logchannel": logchannel,
            "banlist": banlist
        },
        "cogs": {
            "color": "0x9b59b6",
            "activity_slashes": {
                "allowed_roles": [activity_slashes]
            },
            "bans_slashes": {
                "allowed_roles": [bans_slashes]
            },
            "clans_slashes": {
                "allowed_roles": [clans_slashes]
            },
            "mutes_slashes": {
                "allowed_roles": [mutes_slashes]
            },
            "notes_slashes": {
                "allowed_roles": [notes_slashes]
            },
            "profile": {
                "allowed_roles": [profile]
            },
            "rcon": {
                "allowed_roles": [rcon]
            },
            "server_slashes": {
                "allowed_roles": [server_slashes]
            }
        },
        "servers": servers,
        "ban_reasons": ban_reasons,
        "mute_reasons": mute_reasons
    }

    with open("./json/config.json", "w") as f:
        f.write(json.dumps(config, indent=4))
    
    print("\nAlright we're all done. Config file has been created. Go check it out! it's here: ./json/config.json")
    input("Press enter to exit.\n")