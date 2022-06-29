from __future__ import print_function

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from yaml import load, Loader

from gmail_auth import authorize


def get_black_list() -> list[str] | None:
    data = None
    with open("blacklist.yaml", "r") as stream:
        data = load(stream, Loader=Loader)
    return data["BLACK_LIST"]


def show_chatty_threads():
    """Display threads with long conversations(>= 3 messages)
    Return: None

    Load pre-authorized user credentials from the environment.
    TODO(developer) - See https://developers.google.com/identity
    for guides on implementing OAuth2 for the application.
    """
    creds = authorize()
    black_list = get_black_list()

    try:
        # create gmail api client
        service = build("gmail", "v1", credentials=creds)

        threads = service.users().threads().list(userId="me", q="is:unread").execute().get("threads", [])
        for thread in threads:
            tdata = service.users().threads().get(userId="me", id=thread["id"]).execute()
            msg = tdata["messages"][0]["payload"]
            headers = {header["name"]: header["value"] for header in msg["headers"]}
            subject = headers["Subject"]
            from_address = headers["From"]
            for each in black_list:
                if each.lower() in from_address.lower():
                    print(f"{subject} from {from_address}")

    except HttpError as error:
        print(f"An error occurred: {error}")


if __name__ == "__main__":
    show_chatty_threads()
