import json
import boto3


REGION = "ap-northeast-1"
EMBEDDING_MODEL = "amazon.titan-embed-text-v2:0"


class BedrockEmbeddings:
    def __init__(self):
        self.client = boto3.client(
            "bedrock-runtime",
            region_name=REGION,
        )

    def _embed(self, text):
        response = self.client.invoke_model(
            modelId=EMBEDDING_MODEL,
            body=json.dumps({
                "inputText": text
            }),
            contentType="application/json",
            accept="application/json",
        )

        body = json.loads(
            response["body"].read()
        )

        return body["embedding"]

    def embed_documents(self, texts):
        return [
            self._embed(text)
            for text in texts
        ]

    def embed_query(self, text):
        return self._embed(text)


def get_embedding_model():
    return BedrockEmbeddings()
