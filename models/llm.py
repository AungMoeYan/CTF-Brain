import json

import boto3


class LLM:

    def __init__(
        self,
        provider="bedrock",
        model=None,
        region="ap-northeast-1",
    ):
        self.provider = provider

        if provider != "bedrock":
            raise ValueError(
                f"Unsupported provider: {provider}. "
                "This cloud version uses Amazon Bedrock."
            )

        self.model = model or "deepseek.v3-v1:0"

        self.client = boto3.client(
            "bedrock-runtime",
            region_name=region,
        )

    def generate(
        self,
        prompt,
        system=None,
        max_tokens=800,
        temperature=0.2,
    ):

        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "text": prompt
                    }
                ],
            }
        ]

        kwargs = {
            "modelId": self.model,
            "messages": messages,
            "inferenceConfig": {
                "maxTokens": max_tokens,
                "temperature": temperature,
            },
        }

        if system:

            kwargs["system"] = [
                {
                    "text": system
                }
            ]

        response = self.client.converse(
            **kwargs
        )

        return (
            response["output"]
            ["message"]
            ["content"][0]
            ["text"]
        )

    def generate_json(
        self,
        prompt,
        system=None,
        max_tokens=600,
    ):

        response = self.generate(
            prompt=prompt,
            system=system,
            max_tokens=max_tokens,
            temperature=0.1,
        )

        response = response.strip()

        # Remove Markdown JSON fences.
        if response.startswith("```"):

            response = response.replace(
                "```json",
                "",
                1,
            )

            response = response.replace(
                "```",
                "",
            )

            response = response.strip()

        try:

            return json.loads(response)

        except json.JSONDecodeError:

            return {
                "type": "final",
                "answer": response,
                "error": "Invalid JSON returned by model.",
            }
