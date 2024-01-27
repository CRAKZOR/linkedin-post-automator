from time import sleep
import openai

from utils import custom_print


class IncompleteResponse(openai.error.OpenAIError):
    pass


class ChatGpt:
    def __init__ (self, api_key):
        # openai instance
        self.openai = openai
        self.openai.api_key = api_key

    def ask(self, messages, token_limit=150, model="gpt-4", temp=1, retry_limit=5, continuation_limit=3):
        """
            Queries the GPT model for a response based on input messages. In case of incomplete
            responses, it attempts to continue the conversation until the specified continuation limit is reached.

            :param messages          : Input messages formatted as a list of dictionaries.
                                         Example: [{"role": "user", "content": "I am Peter"}]
            :param token_limit       : Maximum length of the GPT response.
            :param model             : Name of the GPT model/engine to be used.
            :param temp              : Specifies the randomness of the model's output. Higher values (close to 1) make
                                         the output more random, while lower values make it more deterministic.
            :param retry_limit       : Maximum number of retries in case of API errors.
            :param continuation_limit: Maximum number of continuations in case of incomplete responses.

            :return: GPT response as a string or None if maximum retries or continuations are reached without a complete response.
        """
        while retry_limit >= 0:
            retry_limit -= 1

            try:
                response = self.openai.ChatCompletion.create(
                    model       = model,
                    messages    = messages,
                    max_tokens  = token_limit,
                    temperature = temp
                )

                # Check if response is incomplete
                if response.choices[0].finish_reason != "stop":
                    continue

                    # TODO: fix continuation

                    # message was cut off
                    # if continuation_limit:
                    #
                    #     # Modify the messages list to append the incomplete response and continue
                    #     messages.append({"role": "user", "content": response.choices[0].message.content.strip()})
                    #     messages.append({"role": "user", "content": "The previous message was cut off."})
                    #
                    #     continuation_limit -= 1
                    #     custom_print(f"{continuation_limit} continuations left")
                    #     print(response.choices[0].message.content.strip())
                    #     continue
                    #
                    # else:
                    #     raise IncompleteResponse()

                else:

                    tokens_used = "\n    ".join([
                        (lambda x: f"Prompt Tokens:     {x['prompt_tokens']}")(response["usage"]),
                        (lambda x: f"Completion Tokens: {x['completion_tokens']}")(response["usage"]),
                        (lambda x: f"Total Tokens:      {x['total_tokens']}")(response["usage"])
                    ])
                    custom_print(f"Tokens Used:\n    {tokens_used}")

                    return response.choices[0].message.content.strip()

            except IncompleteResponse:
                custom_print("Response not complete. Retrying in 60 seconds...")
                sleep(60)

            except self.openai.error.RateLimitError:
                custom_print("Rate limit exceeded. Retrying in 60 seconds...")
                sleep(60)

            except self.openai.error.ServiceUnavailableError:
                custom_print("The server is overloaded or not ready yet.  Retrying in 60 seconds...")
                sleep(60)

        return None
