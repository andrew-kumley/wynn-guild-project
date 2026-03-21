import requests
import os
import time
from datetime import datetime
from dotenv import load_dotenv

def main():

    load_dotenv()
    # environment variables, may be edited locally or in the .env file
    token = os.getenv("TOKEN")
    guild = os.getenv("GUILD")
    headers = {
            "Authorization": f"Bearer {token}",
        }
    url = f"https://api.wynncraft.com/v3/guild/{guild}"

    # creating an empty dictionary to store player stats, keyed by player name and with values of a list of their stats
    # TODO: remove the need for this by saving all data to a database
    player_stats = {}

    # main loop, runs every 2 minutes to update player stats
    while True:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            members = []

            # ranks in the guild, used to access the members of each rank and their stats
            keys = ['owner', 'chief', 'strategist', 'captain', 'recruiter', 'recruit']
            print(datetime.now())

            # iterating through each rank and then each member of that rank to access their stats and save them to the player_stats dictionary
            for rank in keys:
                members += data["members"][rank]

                for member in members:
                    xp = data['members'][rank][member]['contributed']
                    notg = data['members'][rank][member]['guildRaids']['list']['Nest of the Grootslangs']
                    nol = data['members'][rank][member]['guildRaids']['list']['Orphion\'s Nexus of Light']
                    tcc = data['members'][rank][member]['guildRaids']['list']['The Canyon Colossus']
                    tna = data['members'][rank][member]['guildRaids']['list']['The Nameless Anomaly']

                    player_stats[member] = [xp, notg, nol, tcc, tna]
                    print(f"{member:<20}\t{player_stats[member]}")

                members = []
            print()
        else:
            print(f"Error: {response.status_code}")

        time.sleep(120)

main()
