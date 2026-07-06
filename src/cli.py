import argparse
import sys
from datetime import date

import config
from transcription import Transcriber
from summary import Summarizer


def main() -> None:
    parser = argparse.ArgumentParser(description="Transforme un enregistrement audio en compte rendu structuré.")
    parser.add_argument("audio_path", help="Chemin du fichier audio à transcrire.")
    args = parser.parse_args()

    config.require_api_key()

    try:
        print("Transcription en cours...")
        transcript_agent = Transcriber()
        transcription=transcript_agent.transcribe(args.audio_path)
        
        
        print("Rédaction du compte rendu en cours...")
        summarizer_agent = Summarizer()
        report = summarizer_agent.generate_report(transcription)
        
        
    except (FileNotFoundError, RuntimeError) as exc:
        sys.exit(str(exc))

    print(report)

    output_path = f"compte_rendu_{date.today().isoformat()}.md"
    with open(output_path, "w", encoding="utf-8") as output_file:
        output_file.write(report)
    print(f"Compte rendu enregistré dans {output_path}")


if __name__ == "__main__":
    main()
