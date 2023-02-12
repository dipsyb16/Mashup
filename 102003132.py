

import requests
import os
from pydub import AudioSegment
import subprocess
from pytube import YouTube
from pydub import AudioSegment
import pydub
import sys
import re

"""## Get video links from youtube using API"""

# Get video links from youtube

def get_video_links(query, n):
    params = {
        "part": "id",
        "q": query,
        "type": "video",
         "maxResults":50,
        "key": "AIzaSyB5TgGSnbPxPeEmh5XsqYULNVBvXevoL98"
    }
    response = requests.get("https://www.googleapis.com/youtube/v3/search", params=params)
    data = response.json()
    video_ids = [item["id"]["videoId"] for item in data["items"]]
    video_links = [f"https://www.youtube.com/watch?v={video_id}" for video_id in video_ids[:n]]
    return video_links



"""## Download Videos

"""



def download_video_with_audio(link):
    yt = YouTube(link)

    # Get the best video and audio streams
    video_stream = yt.streams.get_highest_resolution()
    audio_stream = yt.streams.get_audio_only()

    # Download the video and audio streams
    if not os.path.exists("videos"):
        os.makedirs("videos")

    # video_filename = f"{(yt.title)[:30]}.{video_stream.subtype}"
    # audio_filename = f"{(yt.title)[:30]}.{audio_stream.subtype}"
    # video_stream.download(output_path="videos", filename=video_filename)
    # audio_stream.download(output_path="videos", filename=audio_filename)

    video_filename = re.sub(r'[^\w\s-]', '_', yt.title[:30]) + f".{video_stream.subtype}"
    audio_filename = re.sub(r'[^\w\s-]', '_', yt.title[:30]) + f".{audio_stream.subtype}"
    video_stream.download(output_path="videos", filename=video_filename)
    audio_stream.download(output_path="videos", filename=audio_filename)
    
    # Merge the video and audio files
    output_filename = f"videos/{yt.title}.mp4"
    command = f"ffmpeg -i {video_filename} -i {audio_filename} -c copy {output_filename}"
    subprocess.run(command.split())
    
    print("Video and audio downloaded")

def download_videos(links):
    for link in links:
        download_video_with_audio(link)


"""## Video to audio"""

def convert_video_to_audio(video_file):
    # Load the video file using pydub
    video = AudioSegment.from_file(video_file, format=video_file.split(".")[-1])

    # Export the audio to a new file in the desired format
    audio_filename = f"audio/{os.path.splitext(os.path.basename(video_file))[0]}.mp3"
    video.export(audio_filename, format="mp3")

    print(f"{video_file} converted to {audio_filename}")

def convert_videos_to_audio():
    # Create the audio directory if it doesn't already exist
    if not os.path.exists("audio"):
        os.makedirs("audio")

    # Get a list of all video files in the video directory
    video_files = [os.path.join("videos", f) for f in os.listdir("videos") if f.endswith((".mp4", ".mkv", ".avi"))]

    # Convert each video file to audio
    for video_file in video_files:
        convert_video_to_audio(video_file)


"""## Trim y seconds"""



def trim_audio(filename, y):
    
    # Load audio file
    audio = AudioSegment.from_file(filename)

    # Trim audio for y seconds
    trimmed_audio = audio[y*1000:]
    
    # Get the file extension of the input file
    file_extension = os.path.splitext(filename)[1][1:]
    
    # Replace any invalid characters in the filename with '_'
    new_filename = os.path.splitext(filename)[0].replace(':', '_').replace('|', '_').replace(' ', '_')
    
    
    if not os.path.exists("trimmed_audio"):
        os.makedirs("trimmed_audio")
    

    # Save trimmed audio to new file
    new_filename = f"{new_filename}_trimmed.{file_extension}"
    if '\x5c' in new_filename:
        new_filename = new_filename.split("\x5c",1)[1]

    print(new_filename)
    trimmed_audio.export("trimmed_audio/"+new_filename, format=file_extension)
    

    print(f"{filename} trimmed and saved as {new_filename}")


def trim_all_audios(directory, y):
    
    if not os.path.exists(directory):
        raise Exception(f"{directory} does not exist")
    
    for filename in os.listdir(directory):
        if filename.endswith(".mp3") or filename.endswith(".wav") or filename.endswith(".m4a"):
            trim_audio(os.path.join(directory, filename), y)



"""## Merge all audios into a single file"""

def merge_all_audios(output_file):

    # Directory where audio files are located
    directory = "trimmed_audio"

    # List of audio files to be merged
    files = [file for file in os.listdir(directory) if file.endswith(".mp3")]

    # Load audio files into memory
    audio_files = [AudioSegment.from_file(os.path.join(directory, file)) for file in files]

    # Merge audio files
    merged_audio = sum(audio_files)

    # if not os.path.exists("merged_audios"):
    #     os.makedirs("merged_audios")

    # Save merged audio to a file
    merged_audio.export(output_file, format="mp3")




def main():
    if(len(sys.argv)!=5):
        print("Number of arguments are not correct")
        exit(0)

    singer=sys.argv[1]
    n=int(sys.argv[2])
    duration=int(sys.argv[3])
    output_file=sys.argv[4]

    if n<=10:
        print("Number of videos must be greater than 10")
        exit(0)
    
    if duration<=20:
        print("Duration must be greater than 20")
        exit(0)

    
    print("Getting video links form youtube...")
    video_links=get_video_links(singer, n)
    
    print("Downloading Videos...")
    download_videos(video_links)
    
    print("Converting Video to audio...")
    convert_videos_to_audio()
    
    print("Triming audios....")
    trim_all_audios("audio", duration)
    
    print("Merging...")
    merge_all_audios(output_file)
    
    print("Done")



if __name__=="__main__":
    main()

