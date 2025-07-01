import json, requests, time
from typing import Any, List, Mapping, Optional, Literal, Union, TypedDict

class LMStudio:
    """LM Studio OpenAI-compatible API interface.
    https://lmstudio.ai/
    """

    Message_Type = TypedDict('Message', { 'role': Literal['user', 'assistant', 'system', 'tool'], 'content': str })

    def __init__(self,
        api_url: str = "http://localhost:1234/v1/chat/completions",
        model: str = "local-model",
        max_tokens: int = 0,
        temperature: Optional[float] = 1.0,
        top_k: Optional[int] = 40,
        top_p: Optional[float] = 1.0,
        presence_penalty: Optional[float] = 0.0,
        frequency_penalty: Optional[float] = 0.0,
        repetition_penalty: Optional[float] = 1.0,
        min_p: Optional[float] = 0.0,
        top_a: Optional[float] = 0.0,
        seed: Optional[int] = None,
        logit_bias: Optional[Mapping[int, int]] = None,
        response_format: Optional[Mapping[str, str]] = None,
        stop: Optional[List[str]] = None,
        timeout: int = 3600,
        ):

        self.api_url = api_url
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.top_k = top_k
        self.top_p = top_p
        self.presence_penalty = presence_penalty
        self.frequency_penalty = frequency_penalty
        self.repetition_penalty = repetition_penalty
        self.min_p = min_p
        self.top_a = top_a
        self.seed = seed
        self.logit_bias = logit_bias
        self.response_format = response_format
        self.stop = stop
        self.timeout = timeout

    def set_params(self,
        max_tokens: Optional[int] | None = None,
        presence_penalty: Optional[float] | None = None,
        frequency_penalty: Optional[float] | None = None,
        repetition_penalty: Optional[float] | None = None,
        response_format: Optional[Mapping[str, str]] | None = None,
        temperature: Optional[float] | None = None,
        seed: Optional[int] | None = None,
        top_k: Optional[int] | None = None,
        top_p: Optional[float] | None = None,
        min_p: Optional[float] | None = None,
        top_a: Optional[float] | None = None,
        ):

        if max_tokens is not None: self.max_tokens = max_tokens
        if presence_penalty is not None: self.presence_penalty = presence_penalty
        if frequency_penalty is not None: self.frequency_penalty = frequency_penalty
        if repetition_penalty is not None: self.repetition_penalty = repetition_penalty
        if response_format is not None: self.response_format = response_format
        if temperature is not None: self.temperature = temperature
        if seed is not None: self.seed = seed
        if top_k is not None: self.top_k = top_k
        if top_p is not None: self.top_p = top_p
        if min_p is not None: self.min_p = min_p
        if top_a is not None: self.top_a = top_a

    def ensure_array(self,
            input_msg: List[Message_Type] | Message_Type
        ) -> List[Message_Type]:
        if isinstance(input_msg, (list, tuple)):
            return input_msg
        else:
            return [input_msg]

    def chat(self,
            messages: Message_Type,
            max_retries: int = 10,
            seed: int = None
    ):
        messages = self.ensure_array(messages)
        headers = {
            "Content-Type": "application/json",
        }
        
        # Build request body with only non-None parameters
        body = {
            "model": self.model,
            "messages": messages,
            "stream": False,
        }
        
        # Add optional parameters only if they have values
        if self.max_tokens > 0:
            body["max_tokens"] = self.max_tokens
        if self.temperature is not None:
            body["temperature"] = self.temperature
        if self.top_k is not None:
            body["top_k"] = self.top_k
        if self.top_p is not None:
            body["top_p"] = self.top_p
        if self.presence_penalty is not None:
            body["presence_penalty"] = self.presence_penalty
        if self.frequency_penalty is not None:
            body["frequency_penalty"] = self.frequency_penalty
        if self.repetition_penalty is not None:
            body["repetition_penalty"] = self.repetition_penalty
        if self.min_p is not None:
            body["min_p"] = self.min_p
        if self.top_a is not None:
            body["top_a"] = self.top_a
        if self.seed is not None or seed is not None:
            body["seed"] = self.seed if seed is None else seed
        if self.logit_bias is not None:
            body["logit_bias"] = self.logit_bias
        if self.response_format is not None:
            body["response_format"] = self.response_format
        if self.stop is not None:
            body["stop"] = self.stop

        retries = 0
        while retries < max_retries:
            try:
                response = requests.post(
                    url=self.api_url, 
                    headers=headers, 
                    data=json.dumps(body), 
                    timeout=self.timeout, 
                    stream=False
                )
                response.raise_for_status()
                
                response_data = response.json()
                if 'choices' in response_data and len(response_data['choices']) > 0:
                    return response_data["choices"][0]["message"]["content"]
                elif 'error' in response_data:
                    error_msg = response_data['error']
                    print(f"LM Studio returns error '{error_msg.get('code', 'unknown')}' with message '{error_msg.get('message', 'unknown error')}', retry attempt {retries + 1}.")
                    
                    # Handle specific error codes
                    error_code = error_msg.get('code', '')
                    if error_code == 400:
                        print("Bad Request (invalid or missing params)")
                    elif error_code == 401:
                        raise Exception("Invalid credentials")
                    elif error_code == 403:
                        print("Forbidden - check LM Studio settings")
                    elif error_code == 408:
                        print("Request timed out")
                    elif error_code == 429:
                        print("Rate limited, waiting 5 seconds")
                        time.sleep(5)
                    elif error_code == 500:
                        print("Internal server error from LM Studio")
                        time.sleep(2)
                    elif error_code == 503:
                        print("LM Studio service unavailable")
                        time.sleep(5)
                else:
                    print(f"Response without error but missing choices, retry attempt {retries + 1}.")
                    print(f"Response: {response_data}")
                    
            except requests.exceptions.HTTPError as http_err:
                print(f"HTTP error occurred: '{http_err}' - Status Code: '{http_err.response.status_code}', retry attempt {retries + 1}.")
                if http_err.response.status_code == 524:
                    time.sleep(10)
            except (requests.exceptions.Timeout, requests.exceptions.TooManyRedirects) as err:
                print(f"Retry attempt {retries + 1} after error: '{err}'")
                time.sleep(2)
            except requests.exceptions.ConnectionError as conn_err:
                print(f"Connection error: '{conn_err}', retry attempt {retries + 1}")
                print("Make sure LM Studio is running and the API server is started")
                time.sleep(5)
            except requests.exceptions.RequestException as req_err:
                print(f"Request error: '{req_err}', retry attempt {retries + 1}.")
                time.sleep(2)
            except Exception as e:
                print(f"Unexpected error: '{e}', retry attempt {retries + 1}.")
                time.sleep(2)
            
            retries += 1
            
        raise Exception(f"Failed to get response from LM Studio after {max_retries} retries") 