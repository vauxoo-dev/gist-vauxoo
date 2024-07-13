import csv

import psycopg2
from faker import Faker

fake = Faker()


def generate_csv(file_name, total_records):
    with open(file_name, mode="w") as file:
        writer = csv.writer(file)
        writer.writerow(["name", "email", "ref", "create_uid", "create_date", "write_uid", "write_date"])

        create_uid = 1
        write_uid = 1

        for _ in range(total_records):
            name = fake.name()
            email = fake.email()
            ref = fake.random_number(digits=10, fix_len=True)
            writer.writerow([name, email, ref, create_uid, "NOW()", write_uid, "NOW()"])


def copy_from_csv(file_name):
    # Use PG* environment variables to connect to database
    conn = psycopg2.connect()
    cursor = conn.cursor()
    try:
        with open(file_name) as file:
            cursor.copy_expert(
                """
                COPY res_partner(name, email, ref, create_uid, create_date, write_uid, write_date)
                FROM STDIN WITH CSV HEADER
                """,
                file,
            )
            conn.commit()
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    fname = "partners.csv"
    # generate_csv(fname, total_records=2000000)
    copy_from_csv(fname)
