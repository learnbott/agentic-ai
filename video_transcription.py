import os, pickle
from moviepy.editor import VideoFileClip
from pydub import AudioSegment
import pytubefix as pt
from openai import OpenAI
import whisper


def download_video(video_url, audio_output_path):
    """
    Download a video from a URL and save it to the output path.

    Parameters:
    video_url (str): The URL of the video to download.
    audio_output_path (str): The path to save the video to.

    """
    yt = pt.YouTube(video_url)
    stream = yt.streams.filter(only_video=True).first()
    stream.download(filename=audio_output_path)


def video_to_audio(video_path, audio_output_path):
    """
    Convert a video to audio and save it to the output path.

    Parameters:
    video_path (str): The path to the video file.
    audio_output_path (str): The path to save the audio to.

    """
    clip = VideoFileClip(video_path)
    audio = clip.audio
    audio.write_audiofile(audio_output_path)


def split_audio_into_chunks(audio_output_path, transcribe_output_dir, max_chunk_size_mb=24):
    # Load the audio file
    audio = AudioSegment.from_mp3(audio_output_path)
    
    # Calculate the maximum duration for each chunk based on the size limit
    max_chunk_size_bytes = max_chunk_size_mb * 1024 * 1024 * 10
    max_chunk_duration = (max_chunk_size_bytes / len(audio.raw_data)) * len(audio)
    
    # Split and export the audio file into chunks
    start_time = 0
    chunk_index = 1
    while start_time < len(audio):
        print(f"Exporting chunk {chunk_index}/{len(audio)/max_chunk_duration}")
        end_time = min(start_time + max_chunk_duration, len(audio))
        chunk = audio[start_time:end_time]
        chunk.export(f"{transcribe_output_dir}/chunk_{chunk_index}.mp3", format="mp3")
        start_time = end_time
        chunk_index += 1


def transcribe_audio_chunks(model, chunk_dir="/workspace/data", file_save_path=None):
    # Initialize the Agentic AI model
    transcription = []
    chunk_list = [chunk for chunk in os.listdir(chunk_dir) if chunk.startswith("chunk")]
    chunk_list=sorted(chunk_list)
    print(chunk_list)

    for chunk in chunk_list:
        print(f"   Transcribing {chunk}...")
        chunk_path = os.path.join(chunk_dir, chunk)
        if isinstance(model, OpenAI):
            audio_file = open(chunk_path, "rb")
            transcription.append(model.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            ))
        else:
            transcription.append(model.transcribe(chunk_path))
    
    if file_save_path:
        with open(file_save_path, "wb") as f:
            pickle.dump(transcription, f)

    return transcription


def get_transcription_model(open_source_model):
    if open_source_model:
        model = whisper.load_model("large")
    else:
        model = OpenAI()
    return model