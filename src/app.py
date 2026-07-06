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
from chat import ChatAgent

st.title("Scribe")
st.write("Enregistrez une note vocale : Scribe la transcrit et en tire un compte rendu structuré.")

if not config.GROQ_API_KEY:
    st.error(
        "Clé API Groq manquante : renseignez GROQ_API_KEY dans un fichier .env (voir .env.example)."
    )
    st.stop()

if "report" not in st.session_state:
    st.session_state.report = None
    st.session_state.chat_agent = None
    st.session_state.tts_path = None

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

    with st.spinner("Génération de la version audio..."):
        tts_path = str(Path(tempfile.gettempdir()) / "compte_rendu.wav")
        Speaker().speak(report, tts_path)

    st.session_state.report = report
    st.session_state.chat_agent = ChatAgent(report)
    st.session_state.tts_path = tts_path

if st.session_state.report:
    st.markdown(st.session_state.report)
    st.audio(st.session_state.tts_path)

    st.subheader("Poser une question sur le compte rendu")
    for message in st.session_state.chat_agent.messages[1:]:
        st.chat_message(message["role"]).write(message["content"])

    if question := st.chat_input("Votre question"):
        st.chat_message("user").write(question)
        try:
            with st.spinner("Réflexion en cours..."):
                answer = st.session_state.chat_agent.ask(question)
        except RuntimeError as exc:
            st.error(str(exc))
        else:
            st.chat_message("assistant").write(answer)
