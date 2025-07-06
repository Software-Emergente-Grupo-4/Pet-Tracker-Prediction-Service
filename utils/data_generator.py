import pymysql.cursors
from faker import Faker
from datetime import datetime, timedelta
import random

# Conexión a la base de datos
conn = pymysql.connect(
    host='localhost',
    user='root',
    password='root',
    database='pet_tracker_fake',
    cursorclass=pymysql.cursors.DictCursor,
    ssl={"tls":True}
)

fake = Faker()
device_record_id = "9a344bf6-2390-4c34-92bb-c170d39b76a4"
hoy = datetime.today()

# Generar datos para los últimos 365 días
dias_a_insertar = 365
registros_por_dia = 5  # Puedes variar esto

try:
    with conn.cursor() as cursor:
        for i in range(dias_a_insertar):
            fecha = hoy - timedelta(days=i)
            for _ in range(registros_por_dia):
                # Genera una hora aleatoria dentro del día
                created_at = fake.date_time_between_dates(
                    datetime_start=fecha.replace(hour=0, minute=0, second=0),
                    datetime_end=fecha.replace(hour=23, minute=59, second=59)
                )
                bpm = random.randint(60, 100)         # bpm realistas
                spo2 = random.randint(92, 100)        # spo2 realistas

                sql = """
                INSERT INTO health_measure (created_at, updated_at, bpm, spo2, device_record_id)
                VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (created_at, created_at, bpm, spo2, device_record_id))

        conn.commit()
        print("✅ Datos insertados correctamente.")

finally:
    conn.close()
