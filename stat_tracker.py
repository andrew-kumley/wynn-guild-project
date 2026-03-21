import requests
import os
from time import sleep
from time import time
from datetime import datetime
from dotenv import load_dotenv
import mysql.connector

def main():

    load_dotenv()
    # environment variables, may be edited locally or in the .env file
    token = os.getenv("TOKEN")
    guild = os.getenv("GUILD")
    headers = {
            "Authorization": f"Bearer {token}",
        }
    url = f"https://api.wynncraft.com/v3/guild/{guild}"

    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

    cursor = conn.cursor(buffered=True)

    # main loop, runs every 2 minutes to update player stats
    while True:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            members = []

            # ranks in the guild, used to access the members of each rank and their stats
            keys = ['owner', 'chief', 'strategist', 'captain', 'recruiter', 'recruit']
            unix = time()
            # iterating through each rank and then each member of that rank to access their stats and save them to the player_stats dictionary
            for rank in keys:
                members += data["members"][rank]

                for member in members:
                    xp = data['members'][rank][member]['contributed']
                    notg = data['members'][rank][member]['guildRaids']['list']['Nest of the Grootslangs']
                    nol = data['members'][rank][member]['guildRaids']['list']['Orphion\'s Nexus of Light']
                    tcc = data['members'][rank][member]['guildRaids']['list']['The Canyon Colossus']
                    tna = data['members'][rank][member]['guildRaids']['list']['The Nameless Anomaly']

                    cursor.execute('INSERT INTO player_stats (date, name, xp, notg, nol, tcc, tna) VALUES (%s, %s, %s, %s, %s, %s, %s)', (unix, member, xp, notg, nol, tcc, tna))
                    conn.commit()

                members = []
        else:
            print(f"Error: {response.status_code}")

        sleep(120)

main()
