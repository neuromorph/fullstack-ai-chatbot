import os
from dotenv import load_dotenv
import requests
import json

load_dotenv()

class GPT:
    def __init__(self):
        self.url = os.environ.get('MODEL_URL')
        self.headers = {
            "Authorization": f"Bearer {os.environ.get('HUGGINGFACE_INFERENCE_TOKEN')}"}
        self.payload = {
            "inputs": {"text":""},
            }


    def query(self, input: str) -> list:
        self.payload["inputs"]["text"] = input
        # self.payload["inputs"]["past_user_inputs"] = ["Do you know plot of movie Titanic?"]
        # self.payload["inputs"]["generated_responses"] = ["Yes, I do."]
        # data = json.dumps(self.payload)
        response = requests.post(
            self.url, headers=self.headers, json=self.payload)
        output = json.loads(response.content.decode("utf-8"))
        # print(output)
        if 'generated_text' in output:
            resp = output['generated_text']
        else:
            resp = output['error']
        # print(resp)
        return resp

if __name__ == "__main__":
    GPT().query("Human: What's your favorite movie? Bot:")
