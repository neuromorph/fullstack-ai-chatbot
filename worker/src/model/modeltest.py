import requests

API_URL = "https://api-inference.huggingface.co/models/microsoft/GODEL-v1_1-large-seq2seq"
headers = {"Authorization": "Bearer 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"}

def query(payload):
	response = requests.post(API_URL, headers=headers, json=payload)
	return response.json()
	
output = query({
	"inputs": {
		# "past_user_inputs": ["Which movie is the best ?"],
		# "generated_responses": ["It's Die Hard for sure."],
		"text": "What's Die Hard about?"
	},
})
print(output)

# import json
# import requests
# API_URL = "https://api-inference.huggingface.co/models/gpt2"
# headers = {"Authorization": f"Bearer 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"}
# def query(payload):
#     data = json.dumps(payload)
#     response = requests.request("POST", API_URL, headers=headers, data=data)
#     return json.loads(response.content.decode("utf-8"))
# data = query("What's movie Die Hard about?")
# print(data)
