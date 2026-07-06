from groq import APIError

import config


class ChatAgent:
    def __init__(self, report: str):
        self.client = config.get_client()
        self.messages = [
            {
                "role": "system",
                "content": (
                    "Tu réponds aux questions de l'utilisateur en te basant uniquement sur le "
                    "compte rendu suivant. Si la réponse ne s'y trouve pas, dis-le clairement.\n\n"
                    f"{report}"
                ),
            }
        ]

    def ask(self, question: str) -> str:
        self.messages.append({"role": "user", "content": question})

        try:
            chat_completion = self.client.chat.completions.create(
                messages=self.messages,
                model=config.LLM_MODEL,
                temperature=config.LLM_TEMPERATURE,
                max_completion_tokens=config.LLM_MAX_TOKENS,
            )
        except APIError as exc:
            raise RuntimeError(f"Échec de la réponse (API Groq) : {exc}") from exc

        answer = chat_completion.choices[0].message.content
        self.messages.append({"role": "assistant", "content": answer})
        return answer


if __name__ == "__main__":
    agent = ChatAgent("Exemple de compte rendu de test.")
    print(agent.ask("De quoi parle ce compte rendu ?"))
