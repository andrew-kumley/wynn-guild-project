import os
# from time import sleep
from dotenv import load_dotenv
import mysql.connector


class logic:
    def __init__(self):
        load_dotenv()

        self.conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )

        self.cursor = self.conn.cursor(buffered=True)

    def get_all_player_diffs(self):
        try:
            self.cursor.execute("""
                SELECT name, xp_diff, notg_diff, nol_diff, tcc_diff, tna_diff, wtp_diff, playtime_diff, wars_diff
                FROM (
                    SELECT 
                        name,
                        xp - LAG(xp) OVER (PARTITION BY name ORDER BY date) AS xp_diff,
                        notg - LAG(notg) OVER (PARTITION BY name ORDER BY date) AS notg_diff,
                        nol - LAG(nol) OVER (PARTITION BY name ORDER BY date) AS nol_diff,
                        tcc - LAG(tcc) OVER (PARTITION BY name ORDER BY date) AS tcc_diff,
                        tna - LAG(tna) OVER (PARTITION BY name ORDER BY date) AS tna_diff,
                        wtp - LAG(wtp) OVER (PARTITION BY name ORDER BY date) AS wtp_diff,
                        playtime - LAG(playtime) OVER (PARTITION BY name ORDER BY date) AS playtime_diff,
                        wars - LAG(wars) OVER (PARTITION BY name ORDER BY date) AS wars_diff,
                        ROW_NUMBER() OVER (PARTITION BY name ORDER BY date DESC) AS rn
                    FROM player_stats
                ) t
                WHERE rn = 1
            """)

            results = self.cursor.fetchall()

            players = []
            for row in results:
                players.append({
                    "name": row[0],
                    "xp": row[1] or 0,
                    "notg": row[2] or 0,
                    "nol": row[3] or 0,
                    "tcc": row[4] or 0,
                    "tna": row[5] or 0,
                    "wtp": row[6] or 0,
                    "playtime": row[7] or 0,
                    "wars": row[8] or 0,
                })

            return players

        except mysql.connector.Error as err:
            print(f"Database error: {err}")
            return []

l = logic()
print(l.get_all_player_diffs())