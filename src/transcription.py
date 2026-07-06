from pathlib import Path

from groq import APIError

import config


class Transcriber:
    def __init__(self):
        self.client = config.get_client()

    def transcribe(self, audio_path: str) -> str:
        if not Path(audio_path).is_file():
            raise FileNotFoundError(f"Fichier audio introuvable : {audio_path}")

        try:
            with open(audio_path, "rb") as audio_file:
                transcription = self.client.audio.transcriptions.create(
                    file=audio_file,
                    model=config.STT_MODEL,
                    response_format="verbose_json",
                    #language=config.STT_LANGUAGE,
                )
        except APIError as exc:
            raise RuntimeError(f"Échec de la transcription (API Groq) : {exc}") from exc

        return transcription.text


if __name__ == "__main__":
    import sys
    transcriber_agent = Transcriber()
    audio_file_path = sys.argv[1] if len(sys.argv) > 1 else "audio1.wav"
    print(transcriber_agent.transcribe(audio_file_path))
