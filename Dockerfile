# FROM golang:1.18 as golang

# ENV GO111MODULE=on \
#     CGO_ENABLED=1 \
#     GOPROXY=https://goproxy.cn,direct

# WORKDIR /build
# ADD /code /build

# RUN CGO_ENABLED=0 GOOS=linux go build -ldflags '-w -s' -o feishu_chatgpt

FROM python:3.9-slim-bullseye

WORKDIR /app

COPY ./code/feishu_chatgpt /app
COPY ./code/role_list.yaml /app
COPY ./pycode /app
COPY ./utils/xray /usr/bin/xray
COPY ./utils/config.json /etc/xray/config.json
COPY ./utils/start.sh /app/start.sh

RUN chmod +x /usr/bin/xray && \
    chmod +x /app/feishu_chatgpt && \
    chmod +x /app/start.sh && \
    pip config set global.index-url https://pypi.mirrors.ustc.edu.cn/simple && \
    pip install --upgrade pip && \
    pip install -r requirements.txt && \
    sed -i 's/deb.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list && \
    apt update && \
    apt install ca-certificates -y && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get clean autoclean && \
    apt-get autoremove --yes && \
    rm -rf /var/lib/{apt,dpkg,cache,log}/

EXPOSE 9000
ENTRYPOINT ["/app/start.sh"]
