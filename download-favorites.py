#!/usr/bin/env python3

# https://twitter.com/hovior
# https://mastodon.social/@hovior

import twitter
import os
import urllib
import re

# Get your tokens from https://developer.twitter.com/apps
CONSUMER_KEY = 'your_consumer_key'
CONSUMER_SECRET = 'your_consumer_secret'
ACCESS_TOKEN = 'your_access_token'
ACCESS_TOKEN_SECRET = 'your_token_secret'

# Create an Api instance.
api = twitter.Api(consumer_key=CONSUMER_KEY,
                  consumer_secret=CONSUMER_SECRET,
                  access_token_key=ACCESS_TOKEN,
                  access_token_secret=ACCESS_TOKEN_SECRET,
                  tweet_mode="extended")

# Get first batch of tweets
tweets = api.GetFavorites(count=200)

# Compile regex to extract the local filename from the media URL
regex = re.compile(r"(.*/|\?.*|:.*)")

# Reference to the latest tweet fetched to be used in the next request
max_id = 0

while len(tweets) > 0:

    for t in tweets:

        # Set path to the directory where tweet media will be stored
        media_dir = "tweets/{0}/{1}".format(t.user.screen_name, t.id)

        # Create directory where media will be stored
        if not os.path.exists(media_dir):
            os.makedirs(media_dir)

        # Store tweet text
        tweet = open("{0}/tweet.txt".format(media_dir), "w")
        tweet.write(t.full_text)
        tweet.close()

        # Initialize media URLs and local filename
        media_url = media_path = None

        print("https://twitter.com/{0}/status/{1}".format(t.user.screen_name, t.id), end=" - ")
        if t.media is None:
            # If no media is found, continue to the next tweet
            print("No media found")
            continue

        # Iterate over all media in the tweet
        for media in t.media:

            # Video media
            if media.type == "video" or media.type == "animated_gif":
                # Video media is encoded to different formats
                # We iterate over all the possible formats to chose the one with
                # the highest bitrate
                selected_variant = None
                for variant in media.video_info["variants"]:
                    if "bitrate" in variant and (selected_variant is None or variant["bitrate"] > selected_variant["bitrate"]):
                        selected_variant = variant
                if variant is None:
                    print("The tweet contains a video, but media URL was not found", end=", ")
                else:
                    media_url = selected_variant["url"]

            # Photo media
            elif media.type == "photo":
                media_url = media.media_url + ":large"

            # Other media?
            else:
                print("Unknown media type {0}".format(media.type), end=", ")

            # Finally, if some media was found, download it to a local file
            if media_url is not None:
                media_path = "{0}/{1}".format(media_dir, regex.sub("", media_url))
                if os.path.isfile(media_path):
                    # A destination file with the same name already exists,
                    # we will assume the media is already downloaded
                    print("Already downloaded", end=", ")
                    continue
                urllib.request.urlretrieve(media_url, "{0}/{1}".format(media_dir, regex.sub("", media_url)))
                print("{0}/{1}".format(media_dir, regex.sub("", media_url)), end=", ")

        print("")

    # Twitter API will always return at least one tweet,
    # we will assume we finished when we only got one tweet from Twitter
    if len(tweets) == 1:
        break

    # Otherwise, just fetch more tweets
    max_id=tweets[len(tweets)-1].id_str
    tweets = api.GetFavorites(count=200, max_id=max_id)
