import json
import os
import re
import traceback
from typing import TYPE_CHECKING

import requests
from dotenv import load_dotenv
from flask import Flask, render_template, request
from psnawp_api import PSNAWP
from psnawp_api.core import PSNAWPAuthenticationError, PSNAWPNotFound
from trello import TrelloClient

if TYPE_CHECKING:
    from trello.card import Card

app = Flask(__name__)


load_dotenv()
trello_client = TrelloClient(
    api_key=os.environ["TRELLO_API_KEY"], token=os.environ["TRELLO_TOKEN"]
)


@app.route("/")
def index():
    return render_template(
        "index.html", input_missing=False, search_result=None, msg=""
    )


# Get all labels from the trello card
def get_all_labels(trello_card: Card):
    # If there are no labels for card
    if trello_card.labels is None:
        return "BLACKLISTED"
    # Otherwise return all label names in string
    labels = ""
    for label in trello_card.labels:
        labels += label.name + ", "
    return labels[:-2]


# Removes the archived cards from list
def delete_archived_cards_and_check_desc(search_result, search_query):
    for card in search_result:
        # closed means the card is archived
        if card.closed:
            search_result.remove(card)
        # Double check to make sure that search query is in card description
        elif (
            re.search(
                rf"\b{search_query}$", card.description.replace("\\", ""), re.I | re.M
            )
            is None
        ):
            search_result.remove(card)
    return search_result


# Searches in trello board using trello api and return the search result in a list
# The list is empty if there are no search results
def search_in_blacklist(search_query: str):
    search_result = list()
    # escapes the special characters so the search result is exact not from wildcard (e.g '-')
    search_result = trello_client.search(
        query=re.escape(search_query), cards_limit=10, models=["cards"]
    )
    search_result_escaped_underscore = list()
    # If underscore is in search query, we need to search it escaped and non escaped
    if "_" in search_query:
        search_result_escaped_underscore = trello_client.search(
            query=re.escape(search_query.replace("_", "\\_")),
            cards_limit=10,
            models=["cards"],
        )
    # Adding results from both searches
    search_result = search_result + search_result_escaped_underscore
    # Removing duplicate search results
    search_result = list(set(search_result))
    search_result = delete_archived_cards_and_check_desc(search_result, search_query)
    return search_result


def get_xbox_info(gamertag):
    auth_headers = {"X-Authorization": os.environ["XAPI_KEY"]}
    params = {"gt": gamertag}
    response = requests.get(
        "https://xbl.io/api/v2/friends/search", headers=auth_headers, params=params
    )
    response.raise_for_status()
    json_response = response.json()
    return json_response["profileUsers"][0]["id"]


def get_psn_info(gamertag):
    """
    Gets the account id from gamertag

    :param gamertag: Gamertag of a user
    :return: account id

    :raises: PSNAWPNotFound: If the gamertag is not found.
    """
    api = PSNAWP(os.environ["NPSSO_COOKIE"])
    user = api.user(online_id=gamertag)
    return user.account_id


@app.route("/search_result", methods=["GET", "POST"])
def search_blacklist():
    # If user hasn't entered anything in the form
    if not request.form["redditname"].strip() and not request.form["gamertag"].strip():
        return render_template(
            "index.html",
            input_missing=True,
            search_result=None,
            msg="Enter reddit username or gamertag",
        )
    err_msg = ""
    # If user gave gamertag
    if request.form["gamertag"].strip():
        # search in trello as it is
        blacklist_search_result = search_in_blacklist(request.form["gamertag"].strip())
        # If xbox is selected as platform
        if request.form["platform"] == "xbox":
            try:
                account_id = get_xbox_info(request.form["gamertag"].strip())
                blacklist_search_result += search_in_blacklist(account_id)
                blacklist_search_result = list(set(blacklist_search_result))
            except KeyError:
                err_msg = (
                    f"The gamertag of the user has been changed. {request.form['gamertag'].strip()} is not "
                    f"affiliated with any XBOX account as of now. The card(s) below may or may not have to latest "
                    f"gamertag."
                )
            except json.JSONDecodeError:
                err_msg = (
                    "Non XBOX 360 compliant GT was provided. The search result was performed without the aid "
                    "of XBOX API. The results may be outdated as offenders tend to change their gamertag after "
                    "a while."
                )
            except Exception:
                err_msg = traceback.format_exc()
        # If psn is selected as platform
        elif request.form["platform"] == "ps":
            try:
                account_id = get_psn_info(request.form["gamertag"].strip())
                blacklist_search_result += search_in_blacklist(account_id)
                blacklist_search_result = list(set(blacklist_search_result))
            except PSNAWPAuthenticationError:
                err_msg = "NPSSO Code Expired. Please contact moderators."
            except PSNAWPNotFound:
                err_msg = (
                    f"The gamertag of the user has been changed. {request.form['gamertag'].strip()} is not "
                    f"affiliated with any PSN account as of now. The card(s) below may or may not have to "
                    f"latest gamertag."
                )
            except Exception:
                err_msg = traceback.format_exc()
    else:
        # If reddit username was giver
        blacklist_search_result = search_in_blacklist(
            request.form["redditname"].strip()
        )

    # We only need the urls for the embedded cards
    blacklist_search_result = [
        (get_all_labels(card), card.url) for card in blacklist_search_result
    ]
    return render_template(
        "index.html",
        input_missing=False,
        search_result=blacklist_search_result,
        msg=err_msg,
    )


if __name__ == "__main__":
    app.run()
