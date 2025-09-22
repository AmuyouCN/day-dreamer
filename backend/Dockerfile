FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# 安装 uv
RUN pip install uv

# 复制项目配置文件
COPY pyproject.toml ./

# 创建虚拟环境并安装依赖
RUN uv venv && \
    uv pip install -e .

# 复制代码
COPY . .

# 创建日志目录
RUN mkdir -p logs

EXPOSE 8000

CMD ["uv", "run", "python", "start.py"]