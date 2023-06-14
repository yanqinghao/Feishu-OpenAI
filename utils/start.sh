#!/bin/bash

nohup /usr/bin/xray -config /etc/xray/config.json > /dev/null 2>&1 &

nohup uvicorn main:app --reload --host 0.0.0.0 --port 5000 > /dev/null 2>&1 &

sleep 5

/app/feishu_chatgpt