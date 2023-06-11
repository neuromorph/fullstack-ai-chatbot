A demo of a fullstack AI chatbot using FastAPI, Redis and Hugging Face Inference API. 
FastAPI is used for the webserver talking to Client with REST and Websocket endpoints.
Client is a simple js/jquery based UI.
Redis enterprise cloud DB (free) instance is used as cache to save chat data.
Redis is also used for message queues (message channel and response channel) between Server and Worker.
Worker connects to Redis streams/channels to communicate with server and also connects to Hugging Face On Demand Inference API to query a hosted model.
The backend is based on an in depth [tutorial](https://blog.stephensanwo.dev/build-a-fullstack-ai-chatbot/series) by Stephen Sanwo written in collaboration with Redis. The frontend UI is based on a [simple UI](https://github.com/PandaWhoCodes/chatbot-frontend/) project.

![Fullstack AI Chatbot Architecture](FullstackChatbotArch.png)