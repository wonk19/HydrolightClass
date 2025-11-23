HydroLight Run Header
 ├─ IOP Model, Atmosphere, Surface, Bottom Specs
 ├─ Absorption table
 ├─ Scattering table
 ├─ Backscattering table
 ├─ IOP summary table
 ├─ Asymptotic radiance (L∞) table
 ├─ Spectral irradiance table
 ├─ Spectral radiance & Rrs table
 ├─ Above-surface radiance/fQ table
 ├─ K-function table
 ├─ Band-integrated Eo / Quantum Eo tables
 └─ Run summary





## 1️⃣ Absorption Coefficients of Individual Components at 550 nm

| 열               | 설명                     |
| --------------- | ---------------------- |
| `iz`            | 수심 인덱스 (계산 그리드 번호)     |
| `Geo Depth (m)` | 실제 수심 (m)              |
| `Opt Depth`     | 무차원 광학 깊이 (τ = ∫ c dz) |
| `Comp 1`        | 성분별 흡수계수 a_i (1/m)     |
| `Total`         | 총 흡수계수 a (1/m) = Σ a_i |

> **무엇을 보는 테이블?**  
> 수심에 따른 흡수 (a) 프로파일. 여기서는 IOP_constant 모델이므로 모든 깊이에서 a = 0.1 m⁻¹ 로 상수.

---

## 2️⃣ Scattering Coefficients of Individual Components at 550 nm

| 열 | 설명 |  
| `Comp 1` | 성분별 산란계수 b_i (1/m) |  
| `Total` | 총 산란계수 b (1/m) |

> **의미:** 깊이에 따른 산란 (b) 분포. 여기서는 b = 0.4 m⁻¹ 상수.

---

## 3️⃣ Backscattering Coefficients of Individual Components at 550 nm

| 열 | 설명 |  
| `Comp 1` | 성분별 후방산란계수 bb_i (1/m) |  
| `Total` | 총 후방산란 bb (1/m) |

> **의미:** Petzold 평균 입자 위상함수를 이용해 b 로부터 계산된 bb (여기서는 bb = 0.00733 m⁻¹).

---

## 4️⃣ Summary of Inherent Optical Properties (IOPs)

| 열 | 설명 |  
| `total a`, `total b`, `total c` | 각각 흡수, 산란, 소멸계수 (c = a + b) |  
| `albedo` | 단일산란 반사도 = b/(a + b) |  
| `total bb` | 후방산란계수 |  
| `total bb/b` | 후방산란 비율 (bb/b) |

> **의미:** 깊이별 IOP 요약 표. 수심 증가와 무관하게 상수 값을 유지함.

---

## 5️⃣ L∞ (Asymptotic Radiance Distribution)

| 열 | 설명 |  
| `theta` | 방향각 (°) |  
| `Linf(theta)` | 무한심도에서의 정규화 복사휘도 분포 |

> **의미:** 심해에서 산출된 방향별 복사 분포 (L∞) – 수평균 복사 비 패턴.

---

## 6️⃣ Spectral Irradiances 및 Mean Cosines at 550 nm

| 열 | 설명 |  
| `Eou` | 상향 외부 복사 (air above surface) |  
| `Eod` | 하향 외부 복사 |  
| `Eo` | 총 복사 (= Eou + Eod) |  
| `Eu`, `Ed` | 수중 상향/하향 복사조도 |  
| `mubar_u`, `mubar_d`, `mubar` | 상향·하향 평균 코사인 |  
| `R = Eu/Ed` | 복사조도 반사율 |

> **의미:** 깊이에 따른 E와 평균 코사인, 반사율 프로파일.

---

## 7️⃣ Selected Spectral Radiances and Radiance–Irradiance Ratios

| 열 | 설명 |  
| `Lu(z)` | 상향 휘도 (θ = 180°) |  
| `Ld(z)` | 하향 휘도 (θ = 0°) |  
| `Lh(z,φ)` | 수평 방향 휘도 |  
| `Lu/Ed` | 상향 휘도 대 하향 복사조도 비 |  
| `Q = Eu/Lu` | Q-factor (복사조도 대 휘도 비 ) |  
| `Lw` | 수면 위 상향 복사 (워터리브 Radiance) |  
| `Rrs = Lw/Ed` | 원격반사도 (1/sr) |

> **의미:** 수심별 방향성 복사휘도 및 Rrs 산출 테이블.

---

## 8️⃣ Spectral Radiances Just Above Surface (+ f/Q)

| 열 | 설명 |  
| `Theta`, `Phi` | 관측 각도 (θ = 천정각, φ = 방위각) |  
| `L(sky)` | 하늘 휘도 |  
| `L(water-lv)` | 수면에서 나온 상향 휘도 |  
| `L(refl-sky)` | 하늘 반사 성분 |  
| `L(total up)` | 총 상향 휘도 |  
| `Rrs` | 정규화 반사도 |  
| `ρ (rho)` | 반사 비 (Lrefl/Lsky) |  
| `f/Q(z=0)` | 수면하 f/Q 인자 (1/sr) |

> **의미:** 수면 위 관측 각도별 스펙트럴 휘도 및 표면 반사·굴절 보정 관계.

---

## 9️⃣ K-functions (Attenuation Coefficients)

| 열 | 설명 |  
| `Kou`, `Kod`, `Ko`, `Ku`, `Kd`, `Knet`, `KLu` | 각각 상향/하향/순복사/순방향 감쇠계수 (1/m) |

> **의미:** 매우 짧은 Δz 구간에서의 국소적 복사 감쇠율 (K(z)).  
> Radiative transfer 미분형 파라미터 추정에 사용됨.

---

## 🔟 Band-Integrated Eo and Quantum Eo (광통합 값)

| 열 | 설명 |  
| `depth` | 수심 (m) |  
| `550.0` | 파장 밴드 중심(여기서는 단일밴드 550 nm) 에서의 Eo 또는 Quantum Eo |

> **의미:** 깊이별 밴드적분 복사조도 및 광양자 플럭스(μmol photons m⁻² s⁻¹).
