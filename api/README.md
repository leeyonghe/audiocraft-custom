# AudioCraft API

AudioCraft의 모든 모델을 REST API로 제공하는 서비스입니다.

## 설치

1. 필요한 패키지 설치:
```bash
pip install -r requirements.txt
```

2. 서버 실행:
```bash
python main.py
```

서버는 기본적으로 `http://localhost:8000`에서 실행됩니다.

## 프로젝트 구조

```
audiocraft-custom/
├── audiocraft/          # 로컬 AudioCraft 라이브러리
├── api/
│   ├── main.py         # API 서버 코드
│   ├── requirements.txt # 의존성 패키지 목록
│   └── README.md       # API 문서
```

## API 엔드포인트

### 1. 음악 생성
```http
POST /generate/music
Content-Type: application/json

{
    "text": "happy electronic music with piano",
    "duration": 10.0,
    "temperature": 1.0,
    "top_k": 250,
    "top_p": 0.0,
    "cfg_coef": 3.0
}
```

### 2. 오디오 생성
```http
POST /generate/audio
Content-Type: application/json

{
    "text": "dog barking and birds chirping",
    "duration": 10.0,
    "temperature": 1.0,
    "top_k": 250,
    "top_p": 0.0,
    "cfg_coef": 3.0
}
```

### 3. 오디오 인코딩
```http
POST /encode
Content-Type: multipart/form-data

audio_file: [오디오 파일]
model: "encodec"
```

### 4. 오디오 디코딩
```http
POST /decode
Content-Type: multipart/form-data

codes: [[코드 배열]]
model: "encodec"
```

### 5. 오디오 분석
```http
POST /analyze
Content-Type: multipart/form-data

audio_file: [오디오 파일]
threshold: 0.5
```

### 6. 상태 확인
```http
GET /health
```

## 응답 형식

### 음악/오디오 생성
- WAV 파일 형식으로 반환

### 인코딩
```json
{
    "codes": [[코드 배열]]
}
```

### 분석
```json
{
    "mpd_score": 0.85,
    "msd_score": 0.92,
    "msstftd_score": 0.78,
    "feature_maps": [[특징 맵 배열]],
    "is_real": true
}
```

### 상태 확인
```json
{
    "status": "healthy",
    "version": "1.0.0",
    "models": ["musicgen", "audiogen", "encodec", "multiband"],
    "discriminators": ["mpd", "msd", "msstftd"]
}
```

## 파라미터 설명

### 생성 파라미터
- `text`: 생성할 오디오를 설명하는 텍스트 프롬프트
- `duration`: 생성할 오디오의 길이 (초)
- `temperature`: 생성 다양성 조절 (높을수록 더 다양한 결과)
- `top_k`: 상위 k개 토큰만 고려
- `top_p`: 누적 확률이 p가 될 때까지의 토큰만 고려
- `cfg_coef`: Classifier-Free Guidance 계수

### 분석 파라미터
- `threshold`: 실제 오디오 판별 임계값 (기본값: 0.5)

## 주의사항

1. 오디오 파일은 WAV 형식을 권장합니다.
2. 생성된 오디오는 32kHz 샘플링 레이트로 저장됩니다.
3. 메모리 사용량이 큰 작업이므로 충분한 RAM이 필요합니다.
4. GPU가 있는 경우 자동으로 사용됩니다.

## 라이선스

이 프로젝트는 AudioCraft의 라이선스를 따릅니다. 