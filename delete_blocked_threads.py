from __future__ import print_function

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from yaml import Loader, load

from gmail_auth import authorize


def get_black_list() -> list[str] | None:
    data = None
    with open("blacklist.yaml", "r") as stream:
        data = load(stream, Loader=Loader)
    return data["BLACK_LIST"]


def delete_blocked_threads() -> int:
    """Display threads with long conversations(>= 3 messages)
    Return: None

    Load pre-authorized user credentials from the environment.
    TODO(developer) - See https://developers.google.com/identity
    for guides on implementing OAuth2 for the application.
    """
    creds = authorize()
    black_list = get_black_list()
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
