from groq import APIError

import config


class Speaker:
    def __init__(self):
        self.client = config.get_client()

    def speak(self, text: str, output_path: str) -> None:
        try:
            response = self.client.audio.speech.create(
                model=config.TTS_MODEL,
                voice=config.TTS_VOICE,
                input=text,
                response_format=config.TTS_RESPONSE_FORMAT,
            )
        except APIError as exc:
            raise RuntimeError(f"Échec de la synthèse vocale (API Groq) : {exc}") from exc

        response.write_to_file(output_path)


if __name__ == "__main__":
    import sys

    text = sys.argv[1] if len(sys.argv) > 1 else "Ceci est un test de synthèse vocale."
    Speaker().speak(text, "test_tts.wav")
