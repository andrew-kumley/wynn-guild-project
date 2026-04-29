import requests
import os
from time import sleep
from time import time
from dotenv import load_dotenv
import mysql.connector

def main():
    load_dotenv()
    
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

            keys = ['owner', 'chief', 'strategist', 'captain', 'recruiter', 'recruit']
            unix = time()

            rows = []
            for rank in keys:
                for member in data['members'][rank]:
                    xp = data['members'][rank][member]['contributed']
                    try:
                        notg = data['members'][rank][member]['globalData']['guildRaids']['list']['Nest of the Grootslangs']
                        nol = data['members'][rank][member]['globalData']['guildRaids']['list']['Orphion\'s Nexus of Light']
                        tcc = data['members'][rank][member]['globalData']['guildRaids']['list']['The Canyon Colossus']
                        tna = data['members'][rank][member]['globalData']['guildRaids']['list']['The Nameless Anomaly']
                        wtp = data['members'][rank][member]['globalData']['guildRaids']['list']['The Wartorn Palace']
                        playtime = data['members'][rank][member]['globalData']['playtime']
                        wars = data['members'][rank][member]['globalData']['wars']
                    except KeyError:
                        notg = None
                        nol = None
                        tcc = None
                        tna = None
                        wtp = None
                        playtime = None
                        wars = None
                    
                    rows.append((unix, member, xp, notg, nol, tcc, tna, wtp, playtime, wars))

        else:
            print(f"Error: {response.status_code}")
        
        try:
            cursor.executemany('INSERT INTO player_stats (date, name, xp, notg, nol, tcc, tna, wtp, playtime, wars) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', rows)
            cursor.execute('DELETE FROM player_stats WHERE date < %s', (unix - 1209600,))
        except mysql.connector.Error as err:
            print(f"Database error: {err}")

        conn.commit()
        sleep(120)

main()