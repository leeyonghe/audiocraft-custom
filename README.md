# AudioCraft 튜닝 프로젝트
> ⚠️ 이 프로젝트는 [Facebook Research의 AudioCraft](https://github.com/facebookresearch/audiocraft)를 기반으로 한 튜닝 버전입니다.
> 원본 프로젝트는 [여기](https://github.com/facebookresearch/audiocraft)에서 확인하실 수 있습니다.

![docs badge](https://github.com/facebookresearch/audiocraft/workflows/audiocraft_docs/badge.svg)
![linter badge](https://github.com/facebookresearch/audiocraft/workflows/audiocraft_linter/badge.svg)
![tests badge](https://github.com/facebookresearch/audiocraft/workflows/audiocraft_tests/badge.svg)

AudioCraft는 오디오 생성에 대한 딥러닝 연구를 위한 PyTorch 라이브러리입니다. AudioCraft는 고품질 오디오를 생성하는 두 가지 최첨단 AI 생성 모델인 AudioGen과 MusicGen의 추론 및 학습 코드를 포함하고 있습니다.


## 설치
AudioCraft는 Python 3.9, PyTorch 2.1.0이 필요합니다. AudioCraft를 설치하려면 다음 명령어를 실행하세요:

```shell
# 먼저 torch가 설치되어 있는지 확인하는 것이 좋습니다. 특히 xformers를 설치하기 전에 확인하세요.
# 이미 PyTorch가 설치되어 있다면 이 명령어를 실행하지 마세요.
python -m pip install 'torch==2.1.0'
# 패키지를 설치하기 전에 다음이 필요할 수 있습니다
python -m pip install setuptools wheel
# 그런 다음 다음 중 하나를 실행하세요
python -m pip install -U audiocraft  # 안정 버전
python -m pip install -U git+https://git@github.com/facebookresearch/audiocraft#egg=audiocraft  # 최신 버전
python -m pip install -e .  # 또는 로컬에서 저장소를 클론한 경우 (학습을 원한다면 필수)
python -m pip install -e '.[wm]'  # 워터마킹 모델을 학습하고 싶은 경우
```

또한 시스템이나 Anaconda를 통해 `ffmpeg`를 설치하는 것을 권장합니다:
```bash
sudo apt-get install ffmpeg
# 또는 Anaconda나 Miniconda를 사용하는 경우
conda install "ffmpeg<5" -c conda-forge
```

## 모델

현재 AudioCraft는 다음 모델들의 학습 코드와 추론 코드를 포함하고 있습니다:
* [MusicGen](./docs/MUSICGEN.md): 최첨단 제어 가능한 텍스트-투-뮤직 모델
* [AudioGen](./docs/AUDIOGEN.md): 최첨단 텍스트-투-사운드 모델
* [EnCodec](./docs/ENCODEC.md): 최첨단 고품질 신경 오디오 코덱
* [Multi Band Diffusion](./docs/MBD.md): EnCodec 호환 디퓨전 기반 디코더
* [MAGNeT](./docs/MAGNET.md): 텍스트-투-뮤직과 텍스트-투-사운드를 위한 최첨단 비자기회귀 모델
* [AudioSeal](./docs/WATERMARKING.md): 최첨단 오디오 워터마킹
* [MusicGen Style](./docs/MUSICGEN_STYLE.md): 최첨단 텍스트-스타일-투-뮤직 모델
* [JASCO](./docs/JASCO.md): "코드, 멜로디, 드럼 트랙에 조건부로 작동하는 고품질 텍스트-투-뮤직 모델"


## 학습 코드

AudioCraft는 오디오 딥러닝 연구를 위한 PyTorch 컴포넌트와 개발된 모델들의 학습 파이프라인을 포함하고 있습니다.
AudioCraft의 설계 원칙과 자체 학습 파이프라인을 개발하기 위한 지침에 대한 일반적인 소개는 [AudioCraft 학습 문서](./docs/TRAINING.md)를 참조하세요.

기존 작업을 재현하고 개발된 학습 파이프라인을 사용하려면, 각 특정 모델에 대한 지침을 참조하세요.
각 모델별 문서는 구성, 예제 그리드, 모델/작업별 정보 및 FAQ에 대한 포인터를 제공합니다.


## API 문서

AudioCraft에 대한 [API 문서](https://facebookresearch.github.io/audiocraft/api_docs/audiocraft/index.html)를 제공합니다.


## FAQ

#### 학습 코드를 사용할 수 있나요?

네! [EnCodec](./docs/ENCODEC.md), [MusicGen](./docs/MUSICGEN.md), [Multi Band Diffusion](./docs/MBD.md), [JASCO](./docs/JASCO.md)의 학습 코드를 제공합니다.

#### 모델은 어디에 저장되나요?

Hugging Face는 모델을 특정 위치에 저장하며, AudioCraft 모델의 경우 `AUDIOCRAFT_CACHE_DIR` 환경 변수를 설정하여 캐시 위치를 재정의할 수 있습니다.
다른 Hugging Face 모델의 캐시 위치를 변경하려면 [Hugging Face Transformers 캐시 설정 문서](https://huggingface.co/docs/transformers/installation#cache-setup)를 확인하세요.
마지막으로, Demucs에 의존하는 모델(예: `musicgen-melody`)을 사용하고 Demucs의 다운로드 위치를 변경하고 싶다면 [Torch Hub 문서](https://pytorch.org/docs/stable/hub.html#where-are-my-downloaded-models-saved)를 참조하세요.


## 라이선스
* 이 저장소의 코드는 [LICENSE 파일](LICENSE)에 명시된 대로 MIT 라이선스 하에 배포됩니다.
* 이 저장소의 모델 가중치는 [LICENSE_weights 파일](LICENSE_weights)에 명시된 대로 CC-BY-NC 4.0 라이선스 하에 배포됩니다.


## 인용

AudioCraft의 일반적인 프레임워크에 대해서는 다음을 인용해 주세요.
```
@inproceedings{copet2023simple,
    title={Simple and Controllable Music Generation},
    author={Jade Copet and Felix Kreuk and Itai Gat and Tal Remez and David Kant and Gabriel Synnaeve and Yossi Adi and Alexandre Défossez},
    booktitle={Thirty-seventh Conference on Neural Information Processing Systems},
    year={2023},
}
```

특정 모델을 인용할 때는 해당 모델의 README에 언급된 대로 인용해 주세요. 예를 들어
[./docs/MUSICGEN.md](./docs/MUSICGEN.md), [./docs/AUDIOGEN.md](./docs/AUDIOGEN.md) 등.
