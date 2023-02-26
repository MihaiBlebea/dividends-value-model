import os
import json
from flask import jsonify, request, redirect, url_for
from flask_login import (
    login_required,
    login_user,
    logout_user,
)
from datetime import timedelta
from oauthlib.oauth2 import WebApplicationClient
import requests as re
from src.user import User


# Initiate the auth constants
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", None)
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", None)
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"


client = WebApplicationClient(GOOGLE_CLIENT_ID)


def get_google_provider_cfg():
    return re.get(GOOGLE_DISCOVERY_URL).json()


def login():
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)


def login_callback():
    try:
        # Get authorization code Google sent back to you
        code = request.args.get("code")
        print(code)
        # Find out what URL to hit to get tokens that allow you to ask for
        # things on behalf of a user
        google_provider_cfg = get_google_provider_cfg()
        token_endpoint = google_provider_cfg["token_endpoint"]

        # Prepare and send request to get tokens! Yay tokens!
        token_url, headers, body = client.prepare_token_request(
            token_endpoint,
            authorization_response=request.url,
            redirect_url=request.base_url,
            code=code,
        )
        token_response = re.post(
            token_url,
            headers=headers,
            data=body,
            auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
        )

        # Parse the tokens!
        client.parse_request_body_response(json.dumps(token_response.json()))

        # Now that we have tokens (yay) let's find and hit URL
        # from Google that gives you user's profile information,
        # including their Google Profile Image and Email
        userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
        uri, headers, body = client.add_token(userinfo_endpoint)
        userinfo_response = re.get(uri, headers=headers, data=body)

        # We want to make sure their email is verified.
        # The user authenticated with Google, authorized our
        # app, and now we've verified their email through Google!
        if userinfo_response.json().get("email_verified"):
            unique_id = userinfo_response.json()["sub"]
            users_email = userinfo_response.json()["email"]
            picture = userinfo_response.json()["picture"]
            users_name = userinfo_response.json()["given_name"]
        else:
            return "User email not available or not verified by Google.", 400

        # Create a user in our db with the information provided
        # by Google
        user = User(
            id=unique_id, name=users_name, email=users_email, profile_pic=picture
        )

        print(user)

        # Doesn't exist? Add to database
        if not User.get(unique_id):
            User.create(unique_id, users_name, users_email, picture)

        # Begin user session by logging the user in
        login_user(user, remember=True, duration=timedelta(days=7))

        # Send user back to homepage
        return redirect(url_for("index"))
    except Exception as err:
        print(err)
        return jsonify({"status": "ERROR", "error": str(err)}), 500


@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))
