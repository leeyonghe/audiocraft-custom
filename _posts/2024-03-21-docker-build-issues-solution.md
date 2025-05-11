---
layout: post
title: "Docker 빌드 문제 해결하기 - gcc 컴파일러와 시간대 설정"
date: 2024-03-21 15:00:00 +0900
categories: [Docker, Troubleshooting]
tags: [docker, build-essential, timezone, pesq]
---

# Docker 빌드 문제 해결하기

오늘은 Docker 이미지 빌드 과정에서 발생한 두 가지 문제를 해결한 경험을 공유하고자 합니다.

## 1. gcc 컴파일러 누락 문제

### 문제 상황
`pesq` 패키지를 설치하는 과정에서 다음과 같은 에러가 발생했습니다:
```
error: command 'gcc' failed: No such file or directory
```

### 원인
`pesq` 패키지는 C 확장을 컴파일하는 과정에서 `gcc` 컴파일러가 필요한데, Docker 컨테이너에 설치되어 있지 않았습니다.

### 해결 방법
Dockerfile의 시스템 의존성 설치 부분에 `build-essential` 패키지를 추가했습니다:

```dockerfile
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    build-essential \
    && rm -rf /var/lib/apt/lists/*
```

## 2. 시간대 설정 프롬프트 문제

### 문제 상황
패키지 설치 과정에서 시간대 설정 관련 대화형 프롬프트가 나타나 빌드가 중단되었습니다.

### 원인
`tzdata` 패키지 설치 과정에서 시간대 설정을 위한 사용자 입력이 필요했기 때문입니다.

### 해결 방법
Dockerfile에 `DEBIAN_FRONTEND=noninteractive` 환경 변수를 추가하여 대화형 프롬프트를 자동으로 처리하도록 했습니다:

```dockerfile
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    build-essential \
    && rm -rf /var/lib/apt/lists/*
```

## 최종 Dockerfile

```dockerfile
FROM pytorch/pytorch:2.1.0-cuda12.1-cudnn8-runtime

WORKDIR /workspace

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
ENV PYTHONPATH=/workspace
```

## 결론

Docker 빌드 과정에서 발생하는 문제들은 대부분 다음과 같은 원인들로 인해 발생합니다:
1. 필요한 시스템 패키지의 누락
2. 대화형 프롬프트로 인한 빌드 중단

이러한 문제들은 적절한 패키지 설치와 환경 변수 설정을 통해 해결할 수 있습니다. 특히 `build-essential`과 `DEBIAN_FRONTEND=noninteractive`는 자주 사용되는 해결책입니다. 