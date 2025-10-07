import csv

import psycopg2
from faker import Faker

fake = Faker()

fields = ["name", "email", "ref", "create_uid", "create_date", "write_uid", "write_date"]
fields_required_possible = {
    # if you database has installed a few extra modules it could raise not null errors
    # Better define a manual default
    "autopost_bills": "ask",
    "group_rfq": "default",
    "group_on": "default",
}


def generate_csv(file_name, total_records, cr):
    cr.execute(
        """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'res_partner'
          AND table_schema = 'public'
          AND is_nullable = 'NO'
          AND column_default IS NULL
    """
    )
    columns_not_null = [i[0] for i in cr.fetchall()]
    missing_columns = set(columns_not_null) - set(fields)
    missing_columns_wo_default = missing_columns - set(fields_required_possible)
    if missing_columns_wo_default:
        raise UserWarning("There are missing columns %s" % missing_columns)
    missing_columns_w_default = missing_columns & set(fields_required_possible)
    fields.extend(missing_columns_w_default)
    with open(file_name, mode="w") as file:
        writer = csv.writer(file)
        writer.writerow(fields)

        create_uid = 1
        write_uid = 1

        for _ in range(total_records):
            name = fake.name()
            email = fake.email()
            ref = fake.random_number(digits=10, fix_len=True)
            default_values = [fields_required_possible[col] for col in missing_columns_w_default]
            writer.writerow([name, email, ref, create_uid, "NOW()", write_uid, "NOW()"] + default_values)


def copy_from_csv(file_name, cr):
    with open(file_name) as file:
        cr.copy_expert(
            "COPY res_partner(%s) FROM STDIN WITH CSV HEADER" % ",".join(fields),
            file,
        )


def main():
    fname = "partners.csv"
    # Use PG* environment variables to connect to database
    conn = psycopg2.connect()
    cursor = conn.cursor()
    try:
        generate_csv(fname, total_records=2000000, cr=cursor)
        copy_from_csv(fname, cr=cursor)
        conn.commit()
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    main()
