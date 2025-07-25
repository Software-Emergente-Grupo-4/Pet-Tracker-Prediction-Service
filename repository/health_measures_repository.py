import pymysql.cursors
from dotenv import load_dotenv
import os

load_dotenv()

def get_daily_averages_for_last_n_months(n_months: int, device_record_id: str) -> list:

    conn = pymysql.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE"),
        cursorclass=pymysql.cursors.DictCursor,
        ssl={"tls": True}
    )

    try:
        with conn.cursor() as cursor:
            query = """
            SELECT
            DATE(created_at) AS fecha,
            ROUND(AVG(bpm), 2) AS avg_bpm,
            ROUND(AVG(spo2), 2) AS avg_spo2
            FROM health_measure
            WHERE
            device_record_id = %s
            AND created_at >= DATE_SUB(CURDATE(), INTERVAL %s MONTH)
            GROUP BY fecha
            ORDER BY fecha ASC;
            """
            cursor.execute(query, (device_record_id, n_months))
            results = cursor.fetchall()
            return results

    finally:
        conn.close()


if __name__ == "__main__":
    results = get_daily_averages_for_last_n_months(6, "9a344bf6-2390-4c34-92bb-c170d39b77a4")
    print(len(results))
