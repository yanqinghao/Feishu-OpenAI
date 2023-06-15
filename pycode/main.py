import os
import asyncio
import openai

# import tiktoken
from fastapi import FastAPI
from pydantic import BaseModel
from revChatGPT.V1 import AsyncChatbot

class ChatGPTRequest(BaseModel):
    model: str = "gpt-3.5-turbo"
    messages: list
    max_tokens: int = 2000
    temperature: float = 1
    top_p: float = 1
    frequency_penalty: float = 0
    presence_penalty:  float = 0

initConfig = {
    "email": os.environ.get("EMAIL"),
    "password": os.environ.get("PASSWORD"),
    "proxy": os.environ.get("PROXY"),
    "model": os.environ.get("MODEL"),   # gpt-4 gpt-4-browsing text-davinci-002-render-sha gpt-3.5-turbo
}

chatbot = AsyncChatbot(config=initConfig)

async def updateAccessToken():
    print("开启AccessToken自动更新", flush=True)
    while True:
        await asyncio.sleep(1 * 24 * 60 * 60)
        print("AccessToken自动更新中", flush=True)
        chatbot.__check_credentials()
        print("AccessToken自动更新完成", flush=True)

async def updateModel():
    print("达到使用次数限制，更新模型为ChatGPT-3.5", flush=True)
    await asyncio.sleep(4 * 60 * 60)
    chatbot.config["model"] = os.environ.get("MODEL")
    print("更新模型为ChatGPT-4", flush=True)

openai.api_key = os.environ.get('OPENAI_KEY')
openai.proxy = {
    'http': os.environ.get("PROXY"),
    'https': os.environ.get("PROXY"),
}

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(updateAccessToken())

@app.post('/chat/completions')
async def chatCompletions(req: ChatGPTRequest):
    maxRetry = 3
    return await makeRequest(req, maxRetry)

async def makeRequest(req, maxRetry):
    if maxRetry > 0:
        maxRetry -= 1
        try:
            prompt = "".join([f'{m["role"]}:{m["content"]}\n' for m in req.messages])
            return await makeRevChatGPTRequest(prompt)
        except Exception as e:
            if "Incorrect API key" in str(e) or "invalid_api_key" in str(e):
                chatbot.__check_credentials()
                return await makeRequest(req, maxRetry)
            elif "You have sent too many messages to the model. Please try again later." in str(e):
                chatbot.config["model"] = "text-davinci-002-render-sha"
                asyncio.create_task(updateModel())
                return await makeRequest(req, maxRetry)
            else:
                print(f"接口请求异常: {e}", flush=True)
                return await makeRequest(req, maxRetry)
    else:
        try:
            return await makeChatGPTAPIRequest(req)
        except Exception as e:
            return {
            "id": "chatcmpl-123",
            "object": "chat.completion",
            "created": 1677652288,
            "model": chatbot.config["model"],
            "choices": [{
                "index": 0,
                "message": {
                "role": "assistant",
                "content": "请求所有ChatGPT接口失败，请联系燕青协助解决。",
                },
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": 9,
                "completion_tokens": 12,
                "total_tokens": 21
            }
        }

async def makeRevChatGPTRequest(prompt):
    chatbot.conversation_id = None
    async for data in chatbot.ask(
        prompt,
    ):
        message = data["message"]

    await chatbot.delete_conversation(convo_id=data["conversation_id"])
    model = "gpt4" if chatbot.config["model"] == "gpt-4" else "gpt3.5"
    return {
            "id": "chatcmpl-123",
            "object": "chat.completion",
            "created": 1677652288,
            "model": chatbot.config["model"],
            "choices": [{
                "index": 0,
                "message": {
                "role": "assistant",
                "content": f"{message}[由{model}生成]",
                },
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": 9,
                "completion_tokens": 12,
                "total_tokens": 21
            }
        }


async def makeChatGPTAPIRequest(req):
    respond = await openai.ChatCompletion.acreate(
            model=req.model,
            messages=req.messages,
            max_tokens=req.max_tokens,
            temperature=req.temperature,
            top_p=req.top_p,
            frequency_penalty=req.frequency_penalty,
            presence_penalty=req.presence_penalty,
        )
    respond["choices"][0]["message"]["content"] += f"[由{req.model}付费生成]"
    return respond
