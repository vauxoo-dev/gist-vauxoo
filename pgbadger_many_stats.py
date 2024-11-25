# pylint: disable=print-used

import csv
import os

from bs4 import BeautifulSoup

directory = os.path.expanduser("~/Downloads/pgbadger")
csv_file = os.path.join(directory, "pgbadger_top_queries.csv")


def get_top_queries_from_file(file_path, top=3):
    result = []
    with open(file_path) as file:
        soup = BeautifulSoup(file, "lxml")
        table = soup.find(id="time-consuming-queries-table")

        rows = table.find_all("tr") if table else []
        rank = 1
        for row in rows:
            cols = row.find_all("td")
            if not cols or len(cols) < 6:
                continue
            result.append(
                {
                    "rank": rank,
                    "total_duration": cols[1].get_text(strip=True),
                    "times_executed": cols[2].get_text(strip=True).replace("Details", ""),
                    "avg_duration": cols[5].get_text(strip=True),
                    "query": cols[6].find_all("div")[0].get_text().strip("\n "),
                    "filename": os.path.basename(file_path),
                }
            )
            rank += 1
            if len(result) >= top:
                break
    return result


def main():
    with open(csv_file, mode="w") as file:
        writer = csv.DictWriter(
            file, fieldnames=["rank", "total_duration", "times_executed", "avg_duration", "filename", "query"]
        )
        writer.writeheader()
        for filename in os.listdir(directory):
            if not filename.endswith(".html"):
                continue
            file_path = os.path.join(directory, filename)

            top_queries = get_top_queries_from_file(file_path)

            writer.writerows(top_queries)

    print(f"csv file generated {csv_file}")


if __name__ == "__main__":
    main()
