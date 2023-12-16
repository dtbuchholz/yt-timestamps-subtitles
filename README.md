# YouTube Timestamp & Subtitle Generator

[![License](https://img.shields.io/github/license/tablelandnetwork/docs.svg)](./LICENSE)
[![standard-readme compliant](https://img.shields.io/badge/standard--readme-OK-green.svg)](https://github.com/RichardLitt/standard-readme)

> YouTube video timestamp and subtitle generator using OpenAI's whisper and GPT-4 models

## Table of Contents

- [Background](#background)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Background

This provides a simple script to generate YouTube timestamps and subtitles from a video file using OpenAI's whisper and GPT-4 models. It outputs a `segments.srt` file and a `timestamps.txt` file, which can be used when uploading a new video to YouTube. You can see an example of what the output looks like with an uploaded video [here](https://www.youtube.com/watch?v=-MUq--Nrd0c).

## Usage

First, make sure you set up an OpenAI API key/organization and set it as an environment variable in your `.env` file:

```shell
OPENAI_API_ORG=your_org_id
OPENAI_API_KEY=your_api_key
```

Then, clone this repo and install dependencies:

```shell
git clone https://github.com/dtbuchholz/yt-timestamps-subtitles.git
python -m venv env
source env/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

The dependencies include:

- `whisper`: OpenAI's whisper model for transcribing an `mp4` file's subtitles (`.srt` format).
- `openai`: Generate YouTube timestamps from the whisper model's output.
- `moviepy`: Used for utility function to get video duration and pass it to the prompt.
- `dotenv`: Load environment variables from `.env` file for the OpenAI API key and organization ID.

Lastly, run the script, passing a path to your video file:

```shell
python3 main.py --file /path/to/video.mp4
```

The output will generate a `segments.srt` file for subtitles with something like the following:

```txt
1
00:00:00,000 --> 00:00:09,599
The Tableland Studio is designed to let you interact with the Tableland network from the comfort of a web application or CLI to create teams, projects and tables.

2
00:00:10,599 --> 00:00:14,480
There are a number of features that it offers and we'll walk through them here today.
```

And a corresponding YouTube timestamps will take this into consideration when creating the `timestamps.txt` file to be used in the YouTube video's description:

```txt
0:00 - Introduction to Tableland Studio
0:15 - Logging into Tableland web app
```

## Contributing

PRs accepted. Please review additional details explained in the [contributing](https://docs.tableland.xyz/contribute) section of the docs site.

Small note: If editing the README, please conform to the [standard-readme](https://github.com/RichardLitt/standard-readme) specification.

## License

MIT AND Apache-2.0, © 2021-2022 Tableland Network Contributors
