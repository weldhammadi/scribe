import json
import tempfile
from pathlib import Path

import streamlit as st

import config
from transcription import Transcriber
from moderator import Moderator
from summary import Summarizer
from speaker import Speaker
from cli import format_report

st.title("Scribe")
st.write("Enregistrez une note vocale : Scribe la transcrit et en tire un compte rendu structuré.")

if not config.GROQ_API_KEY:
    st.error(
        "Clé API Groq manquante : renseignez GROQ_API_KEY dans un fichier .env (voir .env.example)."
    )
    st.stop()

audio_value = st.audio_input("Enregistrer une note vocale")

if audio_value is not None and st.button("Générer le compte rendu"):
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as audio_file:
        audio_file.write(audio_value.getvalue())
        audio_path = audio_file.name

    try:
        with st.spinner("Transcription en cours..."):
            transcriber = Transcriber()
            transcript = transcriber.transcribe(audio_path)

        with st.spinner("Vérification du contenu en cours..."):
            if not Moderator().is_legitimate(transcript):
                st.error(
                    "Scribe ne peut pas traiter cet enregistrement : son contenu ressemble à "
                    "une tentative de détournement de l'outil plutôt qu'à un contenu à résumer."
                )
                st.stop()

        with st.spinner("Rédaction du compte rendu en cours..."):
            report_data = json.loads(
                Summarizer().generate_report(transcript, language=transcriber.language)
            )
            report = format_report(report_data, language=transcriber.language)
    except RuntimeError as exc:
        st.error(str(exc))
        st.stop()

    st.markdown(report)

    with st.spinner("Génération de la version audio..."):
        tts_path = str(Path(tempfile.gettempdir()) / "compte_rendu.wav")
        Speaker().speak(report, tts_path)
    st.audio(tts_path)
