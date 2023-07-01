import requests
import os
from tempfile import NamedTemporaryFile
import whisperx

def transcribe_and_store_audio(audio_url):
    device = "auto" 
    batch_size = 16  # reduce if low on GPU mem
    compute_type = "float16"  # change to "int8" if low on GPU mem (may reduce accuracy)

    # Download audio file from the provided URL
    response = requests.get(audio_url)
    response.raise_for_status()

    # Save the downloaded audio content to a temporary file
    with NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_audio_file:
        tmp_audio_file.write(response.content)
        tmp_audio_file.flush()

        # 1. Transcribe with original whisper (batched)
        model = whisperx.load_model("large-v2", device, compute_type=compute_type)

        audio = whisperx.load_audio(tmp_audio_file.name)
        result = model.transcribe(audio, batch_size=batch_size)



        print(result["segments"]) # after alignment


    # 3. Assign speaker labels
        diarize_model = whisperx.DiarizationPipeline(use_auth_token='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', device=device)

        # add min/max number of speakers if known
        # diarize_model(audio_file, min_speakers=min_speakers, max_speakers=max_speakers)
        diarize_segments = diarize_model(tmp_audio_file.name)
        result = whisperx.assign_word_speakers(diarize_segments, result)
        print(diarize_segments)
        print(result["segments"]) # segments are now assigned speaker IDs

    os.remove(tmp_audio_file.name)
