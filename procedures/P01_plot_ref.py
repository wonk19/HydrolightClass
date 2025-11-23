"""
P01_plot_ref.py
해초 바닥 반사도 스펙트럼 데이터를 파싱하고 그래프로 시각화
"""

import matplotlib
matplotlib.use('Agg')  # GUI 백엔드 비활성화
import matplotlib.pyplot as plt
import os

# 데이터 파일 경로
data_file = r"C:\HE60\cursor\data\bottom_reflectances\avg_clean_seagrass.txt"
output_dir = r"C:\HE60\cursor\results\P01_plot_ref"

# 출력 디렉토리 생성
os.makedirs(output_dir, exist_ok=True)

# 데이터 파싱
wavelengths = []
reflectances = []

with open(data_file, 'r', encoding='utf-8') as f:
    in_data = False
    for line in f:
        line = line.strip()
        
        # 헤더 끝 확인
        if '\\end_header' in line:
            in_data = True
            continue
        
        # 데이터 끝 확인
        if '\\end_data' in line:
            break
        
        # 데이터 읽기
        if in_data and line:
            try:
                parts = line.split()
                if len(parts) >= 2 and not line.startswith('\\'):
                    wavelengths.append(float(parts[0]))
                    reflectances.append(float(parts[1]))
            except:
                pass

# 그래프 그리기
plt.figure(figsize=(10, 6))
plt.plot(wavelengths, reflectances, 'b-', linewidth=2, label='Average Clean Seagrass')
plt.xlabel('Wavelength (nm)', fontsize=12)
plt.ylabel('Reflectance (nondimensional)', fontsize=12)
plt.title('Bottom Reflectance Spectrum - Average Clean Seagrass', fontsize=14, fontweight='bold')
plt.grid(True, alpha=0.3)
plt.legend(fontsize=10)
plt.tight_layout()

# 그래프 저장
output_file = os.path.join(output_dir, 'seagrass_reflectance_spectrum.png')
plt.savefig(output_file, dpi=300, bbox_inches='tight')

# 결과 출력
print(f"그래프가 저장되었습니다: {output_file}")
print(f"\n데이터 요약:")
print(f"  - 총 데이터 포인트: {len(wavelengths)}")
print(f"  - 파장 범위: {min(wavelengths):.1f} - {max(wavelengths):.1f} nm")
print(f"  - 반사도 범위: {min(reflectances):.5f} - {max(reflectances):.5f}")
print("\n처리 완료!")
