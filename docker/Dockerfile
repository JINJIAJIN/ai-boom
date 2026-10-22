# HERMES Docker部署配置
# 用于在Windows Server上通过Docker运行HERMES

FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 克隆HERMES
RUN git clone https://github.com/NousResearch/HERMES.git /app/hermes

WORKDIR /app/hermes

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制配置文件
COPY hermes-config.yaml /app/hermes/config.yaml

# 启动
CMD ["python", "-m", "hermes", "--config", "config.yaml"]
