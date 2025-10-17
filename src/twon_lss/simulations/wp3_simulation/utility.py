import logging
import requests
import typing
import time

import pydantic

from twon_lss.utility import LLM, Chat, Message


class WP3LLM(LLM):
    api_key: str
    url: str

    def _query(self, payload):
        headers: dict = {"Authorization": f"Bearer {self.api_key}"}
        response = requests.post(self.url, headers=headers, json=payload)
        return response.json()
    

    def generate(self, chat: Chat, max_retries: int = 3) -> str:
        try:
            response: str = self._query(
                {
                    "input": {
                        "messages": chat.model_dump()
                    },
                }
            )
            logging.info(f"LLM response: {response}")
    
            response = response["output"][0]["choices"][0]["tokens"][0]
        
        except Exception as e:
            logging.error(f"Failed to query LLM: {e}")
            if max_retries > 0:
                time.sleep(5)
                return self.generate(chat, max_retries - 1)
            raise RuntimeError("Failed to generate response from LLM after retries") from e
        
        return response
