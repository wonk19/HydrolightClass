# HydrolightClass

Hydrolight 실행 결과 분석 및 시각화 도구 모음

## 프로젝트 개요

이 프로젝트는 HydroLight 방사 전달 모델의 출력 결과를 파싱하고, 다양한 해양 광학 특성을 시각화하는 Python 스크립트들을 포함합니다.

## 주요 기능

### 1. P01_plot_ref.py
- Bottom reflectance 스펙트럼 파싱 및 플롯
- 해저면 반사도 데이터 시각화

### 2. P02_GUI_bottom.py
- Bottom reflectance 파일 선택 및 시각화를 위한 GUI 애플리케이션
- 여러 반사도 스펙트럼을 동시에 비교 가능 (Hold 기능)
- 실시간 플롯 업데이트

### 3. P03_parse_HL_results.py
- HydroLight 출력 파일 파싱
- 다양한 해양 광학 특성 플롯 생성:
  - IOPs (Inherent Optical Properties): 흡수, 산란, 후방산란
  - Irradiances: Ed, Eu, Eo 등
  - Radiances: Lu, Ld 등
  - K-functions: Kd, Ku, Ko, KLu
  - 깊이별/파장별 스펙트럼 분석
  - Irradiance reflectance (R = Eu/Ed)
  - Lu/Ed ratio

### 4. P04_compare_exe04_and_exe05.py
- 두 HydroLight 실행 결과 비교 분석
- Lu (Upwelling radiance) 스펙트럼 비교
- Ed (Downward irradiance) 차이 분석
- (Lu 차이)/(Ed) 비율 계산

### 5. library_hydrolight.py
- HydroLight 데이터 파싱을 위한 유틸리티 함수들

## 디렉토리 구조

```
.
├── data/                          # 입력 데이터
│   ├── bottom_reflectances/       # 해저면 반사도 데이터
│   └── PExe*.txt                  # HydroLight 출력 파일
├── procedures/                    # 분석 스크립트
│   ├── P01_plot_ref.py
│   ├── P02_GUI_bottom.py
│   ├── P03_parse_HL_results.py
│   ├── P04_compare_exe04_and_exe05.py
│   └── library_hydrolight.py
└── results/                       # 생성된 플롯 (git 제외)
```

## 사용 방법

### 필요 패키지 설치

```bash
pip install numpy pandas matplotlib tkinter
```

### 스크립트 실행

```bash
# Bottom reflectance 플롯
python procedures/P01_plot_ref.py

# GUI 실행
python procedures/P02_GUI_bottom.py

# HydroLight 결과 파싱 및 플롯
python procedures/P03_parse_HL_results.py

# 두 실험 결과 비교
python procedures/P04_compare_exe04_and_exe05.py
```

## 데이터 형식

### HydroLight 출력 파일
- 각 파장별로 구분된 블록 구조
- IOPs, Irradiances, Radiances, K-functions 섹션 포함

### Bottom Reflectance 파일
- `\begin_header`, `\end_header`, `\begin_data`, `\end_data` 구조
- 파장(nm)과 반사도 값의 2열 형식

## 출력 결과

모든 플롯은 300 DPI PNG 형식으로 `results/` 디렉토리에 저장됩니다:
- 깊이별 광학 특성 플롯
- 파장별 스펙트럼 플롯
- 비교 분석 플롯

## 라이선스

MIT License

## 저자

wonk19

## 참고 자료

HydroLight 방사 전달 모델에 대한 자세한 정보:
- [Sequoia Scientific - HydroLight](https://www.sequoiasci.com/product/hydrolight/)

