"""
P04_compare_exe04_and_exe05.py
PExe04와 PExe05의 Lu(Upwelling radiance) 스펙트럼 비교
"""

import os
import re
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path


def parse_irradiances_improved(raw_lines):
    """Spectral Irradiances 블록 파싱"""
    start = None
    for i, line in enumerate(raw_lines):
        if "Spectral Irradiances [units of W/(m^2 nm)]" in line:
            start = i
            break
    if start is None:
        return pd.DataFrame()
    
    # 데이터 시작 찾기 (헤더 다음)
    data_start = None
    for i in range(start, min(start + 20, len(raw_lines))):
        if "R = Eu/Ed" in raw_lines[i]:
            data_start = i + 1
            break
    
    if data_start is None:
        return pd.DataFrame()
    
    rows = []
    for line in raw_lines[data_start:]:
        s = line.strip()
        if not s:
            continue
        if s.startswith("Selected Spectral") or s.startswith("K-functions"):
            break
        if "in air" in s:
            continue
        
        parts = s.split()
        if len(parts) >= 12 and parts[0].isdigit():
            try:
                iz = int(parts[0])
                z = float(parts[1])
                zeta = float(parts[2])
                Eou = float(parts[3])
                Eod = float(parts[4])
                Eo = float(parts[5])
                Eu = float(parts[6])
                Ed = float(parts[7])
                mubar_u = float(parts[8])
                mubar_d = float(parts[9])
                mubar = float(parts[10])
                R = float(parts[11])
                rows.append([iz, z, zeta, Eou, Eod, Eo, Eu, Ed, mubar_u, mubar_d, mubar, R])
            except:
                pass
    
    if not rows:
        return pd.DataFrame()
    
    cols = ["iz","z_m","zeta","Eou","Eod","Eo","Eu","Ed","mubar_u","mubar_d","mubar","R"]
    return pd.DataFrame(rows, columns=cols)


def parse_radiances_improved(raw_lines):
    """Selected Radiances 블록 파싱"""
    start = None
    for i, line in enumerate(raw_lines):
        if "Selected Spectral Radiances [units of W/(m^2 sr nm)]" in line:
            start = i
            break
    if start is None:
        return pd.DataFrame()
    
    # 데이터 시작 찾기
    data_start = None
    for i in range(start, min(start + 20, len(raw_lines))):
        if "(theta=180)" in raw_lines[i]:
            data_start = i + 1
            break
    
    if data_start is None:
        return pd.DataFrame()
    
    rows = []
    for line in raw_lines[data_start:]:
        s = line.strip()
        if not s:
            continue
        if "Spectral Radiances Just Above" in s or "K-functions" in s:
            break
        if "in air" in s:
            continue
        
        parts = s.split()
        if len(parts) >= 10 and parts[0].isdigit():
            try:
                iz = int(parts[0])
                z = float(parts[1])
                zeta = float(parts[2])
                Lu = float(parts[3])
                Ld = float(parts[4])
                Lh0 = float(parts[5])
                Lh90 = float(parts[6])
                Lh180 = float(parts[7])
                Lu_over_Ed = float(parts[8])
                Q = float(parts[9])
                rows.append([iz, z, zeta, Lu, Ld, Lh0, Lh90, Lh180, Lu_over_Ed, Q])
            except:
                pass
    
    if not rows:
        return pd.DataFrame()
    
    cols = ["iz","z","zeta","Lu","Ld","Lh0","Lh90","Lh180","Lu_over_Ed","Q"]
    return pd.DataFrame(rows, columns=cols)


