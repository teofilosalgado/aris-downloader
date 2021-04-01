from __future__ import annotations

import time
from argparse import ArgumentParser

from clients import SeleniumClient


def main():
    parser: ArgumentParser = ArgumentParser(
        description="Traverse ARIS item descending tree and store resulting graph in an SQLite database."
    )
    parser.add_argument(
        "base_url",
        metavar="base_url",
        type=str,
        help="Base URL before '/'.",
    )
    parser.add_argument(
        "database_name",
        metavar="database_name",
        type=str,
        help="Database name as you can see in the right corner of ARIS connect.",
    )
    parser.add_argument(
        "username",
        metavar="username",
        type=str,
        help="User authentication name.",
    )
    parser.add_argument(
        "password",
        metavar="password",
        type=str,
        help="User authentication password.",
    )
    parser.add_argument(
        "item_url",
        metavar="item_url",
        type=str,
        help="Unique root item URL. Normally found after '/#insights/item/'.",
    )
    parser.add_argument(
        "item_title",
        metavar="item_title",
        type=str,
        help="Item title. You can copy it from your browser.",
    )
    args = parser.parse_args()

    with SeleniumClient(
        args.base_url, args.database_name, args.username, args.password
    ) as client:
        start = time.time()
        client.traverse(args.item_url, args.item_title)
        end = time.time()
        print(f"Elapsed time: {end - start} seconds")


if __name__ == "__main__":
    main()
