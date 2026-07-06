import argparse
import json
import os
import sys
from datetime import date

import config
from transcription import Transcriber
from summary import Summarizer
from moderator import Moderator
from speaker import Speaker
from chat import ChatAgent


LABELS = {
    "fr": {"points": "Points clés", "decisions": "Décisions / actions"},
    "en": {"points": "Key points", "decisions": "Decisions / actions"},
}


def format_report(data: dict, language: str = "fr") -> str:
    labels = LABELS.get(language, LABELS["en"])
    lines = [data["titre"], "", data["resume"], "", labels["points"]]
    lines += [f"- {point}" for point in data["points_cles"]]
    lines += ["", labels["decisions"]]
    lines += [f"- {item}" for item in data["decisions_actions"]]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Transforme un enregistrement audio en compte rendu structuré.")
    parser.add_argument("audio_path", help="Chemin du fichier audio à transcrire.")
    args = parser.parse_args()

    config.require_api_key()

    try:
        print("Transcription en cours...")
        transcript_agent = Transcriber()
        transcription=transcript_agent.transcribe(args.audio_path)

        print("Vérification du contenu en cours...")
        moderator_agent = Moderator()
        if not moderator_agent.is_legitimate(transcription):
            sys.exit(
                "Scribe ne peut pas traiter cet enregistrement : son contenu ressemble à une "
                "tentative de détournement de l'outil plutôt qu'à un contenu à résumer."
            )

        print("Rédaction du compte rendu en cours...")
        summarizer_agent = Summarizer()
        report_data = json.loads(
            summarizer_agent.generate_report(transcription, language=transcript_agent.language)
        )
        report = format_report(report_data, language=transcript_agent.language)
    except (FileNotFoundError, RuntimeError) as exc:
        sys.exit(str(exc))

    print(report)

    date_str = date.today().isoformat()
    output_path = f"compte_rendu_{date_str}.md"
    with open(output_path, "w", encoding="utf-8") as output_file:
        output_file.write(report)
    print(f"Compte rendu enregistré dans {output_path}")

    print("Lecture du compte rendu à voix haute...")
    audio_path = f"compte_rendu_{date_str}.wav"
    Speaker().speak(report, audio_path)
    os.startfile(audio_path)

    print("\nPose tes questions sur le compte rendu (tape 'quit' pour terminer).")
    chat_agent = ChatAgent(report)
    while True:
        question = input("> ")
        if question.strip().lower() in ("quit", "exit", "q"):
            break
        try:
            print(chat_agent.ask(question))
        except RuntimeError as exc:
            print(exc)


if __name__ == "__main__":
    main()