def parse_hydrolight_data(filepath):
    """HydroLight 결과 파일에서 Irradiances와 Radiances 파싱"""
    print(f"Reading file: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        raw_lines = f.readlines()
    
    print(f"Total lines: {len(raw_lines)}")
    
    # 파장 목록 추출
    wavelengths = []
    for i, line in enumerate(raw_lines):
        if "Summary of Inherent Optical Properties at" in line:
            match = re.search(r"at\s+([\d.]+)\s*nm", line)
            if match:
                wl = float(match.group(1))
                wavelengths.append((wl, i))
    
    print(f"Found {len(wavelengths)} wavelengths: {[w[0] for w in wavelengths]}")
    
    # 각 파장별로 데이터 파싱
    irradiances_list = []
    radiances_list = []
    
    for wl, start_idx in wavelengths:
        # 다음 파장까지의 라인 추출 (또는 파일 끝까지)
        next_idx = wavelengths[wavelengths.index((wl, start_idx)) + 1][1] if wavelengths.index((wl, start_idx)) < len(wavelengths) - 1 else len(raw_lines)
        block_lines = raw_lines[start_idx:next_idx]
        
        # Irradiances 파싱
        irrad_df = parse_irradiances_improved(block_lines)
        if not irrad_df.empty:
            irrad_df['wavelength'] = wl
            irradiances_list.append(irrad_df)
        
        # Radiances 파싱
        rad_df = parse_radiances_improved(block_lines)
        if not rad_df.empty:
            rad_df['wavelength'] = wl
            radiances_list.append(rad_df)
    
    # DataFrame 병합
    result = {}
    
    if irradiances_list:
        result['irradiances'] = pd.concat(irradiances_list, ignore_index=True)
        print(f"Total irradiances: {len(result['irradiances'])} rows")
    else:
        result['irradiances'] = pd.DataFrame()
        print("No irradiances data found")
    
    if radiances_list:
        result['radiances'] = pd.concat(radiances_list, ignore_index=True)
        print(f"Total radiances: {len(result['radiances'])} rows")
    else:
        result['radiances'] = pd.DataFrame()
        print("No radiances data found")
    
    return result


def plot_Lu_spectrum(df, output_dir, title, filename, color_scheme='viridis'):
    """깊이별 Lu 스펙트럼 플롯"""
    if df.empty:
        print(f"No data to plot: {filename}")
        return
    
    print(f"\nPlotting {title}...")
    depths = sorted(df['z'].unique())
    colors = plt.cm.get_cmap(color_scheme)(np.linspace(0, 1, len(depths)))
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    for i, depth in enumerate(depths):
        data = df[df['z'] == depth].sort_values('wavelength')
        ax.plot(data['wavelength'], data['Lu'], '-o', color=colors[i], 
                linewidth=2, markersize=4, label=f'{depth:.1f} m')
    
    ax.set_xlabel('Wavelength (nm)', fontsize=12)
    ax.set_ylabel('Upwelling Radiance Lu [W/(m² sr nm)]', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=9, title='Depth', ncol=2, loc='best')
    
    plt.tight_layout()
    output_file = output_dir / filename
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Saved: {output_file}")
    plt.close()


def plot_Lu_difference(df_exe04, df_exe05, output_dir):
    """깊이별 Lu 차이 스펙트럼 플롯 (Exe04 - Exe05)"""
    if df_exe04.empty or df_exe05.empty:
        print("No data to plot difference")
        return
    
    print("\nPlotting Lu Difference (Exe04 - Exe05)...")
    
    # 두 데이터프레임을 병합
    exe04_subset = df_exe04[['wavelength', 'z', 'Lu']].copy()
    exe05_subset = df_exe05[['wavelength', 'z', 'Lu']].copy()
    
    exe04_subset.rename(columns={'Lu': 'Lu_exe04'}, inplace=True)
    exe05_subset.rename(columns={'Lu': 'Lu_exe05'}, inplace=True)
    
    # 병합
    merged = pd.merge(exe04_subset, exe05_subset, on=['wavelength', 'z'], how='inner')
    
    # 차이 계산
    merged['Lu_diff'] = merged['Lu_exe04'] - merged['Lu_exe05']
    
    # 플롯
    depths = sorted(merged['z'].unique())
    colors = plt.cm.plasma(np.linspace(0, 1, len(depths)))
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    for i, depth in enumerate(depths):
        data = merged[merged['z'] == depth].sort_values('wavelength')
        ax.plot(data['wavelength'], data['Lu_diff'], '-o', color=colors[i], 
                linewidth=2, markersize=4, label=f'{depth:.1f} m')
    
    ax.set_xlabel('Wavelength (nm)', fontsize=12)
    ax.set_ylabel('Lu Difference (Exe04 - Exe05) [W/(m² sr nm)]', fontsize=12)
    ax.set_title('Lu Difference: PExe04 - PExe05 by Depth', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=9, title='Depth', ncol=2, loc='best')
    ax.axhline(y=0, color='black', linestyle='--', linewidth=1, alpha=0.5)
    
    plt.tight_layout()
    output_file = output_dir / 'Lu_difference_exe04_minus_exe05.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Saved: {output_file}")
    plt.close()


def plot_Ed_difference(irrad_exe04, irrad_exe05, output_dir):
    """깊이별 Ed 차이 스펙트럼 플롯 (Exe04 - Exe05)"""
    if irrad_exe04.empty or irrad_exe05.empty:
        print("No data to plot Ed difference")
        return
    
    print("\nPlotting Ed Difference (Exe04 - Exe05)...")
    
    # 두 데이터프레임을 병합 (depth 컬럼명은 z_m)
    exe04_subset = irrad_exe04[['wavelength', 'z_m', 'Ed']].copy()
    exe05_subset = irrad_exe05[['wavelength', 'z_m', 'Ed']].copy()
    
    exe04_subset.rename(columns={'Ed': 'Ed_exe04'}, inplace=True)
    exe05_subset.rename(columns={'Ed': 'Ed_exe05'}, inplace=True)
    
    # 병합
    merged = pd.merge(exe04_subset, exe05_subset, on=['wavelength', 'z_m'], how='inner')
    
    # 차이 계산
    merged['Ed_diff'] = merged['Ed_exe04'] - merged['Ed_exe05']
    
    # 플롯
    depths = sorted(merged['z_m'].unique())
    colors = plt.cm.plasma(np.linspace(0, 1, len(depths)))
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    for i, depth in enumerate(depths):
        data = merged[merged['z_m'] == depth].sort_values('wavelength')
        ax.plot(data['wavelength'], data['Ed_diff'], '-o', color=colors[i], 
                linewidth=2, markersize=4, label=f'{depth:.1f} m')
    
    ax.set_xlabel('Wavelength (nm)', fontsize=12)
    ax.set_ylabel('Ed Difference (Exe04 - Exe05) [W/(m² nm)]', fontsize=12)
    ax.set_title('Ed Difference: PExe04 - PExe05 by Depth', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=9, title='Depth', ncol=2, loc='best')
    ax.axhline(y=0, color='black', linestyle='--', linewidth=1, alpha=0.5)
    
    plt.tight_layout()
    output_file = output_dir / 'Ed_difference_exe04_minus_exe05.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Saved: {output_file}")
    plt.close()


def plot_Lu_diff_over_Ed_exe05(rad_exe04, rad_exe05, irrad_exe05, output_dir):
    """깊이별 (Lu 차이) / (Ed of Exe05) 스펙트럼 플롯"""
    if rad_exe04.empty or rad_exe05.empty or irrad_exe05.empty:
        print("No data to plot Lu_diff/Ed_exe05")
        return
    
    print("\nPlotting (Lu Difference) / (Ed Exe05)...")
    
    # Radiances에서 Lu 추출
    rad04_subset = rad_exe04[['wavelength', 'z', 'Lu']].copy()
    rad05_subset = rad_exe05[['wavelength', 'z', 'Lu']].copy()
    
    rad04_subset.rename(columns={'Lu': 'Lu_exe04'}, inplace=True)
    rad05_subset.rename(columns={'Lu': 'Lu_exe05'}, inplace=True)
    
    # Lu 병합
    lu_merged = pd.merge(rad04_subset, rad05_subset, on=['wavelength', 'z'], how='inner')
    lu_merged['Lu_diff'] = lu_merged['Lu_exe04'] - lu_merged['Lu_exe05']
    
    # Irradiances에서 Ed 추출 (depth 컬럼명은 z_m)
    irrad05_subset = irrad_exe05[['wavelength', 'z_m', 'Ed']].copy()
    irrad05_subset.rename(columns={'z_m': 'z', 'Ed': 'Ed_exe05'}, inplace=True)
    
    # Lu_diff와 Ed_exe05 병합
    final_merged = pd.merge(lu_merged[['wavelength', 'z', 'Lu_diff']], 
                           irrad05_subset, 
                           on=['wavelength', 'z'], 
                           how='inner')
    
    # 비율 계산
    final_merged['Lu_diff_over_Ed'] = final_merged['Lu_diff'] / final_merged['Ed_exe05']
    
    # 플롯
    depths = sorted(final_merged['z'].unique())
    colors = plt.cm.plasma(np.linspace(0, 1, len(depths)))
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    for i, depth in enumerate(depths):
        data = final_merged[final_merged['z'] == depth].sort_values('wavelength')
        ax.plot(data['wavelength'], data['Lu_diff_over_Ed'], '-o', color=colors[i], 
                linewidth=2, markersize=4, label=f'{depth:.1f} m')
    
    ax.set_xlabel('Wavelength (nm)', fontsize=12)
    ax.set_ylabel('(Lu_diff / Ed_Exe05) [sr⁻¹]', fontsize=12)
    ax.set_title('(Lu Difference) / (Ed of PExe05) by Depth', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=9, title='Depth', ncol=2, loc='best')
    ax.axhline(y=0, color='black', linestyle='--', linewidth=1, alpha=0.5)
    
    plt.tight_layout()
    output_file = output_dir / 'Lu_diff_over_Ed_exe05.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Saved: {output_file}")
    plt.close()


def main():
    print("="*50)
    print("P04_compare_exe04_and_exe05.py STARTED")
    print("="*50)
    
    # 파일 경로 설정
    data_dir = Path(r"C:\HE60\cursor\data")
    exe04_file = data_dir / "PExe04.txt"
    exe05_file = data_dir / "PExe05.txt"
    
    # 출력 폴더 생성
    output_dir = Path(r"C:\HE60\cursor\results\P04_compare_exe04_and_exe05")
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"Output directory: {output_dir}")
    
    # 데이터 파싱
    print("\n" + "="*50)
    print("Parsing PExe04.txt...")
    print("="*50)
    data_exe04 = parse_hydrolight_data(exe04_file)
    irradiances_exe04 = data_exe04['irradiances']
    radiances_exe04 = data_exe04['radiances']
    
    print("\n" + "="*50)
    print("Parsing PExe05.txt...")
    print("="*50)
    data_exe05 = parse_hydrolight_data(exe05_file)
    irradiances_exe05 = data_exe05['irradiances']
    radiances_exe05 = data_exe05['radiances']
    
    # 플롯 생성
    print("\n" + "="*50)
    print("Creating comparison plots...")
    print("="*50)
    
    # 1. PExe04 Lu 스펙트럼
    plot_Lu_spectrum(radiances_exe04, output_dir, 
                     'Upwelling Radiance (Lu) - PExe04', 
                     'Lu_spectrum_PExe04.png',
                     color_scheme='viridis')
    
    # 2. PExe05 Lu 스펙트럼
    plot_Lu_spectrum(radiances_exe05, output_dir, 
                     'Upwelling Radiance (Lu) - PExe05', 
                     'Lu_spectrum_PExe05.png',
                     color_scheme='viridis')
    
    # 3. Lu 차이 플롯
    plot_Lu_difference(radiances_exe04, radiances_exe05, output_dir)
    
    # 4. Ed 차이 플롯
    plot_Ed_difference(irradiances_exe04, irradiances_exe05, output_dir)
    
    # 5. (Lu 차이) / (Ed of Exe05) 플롯
    plot_Lu_diff_over_Ed_exe05(radiances_exe04, radiances_exe05, irradiances_exe05, output_dir)
    
    print("\n" + "="*50)
    print("All plots completed!")
    print("="*50)
    print(f"\nResults saved in: {output_dir}")


if __name__ == "__main__":
    main()

