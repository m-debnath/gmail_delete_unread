# from __future__ import print_function

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from gmail_auth import authorize


def main() -> int:
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    try:
        creds = authorize()
        # Call the Gmail API
        service = build("gmail", "v1", credentials=creds)
        results = service.users().labels().list(userId="me").execute()
        labels = results.get("labels", [])

        if not labels:
            print("No labels found.")
            return 0
        print("Labels:")
        for label in labels:
            print(label["name"])

        return 0

    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f"An error occurred: {error}")
        return 1


if __name__ == "__main__":
    exit(main())
