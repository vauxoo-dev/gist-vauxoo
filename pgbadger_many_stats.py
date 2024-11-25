# pylint: disable=print-used
import csv
import os

from lxml import html

directory = os.path.expanduser("~/Downloads/pgbadger")
csv_file = os.path.join(directory, "pgbadger_top_queries3.csv")


def get_top_queries_from_file(file_path, top=3):
    result = []
    with open(file_path) as file:
        tree = html.parse(file)
        for row in tree.xpath('//*[@id="time-consuming-queries-table"]//tr')[1:]:
            cols = row.xpath(".//td")
            if len(cols) < 6:
                continue
            rank = int(cols[0].text_content().strip())
            result.append(
                {
                    "rank": rank,
                    "total_duration": cols[1].text_content().strip(),
                    "times_executed": cols[2].text_content().replace("Details", "").strip(),
                    "avg_duration": cols[5].text_content().strip(),
                    "query": "".join(cols[6].xpath("./div[1]//text()")).strip("\n "),
                    "filename": os.path.basename(file_path),
                }
            )
            if rank >= top:
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

    print(f"CSV file generated: {csv_file}")


if __name__ == "__main__":
    main()
