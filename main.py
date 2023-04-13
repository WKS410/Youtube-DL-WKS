# -*- coding: utf-8 -*-
# Module: Youtube-DL-WKS
# Created on: 13/04/2023
# Authors: -∞WKS∞-#3982
# Version: 1.1.0


import pytube
import argparse
import subprocess
import requests


# Define arguments
parser = argparse.ArgumentParser(description='Download a YouTube video.')
parser.add_argument('url', metavar='url', type=str, help='YouTube video URL')
parser.add_argument('-r', '--resolution', metavar='resolution', type=str, help='Video resolution')
parser.add_argument('-a', '--audio', action='store_true', help='Download audio only')
parser.add_argument('-o', '--output', metavar='path', type=str, help='Output path')
parser.add_argument('-c', '--cookies', metavar='cookies_file', type=str, help='Path to cookies file')

# Parse arguments
args = parser.parse_args()

try:
    # Create YouTube object
    yt = pytube.YouTube(args.url)

    # Set cookies if provided
    if args.cookies:
        with open(args.cookies, 'r') as f:
            cookies = {}
            for line in f.read().split(';'):
                if '=' in line:
                    name, value = line.strip().split('=', 1)
                    cookies[name] = value
        yt = pytube.YouTube(args.url, cookies=cookies)

    # Get video stream
    streams = yt.streams.filter(progressive=True, file_extension='mp4')
    if args.resolution:
        streams = streams.filter(res=args.resolution)

    # Sort by file size (largest to smallest)
    streams = sorted(streams, key=lambda x: -x.filesize)

    # Check for audio only and no audio stream
    if args.audio and not streams[0].includes_audio_track:
        raise ValueError("Cannot download audio only for this video.")

    # Download video or audio if available
    if args.audio:
        audio_path = "{}.m4a".format(yt.title)
        audio_url = streams[0].audio_url
        r = requests.head(audio_url, allow_redirects=True)
        subprocess.run(["aria2c", "-x", "16", "-s", "16", "-o", audio_path, audio_url])
        logging.info("Audio downloaded to {}".format(audio_path))
    else:
        video_path = "{}.mp4".format(yt.title)
        video_url = streams[0].url
        r = requests.head(video_url, allow_redirects=True)
        subprocess.run(["aria2c", "-x", "16", "-s", "16", "-o", video_path, video_url])
        logging.info("Video downloaded to {}".format(video_path))

    # Show download complete message
    logging.info("Download complete!")
except pytube.exceptions.RegexMatchError:
    logging.error("Could not find video at provided URL.")
except ValueError as e:
    logging.error(str(e))
except Exception:
    logging.error("An error occurred during video download.")