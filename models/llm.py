import os

from dotenv import load_dotenv
from openai import OpenAI
from ollama import Client as OllamaClient


load_dotenv()


class LLM:

    def __init__(
        self,
        provider="deepseek",
        model=None,
    ):

        self.provider = provider

        if provider == "deepseek":

            self.model = model or "deepseek-chat"

            api_key = os.getenv(
                "DEEPSEEK_API_KEY"
            )

            if not api_key:
                raise RuntimeError(
                    "DEEPSEEK_API_KEY is not set."
                )

            self.client = OpenAI(
                api_key=api_key,
                base_url="https://api.deepseek.com",
            )

        elif provider == "ollama":

            self.model = model or "qwen3:8b"

            self.client = OllamaClient(
                host="http://192.168.56.1:11434"
            )

        else:

            raise ValueError(
                f"Unknown provider: {provider}"
            )


    def generate(
        self,
        prompt,
        system=None,
    ):

        messages = []

        if system:

            messages.append(
                {
                    "role": "system",
                    "content": system,
                }
            )

        messages.append(
            {
                "role": "user",
                "content": prompt,
            }
        )

        if self.provider == "deepseek":

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
            )

            return response.choices[0].message.content

        elif self.provider == "ollama":

            response = self.client.chat(
                model=self.model,
                messages=messages,
            )

            return response["message"]["content"]