import requests
import os
from time import sleep
from time import time
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

        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Request failed: {e}")
            sleep(120)
            continue

        if response.status_code == 200:
            data = response.json()

            # ranks in the guild, used to access the members of each rank and their stats
            keys = ['owner', 'chief', 'strategist', 'captain', 'recruiter', 'recruit']
            unix = time()

            rows = []

            # iterating through each rank and then each member of that rank to access their stats and save them to the player_stats dictionary
            for rank in keys:

                for member in data['members'][rank]:
                    xp = data['members'][rank][member]['contributed']
                    notg = data['members'][rank][member]['guildRaids']['list']['Nest of the Grootslangs']
                    nol = data['members'][rank][member]['guildRaids']['list']['Orphion\'s Nexus of Light']
                    tcc = data['members'][rank][member]['guildRaids']['list']['The Canyon Colossus']
                    tna = data['members'][rank][member]['guildRaids']['list']['The Nameless Anomaly']
                    rows.append((unix, member, xp, notg, nol, tcc, tna))

        else:
            print(f"Error: {response.status_code}")
        
        try:
            cursor.executemany('INSERT INTO player_stats (date, name, xp, notg, nol, tcc, tna) VALUES (%s, %s, %s, %s, %s, %s, %s)', rows)
            cursor.execute('DELETE FROM player_stats WHERE date < %s', (unix - 1209600,))
        except mysql.connector.Error as err:
            print(f"Database error: {err}")

        conn.commit()
        sleep(120)

main()
