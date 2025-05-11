from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import torch
import torchaudio
import numpy as np
from typing import List, Optional, Dict, Any
import io
import tempfile
import os
import sys

# 로컬 AudioCraft 라이브러리 경로 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from audiocraft.models import (
    MusicGen,
    AudioGen,
    EncodecModel,
    MultiBandDiffusion
)
from audiocraft.adversarial.discriminators import (
    MultiPeriodDiscriminator,
    MultiScaleDiscriminator,
    MultiScaleSTFTDiscriminator
)

app = FastAPI(
    title="AudioCraft API",
    description="AudioCraft의 모든 모델을 REST API로 제공하는 서비스",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 모델 초기화
models = {
    "musicgen": MusicGen.get_pretrained("facebook/musicgen-small"),
    "audiogen": AudioGen.get_pretrained("facebook/audiogen-medium"),
    "encodec": EncodecModel.get_pretrained("facebook/encodec_24khz"),
    "multiband": MultiBandDiffusion.get_pretrained("facebook/multiband-diffusion")
}

# 판별자 초기화
discriminators = {
    "mpd": MultiPeriodDiscriminator(periods=[2, 3, 5, 7, 11], channels=32, kernel_size=5),
    "msd": MultiScaleDiscriminator(scales=[1, 2, 4], channels=32, kernel_size=5),
    "msstftd": MultiScaleSTFTDiscriminator(n_ffts=[1024, 2048, 4096], hop_lengths=[120, 240, 480], channels=32)
}

class TextToAudioRequest(BaseModel):
    """텍스트-오디오 생성 요청 모델"""
    text: str
    duration: float = 10.0
    temperature: float = 1.0
    top_k: int = 250
    top_p: float = 0.0
    cfg_coef: float = 3.0

class AudioAnalysisResponse(BaseModel):
    """오디오 분석 결과를 위한 응답 모델"""
    mpd_score: float
    msd_score: float
    msstftd_score: float
    feature_maps: List[List[float]]
    is_real: bool

def process_audio(audio_data: bytes) -> torch.Tensor:
    """오디오 데이터를 처리하여 텐서로 변환"""
    try:
        waveform, sample_rate = torchaudio.load(io.BytesIO(audio_data))
        if waveform.shape[0] > 1:
            waveform = torch.mean(waveform, dim=0, keepdim=True)
        return waveform
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"오디오 처리 중 오류 발생: {str(e)}")

@app.post("/generate/music", response_class=FileResponse)
async def generate_music(request: TextToAudioRequest):
    """
    텍스트 프롬프트를 사용하여 음악을 생성합니다.
    """
    try:
        model = models["musicgen"]
        model.set_generation_params(
            duration=request.duration,
            temperature=request.temperature,
            top_k=request.top_k,
            top_p=request.top_p,
            cfg_coef=request.cfg_coef
        )
        
        wav = model.generate([request.text])
        
        # 임시 파일로 저장
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            torchaudio.save(tmp.name, wav.cpu(), 32000)
            return tmp.name
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"음악 생성 중 오류 발생: {str(e)}")

@app.post("/generate/audio", response_class=FileResponse)
async def generate_audio(request: TextToAudioRequest):
    """
    텍스트 프롬프트를 사용하여 일반 오디오를 생성합니다.
    """
    try:
        model = models["audiogen"]
        model.set_generation_params(
            duration=request.duration,
            temperature=request.temperature,
            top_k=request.top_k,
            top_p=request.top_p,
            cfg_coef=request.cfg_coef
        )
        
        wav = model.generate([request.text])
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            torchaudio.save(tmp.name, wav.cpu(), 32000)
            return tmp.name
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"오디오 생성 중 오류 발생: {str(e)}")

@app.post("/encode")
async def encode_audio(
    audio_file: UploadFile = File(...),
    model: str = Form("encodec")
):
    """
    오디오를 EnCodec을 사용하여 인코딩합니다.
    """
    try:
        audio_data = await audio_file.read()
        waveform = process_audio(audio_data)
        
        model = models[model]
        codes = model.encode(waveform)
        
        return {"codes": codes.cpu().numpy().tolist()}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"인코딩 중 오류 발생: {str(e)}")

@app.post("/decode")
async def decode_audio(
    codes: List[List[int]] = Form(...),
    model: str = Form("encodec")
):
    """
    EnCodec 코드를 사용하여 오디오를 디코딩합니다.
    """
    try:
        model = models[model]
        codes = torch.tensor(codes)
        wav = model.decode(codes)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            torchaudio.save(tmp.name, wav.cpu(), 32000)
            return tmp.name
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"디코딩 중 오류 발생: {str(e)}")

@app.post("/analyze", response_model=AudioAnalysisResponse)
async def analyze_audio(
    audio_file: UploadFile = File(...),
    threshold: float = 0.5
):
    """
    오디오 파일을 분석하여 각 판별자의 결과를 반환합니다.
    """
    try:
        audio_data = await audio_file.read()
        waveform = process_audio(audio_data)
        
        with torch.no_grad():
            # MPD 분석
            mpd_logits, mpd_features = discriminators["mpd"](waveform)
            mpd_score = torch.mean(torch.sigmoid(mpd_logits[0])).item()
            
            # MSD 분석
            msd_logits, msd_features = discriminators["msd"](waveform)
            msd_score = torch.mean(torch.sigmoid(msd_logits[0])).item()
            
            # MS-STFT-D 분석
            msstftd_logits, msstftd_features = discriminators["msstftd"](waveform)
            msstftd_score = torch.mean(torch.sigmoid(msstftd_logits[0])).item()
            
            # 특징 맵 추출
            feature_maps = []
            for features in [mpd_features, msd_features, msstftd_features]:
                for feat in features:
                    feature_maps.append(feat.mean(dim=1).cpu().numpy().tolist())
        
        is_real = (mpd_score + msd_score + msstftd_score) / 3 > threshold
        
        return AudioAnalysisResponse(
            mpd_score=mpd_score,
            msd_score=msd_score,
            msstftd_score=msstftd_score,
            feature_maps=feature_maps,
            is_real=is_real
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"분석 중 오류 발생: {str(e)}")

@app.get("/health")
async def health_check():
    """API 서버 상태 확인"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "models": list(models.keys()),
        "discriminators": list(discriminators.keys())
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 