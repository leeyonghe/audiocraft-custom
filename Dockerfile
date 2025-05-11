FROM pytorch/pytorch:2.1.0-cuda12.1-cudnn8-runtime

# 작업 디렉토리 설정
WORKDIR /workspace

# 시스템 의존성 설치
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Python 가상환경 생성 및 활성화
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# 애플리케이션 파일 복사
COPY . .

# Python 의존성 설치
RUN pip install --no-cache-dir -r requirements.txt

# audiocraft 패키지 설치
RUN pip install -e .

# 환경 변수 설정
ENV PYTHONPATH=/workspace
ENV HUGGING_FACE_HUB_TOKEN=${HUGGING_FACE_HUB_TOKEN}

# FastAPI 서버 포트 노출
EXPOSE 8000

# FastAPI 서버 실행
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"] 