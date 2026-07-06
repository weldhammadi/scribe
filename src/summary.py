from groq import APIError

import config


class Summarizer:
    def __init__(self):
        self.client = config.get_client()

    def generate_report(self, transcript: str) -> str:
        system_prompt = config.SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")

        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": transcript},
                ],
                model=config.LLM_MODEL,
                temperature=config.LLM_TEMPERATURE,
                max_completion_tokens=config.LLM_MAX_TOKENS,
            )
        except APIError as exc:
            raise RuntimeError(f"Échec de la génération du compte rendu (API Groq) : {exc}") from exc

        return chat_completion.choices[0].message.content


if __name__ == "__main__":
    import sys

    transcript = sys.argv[1] if len(sys.argv) > 1 else "Exemple de transcription de test."
    print(Summarizer().generate_report(transcript))
