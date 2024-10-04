"""Transcribe a video file and generate YouTube timestamps."""

from sys import exit
from argparse import ArgumentParser
from os import getenv

from dotenv import find_dotenv, load_dotenv
from moviepy.editor import VideoFileClip
from openai import OpenAI
from whisper import load_model, DecodingOptions

# Load env vars for OpenAI API and organization
load_dotenv(find_dotenv())
openai_api_key = getenv("OPENAI_API_KEY")
openai_api_org = getenv("OPENAI_API_ORG")
if not openai_api_key or not openai_api_org:
    exit("Environment variables not found: OPENAI_API_KEY and/or OPENAI_API_ORG")

# Load OpenAI API client
client = OpenAI(
    organization=openai_api_org,
    api_key=openai_api_key,
)

# Load whisper model
options = DecodingOptions(fp16=False, language="en")
whisper_model = load_model("base.en")


def cmd() -> str:
    """
    Parse command line arguments for video file path.

    Returns
    -------
        str
            Path to video file.
    """

    parser = ArgumentParser(
        description="Transcribe a video file and generate YouTube timestamps."
    )
    parser.add_argument(
        "--file",
        type=str,
        default=None,
        help="Input video file path to transcribe.",
    )
    args = parser.parse_args()
    return args.file


def get_video_duration(video_path: str) -> str:
    """
    Get the duration of a video file.

    Parameters
    ----------
        video_path : str
            Path to video file.

    Returns
    -------
        str
            Duration of video file in HH:MM:SS format.
    """
    with VideoFileClip(video_path) as video:
        duration = video.duration
        hours = int(duration // 3600)
        minutes = int((duration % 3600) // 60)
        seconds = int(duration % 60)
        return f"{hours}:{minutes}:{seconds}"


def transcribe(video_path) -> str:
    """
    Transcribe a video file with the whisper model.

    Parameters
    ----------
        video_path : str
            Path to video file.

    Returns
    -------
        str
            Transcription of video file.
    """
    try:
        with VideoFileClip(video_path) as video:
            if video.audio is None:
                raise ValueError("File does not contain an audio stream.")

        result = whisper_model.transcribe(video_path, **options.__dict__, verbose=False)
        return result
    except ValueError as e:
        print(f"Error transcribing video: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error transcribing video: {e}")
        return None


def segments_to_srt(segments) -> str:
    """
    Convert segments to SRT format.

    Parameters
    ----------
        segments : list
            List of segments from whisper model.

    Returns
    -------
        str
            SRT formatted segments.
    """
    srt_text = []
    for i, segment in enumerate(segments):
        # SRT index starts from 1
        srt_index = i + 1
        srt_text.append(str(srt_index))

        # Formatting start and end times
        start_time = format_time(segment["start"])
        end_time = format_time(segment["end"])
        srt_text.append(f"{start_time} --> {end_time}")

        # Adding text
        srt_text.append(segment["text"].strip())

        # Add an empty line after each segment
        srt_text.append("")

    return "\n".join(srt_text)


def format_time(seconds) -> str:
    """Convert time in seconds to SRT time format"""
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    milliseconds = int((seconds - int(seconds)) * 1000)
    return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d},{milliseconds:03d}"


def generate_summary(transcript: str, length: int) -> str:
    """
    Generate a summary of the transcript using OpenAI's gpt-4 model as YouTube
    timestamps.

    The summary should be a set of YouTube timestamps that can be used as key
    points across all segments.

    Parameters
    ----------
        transcript : str
            Transcript of the video.
        length : int

    Returns
    -------
        str
            Summary of the transcript as YouTube timestamps.
    """
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": """You are a helpful assistant that will summarize
                           audio transcripts and generate YouTube video
                           timestamps for important topics in the transcript.
                           You will adhere to YouTube video timestamp format.
                           The format expects the timestamps to be formatted as
                           `HH:MM:SS` for videos longer than an hour and as `MM:SS`
                           for videos less than an hour. For example, a video
                           with a length of 00:59:59 (provided as `HH:MM:SS`)
                           would have timestamps formatted as `MM:SS`, with a min
                           value of 00:00 and a max value of 59:59. 
                           
                           The timestamps should consider segments in the
                           transcript but not include each segment but only
                           summarize the general themes. The timestamps should
                           not exceed the full length of the video. Segments
                           will be provided in SRT format `HH:MM:SS,MS -->
                           HH:MM:SS,MS` to assist with YouTube timestamp chapter
                           generation. You should not generate a summary for
                           each SRT segment, but rather, generate a set of
                           summary YouTube timestamps that can be used as key
                           points across all segments. 
                           
                           For example, a video with
                           a length of 00:20:00 might have 8-10 total timestamps
                           with the timestamp format `MM:SS`. It might have a
                           set of input text that follows the format: 
                           ```
                           1
                           00:00:00,000 --> 00:01:00,000
                           This is the first sentence of the first segment.
                           
                           2
                           00:01:00,000 --> 00:01:15,000
                           This is the second sentence of the second segment.
                           
                           3
                           00:01:15,000 --> 00:02:20,000
                           This is the third sentence of the third segment.
                           ```
                           Which would result in a set of timestamps like:
                           ```
                           0:00 - Introduction
                           1:15 - Topic overview
                           etc.
                           ```
                """,
            },
            {
                "role": "user",
                "content": f"The following transcript is for a video of length {length}:\n {transcript}",
            },
        ],
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()


def main():
    """
    Transcribe a video file and generate YouTube timestamps.
    - Get the video file path from the command line.
    - Get the duration of the video file.
    - Transcribe the video file.
    - Convert the segments to SRT format.
    - Generate a summary of the transcript as YouTube timestamps.
    """
    try:
        # Get video file path
        video_path = cmd()
        duration = get_video_duration(video_path)
        print(f"Video duration: {duration}")

        # Transcribe video and convert to SRT
        transcript = transcribe(video_path)
        if transcript is None:
            raise Exception("Cannot proceed without a valid transcription.")

        segments = segments_to_srt(transcript["segments"])
        # Write segments to file
        segments_file = "segments.srt"
        with open(segments_file, "w") as f:
            print(f"Writing segments SRT file to: {segments_file}")
            f.write(segments)
        summary = generate_summary(segments, duration)

        # Write summary to file
        timestamps_file = "timestamps.txt"
        with open(timestamps_file, "w") as f:
            print(f"Writing YouTube timestamps file to: {timestamps_file}")
            f.write(summary)
    except Exception as e:
        exit(f"Error processing video: {e}")


if __name__ == "__main__":
    main()
