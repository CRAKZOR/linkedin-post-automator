from time import sleep
from openai import OpenAI, RateLimitError, APIStatusError   # new import style

from utils import custom_print


class IncompleteResponse(Exception):      # openai.OpenAIError no longer exists
    """Raised when we decide not to resume a truncated answer."""
    pass


class ChatGpt:
    def __init__(self, api_key: str):
        # instantiate an explicit client instead of relying on module‑level globals
        # (recommended in the v1 migration guide)
        self.client = OpenAI(api_key=api_key)

    def ask(
        self,
        messages: list[dict[str, str]],
        token_limit: int = 150,
        model: str = "gpt-4o-mini",
        temp: float = 1.0,
        retry_limit: int = 5,
        continuation_limit: int = 3,
    ) -> str | None:

        retries = retry_limit

        while retries >= 0:
            retries -= 1
            try:
                # ChatCompletion.create → client.chat.completions.create
                completion = self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    max_tokens=token_limit,
                    temperature=temp,
                )

                # finish_reason still exists, but the object is now a Pydantic model
                if completion.choices[0].finish_reason != "stop":
                    # TODO: continuation logic
                    continue

                usage = completion.usage
                custom_print(
                    "Tokens Used:\n"
                    f"    Prompt Tokens:     {usage.prompt_tokens}\n"
                    f"    Completion Tokens: {usage.completion_tokens}\n"
                    f"    Total Tokens:      {usage.total_tokens}"
                )
                return completion.choices[0].message.content.strip()

            # ---- v1 error classes ------------------------------------------
            except RateLimitError as e:                      # 429
                # custom_print(e)
                custom_print("Rate limit exceeded. Retrying in 60 seconds...")
                sleep(60)

            except APIStatusError as err:               # any 4xx / 5xx
                if err.status_code == 503:              # “Service Unavailable”
                    custom_print("The server is overloaded. Retrying in 60 seconds...")
                    sleep(60)
                else:
                    raise

            except IncompleteResponse:
                custom_print("Response not complete. Retrying in 60 seconds...")
                sleep(60)

        return None
