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

        self.model = model or "deepseek.v3.2"

        self.client = boto3.client(
            "bedrock-runtime",
            region_name=region,
        )

    def generate(
        self,
        prompt,
        system=None,
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
        }

        if system:
            kwargs["system"] = [
                {
                    "text": system
                }
            ]

        response = self.client.converse(**kwargs)

        return response["output"]["message"]["content"][0]["text"]
