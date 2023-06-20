#!/bin/bash

nohup /usr/bin/xray -config /etc/xray/config.json > xray.log 2>&1 &

sleep 5

nohup uvicorn main:app --reload --host 0.0.0.0 --port 5000 > openai-proxy.log 2>&1 &

sleep 5

/app/feishu_chatgpt