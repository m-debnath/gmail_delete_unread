#! ./venv/Scripts/python.exe

from __future__ import annotations, print_function

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from yaml import Loader, load

from gmail_auth import authorize


def get_black_list() -> list[str] | None:
    """Reads the black list.
    Return: list of blocked phrases or None
    """
    data = None
    try:
        with open("blacklist.yaml", "r") as stream:
            data = load(stream, Loader=Loader)
        return data["BLACK_LIST"]
    except FileNotFoundError:
        print("No blacklist configured. Please create a file called blacklist.yaml to continue.")
        return None
    except KeyError:
        print("blacklist.yaml should have BLACK_LIST root element.")
        return None


def delete_blocked_threads() -> int:
    """Delete threads with From address matching a black list.
    Return: int
    """
    creds = authorize()
    black_list = get_black_list()
    if not black_list:
        return 1
    counter = 0

    try:
        # create gmail api client
        service = build("gmail", "v1", credentials=creds)

        threads = service.users().threads().list(userId="me", q="is:unread").execute().get("threads", [])
        for thread in threads:
            tdata = service.users().threads().get(userId="me", id=thread["id"]).execute()
            msg = tdata["messages"][0]["payload"]
            headers = {header["name"]: header["value"] for header in msg["headers"]}
            from_address = headers["From"]
            if black_list:
                for each in black_list:
                    if each.lower() in from_address.lower():
                        service.users().threads().trash(userId="me", id=thread["id"]).execute()
                        counter += 1
                        break
        print(f"{counter} conversation(s) moved to trash.")
        return 0

    except HttpError as error:
        print(f"An error occurred: {error}")
        return 1


if __name__ == "__main__":
    exit(delete_blocked_threads())
