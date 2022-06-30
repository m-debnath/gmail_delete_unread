#! ./venv/Scripts/python.exe

from __future__ import annotations, print_function

from typing import Any

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from pandas import DataFrame
from yaml import Loader, load

from gmail_auth import authorize

_black_list: list[str] | None
_gmail_service: Any


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


def check_if_spam(row) -> int:
    global _black_list
    if _black_list:
        for each in _black_list:
            if each.lower() in row["From"].lower() or each.lower() in row["Text"].lower():
                return 1
    return 0


def delete_email_thread(row) -> None:
    global _gmail_service
    _gmail_service.users().threads().trash(userId="me", id=row["Thread Id"]).execute()


def delete_blocked_threads() -> int:
    """Delete threads with From address matching a black list.
    Return: int
    """
    global _black_list, _gmail_service
    creds = authorize()
    _black_list = get_black_list()
    if not _black_list:
        input("Press Enter to continue...")
        return 1

    try:
        # create gmail api client
        _gmail_service = build("gmail", "v1", credentials=creds)

        threads = _gmail_service.users().threads().list(userId="me", q="is:unread").execute().get("threads", [])
        emails: DataFrame = DataFrame({"Thread Id": [], "From": [], "Text": [], "Spam": []})
        for thread in threads:
            tdata = _gmail_service.users().threads().get(userId="me", id=thread["id"]).execute()
            msg = tdata["messages"][0]["payload"]
            headers = {header["name"]: header["value"] for header in msg["headers"]}
            emails.loc[len(emails)] = [thread["id"], headers["From"], headers["Subject"], 0]
        emails["Spam"] = emails.apply(lambda row: check_if_spam(row), axis=1)
        spam_emails: DataFrame = emails[emails["Spam"] == 1]
        spam_emails.apply(lambda row: delete_email_thread(row), axis=1)
        print(f"{spam_emails.shape[0]} conversation(s) moved to trash.")
        input("Press Enter to continue...")
        return 0

    except HttpError as error:
        print(f"An error occurred: {error}")
        input("Press Enter to continue...")
        return 1


if __name__ == "__main__":
    exit(delete_blocked_threads())
