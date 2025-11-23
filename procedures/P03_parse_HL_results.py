"""
P03_parse_HL_results.py
Hydrolight 실행 결과를 파싱하고 다양한 플롯을 생성
"""

import sys
import os
import re
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path

# 개선된 파싱 함수들
def parse_irradiances_improved(raw_lines):
    """Spectral Irradiances 블록 파싱 (개선된 버전)"""
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


def parse_iops_improved(raw_lines):
    """IOPs 블록 파싱 (개선된 버전)"""
    start = None
    for i, line in enumerate(raw_lines):
        if "Summary of Inherent Optical Properties at" in line:
            start = i
            break
    if start is None:
        return pd.DataFrame()
    
    # 데이터 헤더 찾기
    data_start = None
    for i in range(start, min(start + 30, len(raw_lines))):
        if "total bb/b" in raw_lines[i] or "Geo Depth" in raw_lines[i]:
            data_start = i + 1
            break
    
    if data_start is None:
        return pd.DataFrame()
    
    rows = []
    for line in raw_lines[data_start:]:
        s = line.strip()
        if not s:
            continue
        if "Spectral Irradiances" in s or "chlorophyll" in s.lower():
            break
        
        parts = s.split()
        if len(parts) >= 9 and parts[0].isdigit():
            try:
                iz = int(parts[0])
                geo_depth = float(parts[1])
                opt_depth = float(parts[2])
                total_a = float(parts[3])
                total_b = float(parts[4])
                total_c = float(parts[5])
                albedo = float(parts[6])
                total_bb = float(parts[7])
                bb_over_b = float(parts[8])
                rows.append([iz, geo_depth, opt_depth, total_a, total_b, total_c, albedo, total_bb, bb_over_b])
            except:
                pass
    
    if not rows:
        return pd.DataFrame()
    
    cols = ["iz","Geo_Depth","Opt_Depth","total_a","total_b","total_c","albedo","total_bb","total_bb_over_b"]
    return pd.DataFrame(rows, columns=cols)


def parse_radiances_improved(raw_lines):
    """Selected Radiances 블록 파싱 (개선된 버전)"""
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


def parse_kfunctions(raw_lines):
    """K-functions 블록 파싱 (개선된 버전)"""
    start = None
    for i, line in enumerate(raw_lines):
        if "K-functions (units of 1/meter)" in line:
            start = i
            break
    if start is None:
        return pd.DataFrame()
    
    # 데이터 헤더 찾기
    data_start = None
    for i in range(start, min(start + 20, len(raw_lines))):
        if "KLu(z)" in raw_lines[i]:
            data_start = i + 1
            break
    
    if data_start is None:
        return pd.DataFrame()
    
    rows = []
    for line in raw_lines[data_start:]:
        s = line.strip()
        if not s:
            continue
        if "Waveband" in s or "Output for wavelength" in s or "Summary of" in s:
            break
        
        parts = s.split()
        # zupper, zlower, z, Kou, Kod, Ko, Ku, Kd, Knet, KLu
        if len(parts) >= 10:
            try:
                zupper = float(parts[0])
                zlower = float(parts[1])
                z = float(parts[2])
                Kou = float(parts[3])
                Kod = float(parts[4])
                Ko = float(parts[5])
                Ku = float(parts[6])
                Kd = float(parts[7])
                Knet = float(parts[8])
                KLu = float(parts[9])
                rows.append([z, Kd, Ku, Ko, Knet, KLu])
            except:
                pass
    
    if not rows:
        return pd.DataFrame()
    
    cols = ["depth", "Kd", "Ku", "Ko", "Knet", "KLu"]
    return pd.DataFrame(rows, columns=cols)


def parse_hydrolight_file(filepath):
    """HydroLight 결과 파일 전체 파싱"""
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
    all_data = {
        'iops': [],
        'irradiances': [],
        'radiances': [],
        'kfunctions': []
    }
    
    for wl, start_idx in wavelengths:
        print(f"\nParsing wavelength {wl} nm...")
        
        # 다음 파장까지의 라인 추출 (또는 파일 끝까지)
        next_idx = wavelengths[wavelengths.index((wl, start_idx)) + 1][1] if wavelengths.index((wl, start_idx)) < len(wavelengths) - 1 else len(raw_lines)
        block_lines = raw_lines[start_idx:next_idx]
        
        # IOPs 파싱
        iops_df = parse_iops_improved(block_lines)
        if not iops_df.empty:
            iops_df['wavelength'] = wl
            all_data['iops'].append(iops_df)
            print(f"  IOPs: {len(iops_df)} rows")
        
        # Irradiances 파싱
        irrad_df = parse_irradiances_improved(block_lines)
        if not irrad_df.empty:
            irrad_df['wavelength'] = wl
            all_data['irradiances'].append(irrad_df)
            print(f"  Irradiances: {len(irrad_df)} rows")
        
        # Radiances 파싱
        rad_df = parse_radiances_improved(block_lines)
        if not rad_df.empty:
            rad_df['wavelength'] = wl
            all_data['radiances'].append(rad_df)
            print(f"  Radiances: {len(rad_df)} rows")
        
        # K-functions 파싱
        k_df = parse_kfunctions(block_lines)
        if not k_df.empty:
            k_df['wavelength'] = wl
            all_data['kfunctions'].append(k_df)
            print(f"  K-functions: {len(k_df)} rows")
    
    # DataFrame 병합
    result = {}
    for key in all_data:
        if all_data[key]:
            result[key] = pd.concat(all_data[key], ignore_index=True)
            print(f"\nTotal {key}: {len(result[key])} rows")
        else:
            result[key] = pd.DataFrame()
            print(f"\nTotal {key}: 0 rows")
    
    return result


def plot_iops(df, output_dir):
    """IOPs 플롯 생성"""
    if df.empty:
        print("No IOPs data to plot")
        return
    
    print("\nPlotting IOPs...")
    wavelengths = sorted(df['wavelength'].unique())
    colors = plt.cm.jet(np.linspace(0, 1, len(wavelengths)))
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle('Inherent Optical Properties vs Depth', fontsize=14, fontweight='bold')
    
    # Total absorption
    ax = axes[0, 0]
    for i, wl in enumerate(wavelengths):
        data = df[df['wavelength'] == wl]
        ax.plot(data['total_a'], data['Geo_Depth'], '-o', color=colors[i], 
                label=f'{int(wl)} nm', markersize=4)
    ax.set_xlabel('Total Absorption a (1/m)', fontsize=10)
    ax.set_ylabel('Depth (m)', fontsize=10)
    ax.set_title('(a) Total Absorption', fontweight='bold')
    ax.invert_yaxis()
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=7, ncol=2)
    
    # Total scattering
    ax = axes[0, 1]
    for i, wl in enumerate(wavelengths):
        data = df[df['wavelength'] == wl]
        ax.plot(data['total_b'], data['Geo_Depth'], '-o', color=colors[i], 
                label=f'{int(wl)} nm', markersize=4)
    ax.set_xlabel('Total Scattering b (1/m)', fontsize=10)
    ax.set_ylabel('Depth (m)', fontsize=10)
    ax.set_title('(b) Total Scattering', fontweight='bold')
    ax.invert_yaxis()
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=7, ncol=2)
    
    # Albedo
    ax = axes[1, 0]
    for i, wl in enumerate(wavelengths):
        data = df[df['wavelength'] == wl]
        ax.plot(data['albedo'], data['Geo_Depth'], '-o', color=colors[i], 
                label=f'{int(wl)} nm', markersize=4)
    ax.set_xlabel('Single Scattering Albedo ω₀', fontsize=10)
    ax.set_ylabel('Depth (m)', fontsize=10)
    ax.set_title('(c) Single Scattering Albedo', fontweight='bold')
    ax.invert_yaxis()
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=7, ncol=2)
    
    # Backscattering ratio
    ax = axes[1, 1]
    for i, wl in enumerate(wavelengths):
        data = df[df['wavelength'] == wl]
        ax.plot(data['total_bb_over_b'], data['Geo_Depth'], '-o', color=colors[i], 
                label=f'{int(wl)} nm', markersize=4)
    ax.set_xlabel('Backscattering Ratio bb/b', fontsize=10)
    ax.set_ylabel('Depth (m)', fontsize=10)
    ax.set_title('(d) Backscattering Ratio', fontweight='bold')
    ax.invert_yaxis()
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=7, ncol=2)
    
    plt.tight_layout()
    output_file = output_dir / 'IOPs_vs_depth.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Saved: {output_file}")
    plt.close()


def plot_irradiances(df, output_dir):
    """Irradiances 플롯 생성"""
    if df.empty:
        print("No irradiances data to plot")
        return
    
    print("\nPlotting Irradiances...")
    wavelengths = sorted(df['wavelength'].unique())
    colors = plt.cm.jet(np.linspace(0, 1, len(wavelengths)))
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle('Spectral Irradiances vs Depth', fontsize=14, fontweight='bold')
    
    # Downward irradiance Ed
    ax = axes[0, 0]
    for i, wl in enumerate(wavelengths):
        data = df[df['wavelength'] == wl]
        ax.semilogx(data['Ed'], data['z_m'], '-o', color=colors[i], 
                    label=f'{int(wl)} nm', markersize=4)
    ax.set_xlabel('Ed [W/(m² nm)]', fontsize=10)
    ax.set_ylabel('Depth (m)', fontsize=10)
    ax.set_title('(a) Downward Irradiance Ed', fontweight='bold')
    ax.invert_yaxis()
    ax.grid(True, alpha=0.3, which='both')
    ax.legend(fontsize=7, ncol=2)
    
    # Upward irradiance Eu
    ax = axes[0, 1]
    for i, wl in enumerate(wavelengths):
        data = df[df['wavelength'] == wl]
        ax.semilogx(data['Eu'], data['z_m'], '-o', color=colors[i], 
                    label=f'{int(wl)} nm', markersize=4)
    ax.set_xlabel('Eu [W/(m² nm)]', fontsize=10)
    ax.set_ylabel('Depth (m)', fontsize=10)
    ax.set_title('(b) Upward Irradiance Eu', fontweight='bold')
    ax.invert_yaxis()
    ax.grid(True, alpha=0.3, which='both')
    ax.legend(fontsize=7, ncol=2)
    
    # Scalar irradiance Eo
    ax = axes[1, 0]
    for i, wl in enumerate(wavelengths):
        data = df[df['wavelength'] == wl]
        ax.semilogx(data['Eo'], data['z_m'], '-o', color=colors[i], 
                    label=f'{int(wl)} nm', markersize=4)
    ax.set_xlabel('Eo [W/(m² nm)]', fontsize=10)
    ax.set_ylabel('Depth (m)', fontsize=10)
    ax.set_title('(c) Scalar Irradiance Eo', fontweight='bold')
    ax.invert_yaxis()
    ax.grid(True, alpha=0.3, which='both')
    ax.legend(fontsize=7, ncol=2)
    
    # Irradiance reflectance R
    ax = axes[1, 1]
    for i, wl in enumerate(wavelengths):
        data = df[df['wavelength'] == wl]
        ax.plot(data['R'], data['z_m'], '-o', color=colors[i], 
                label=f'{int(wl)} nm', markersize=4)
    ax.set_xlabel('R = Eu/Ed', fontsize=10)
    ax.set_ylabel('Depth (m)', fontsize=10)
    ax.set_title('(d) Irradiance Reflectance R', fontweight='bold')
    ax.invert_yaxis()
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=7, ncol=2)
    
    plt.tight_layout()
    output_file = output_dir / 'Irradiances_vs_depth.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Saved: {output_file}")
    plt.close()


def plot_radiances(df, output_dir):
    """Radiances 플롯 생성"""
    if df.empty:
        print("No radiances data to plot")
        return
    
    print("\nPlotting Radiances...")
    wavelengths = sorted(df['wavelength'].unique())
    colors = plt.cm.jet(np.linspace(0, 1, len(wavelengths)))
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle('Spectral Radiances vs Depth', fontsize=14, fontweight='bold')
    
    # Upwelling radiance Lu
    ax = axes[0, 0]
    for i, wl in enumerate(wavelengths):
        data = df[df['wavelength'] == wl]
        ax.semilogx(data['Lu'], data['z'], '-o', color=colors[i], 
                    label=f'{int(wl)} nm', markersize=4)
    ax.set_xlabel('Lu [W/(m² sr nm)]', fontsize=10)
    ax.set_ylabel('Depth (m)', fontsize=10)
    ax.set_title('(a) Upwelling Radiance Lu', fontweight='bold')
    ax.invert_yaxis()
    ax.grid(True, alpha=0.3, which='both')
    ax.legend(fontsize=7, ncol=2)
    
    # Downwelling radiance Ld
    ax = axes[0, 1]
    for i, wl in enumerate(wavelengths):
        data = df[df['wavelength'] == wl]
        ax.semilogx(data['Ld'], data['z'], '-o', color=colors[i], 
                    label=f'{int(wl)} nm', markersize=4)
    ax.set_xlabel('Ld [W/(m² sr nm)]', fontsize=10)
    ax.set_ylabel('Depth (m)', fontsize=10)
    ax.set_title('(b) Downwelling Radiance Ld', fontweight='bold')
    ax.invert_yaxis()
    ax.grid(True, alpha=0.3, which='both')
    ax.legend(fontsize=7, ncol=2)
    
    # Lu/Ed ratio
    ax = axes[1, 0]
    for i, wl in enumerate(wavelengths):
        data = df[df['wavelength'] == wl]
        ax.semilogx(data['Lu_over_Ed'], data['z'], '-o', color=colors[i], 
                    label=f'{int(wl)} nm', markersize=4)
    ax.set_xlabel('Lu/Ed [1/sr]', fontsize=10)
    ax.set_ylabel('Depth (m)', fontsize=10)
    ax.set_title('(c) Radiance-Irradiance Ratio Lu/Ed', fontweight='bold')
    ax.invert_yaxis()
    ax.grid(True, alpha=0.3, which='both')
    ax.legend(fontsize=7, ncol=2)
    
    # Q factor
    ax = axes[1, 1]
    for i, wl in enumerate(wavelengths):
        data = df[df['wavelength'] == wl]
        ax.plot(data['Q'], data['z'], '-o', color=colors[i], 
                label=f'{int(wl)} nm', markersize=4)
    ax.set_xlabel('Q = Eu/Lu [sr]', fontsize=10)
    ax.set_ylabel('Depth (m)', fontsize=10)
    ax.set_title('(d) Q Factor (Eu/Lu)', fontweight='bold')
    ax.invert_yaxis()
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=7, ncol=2)
    
    plt.tight_layout()
    output_file = output_dir / 'Radiances_vs_depth.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Saved: {output_file}")
    plt.close()


def plot_kfunctions(df, output_dir):
    """K-functions 플롯 생성"""
    if df.empty:
        print("No K-functions data to plot")
        return
    
    print("\nPlotting K-functions...")
    wavelengths = sorted(df['wavelength'].unique())
    colors = plt.cm.jet(np.linspace(0, 1, len(wavelengths)))
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle('K-functions vs Depth', fontsize=14, fontweight='bold')
    
    # Kd
    ax = axes[0, 0]
    for i, wl in enumerate(wavelengths):
        data = df[df['wavelength'] == wl]
        ax.plot(data['Kd'], data['depth'], '-o', color=colors[i], 
                label=f'{int(wl)} nm', markersize=4)
    ax.set_xlabel('Kd (1/m)', fontsize=10)
    ax.set_ylabel('Depth (m)', fontsize=10)
    ax.set_title('(a) Diffuse Attenuation Kd', fontweight='bold')
    ax.invert_yaxis()
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=7, ncol=2)
    
    # Ku
    ax = axes[0, 1]
    for i, wl in enumerate(wavelengths):
        data = df[df['wavelength'] == wl]
        ax.plot(data['Ku'], data['depth'], '-o', color=colors[i], 
                label=f'{int(wl)} nm', markersize=4)
    ax.set_xlabel('Ku (1/m)', fontsize=10)
    ax.set_ylabel('Depth (m)', fontsize=10)
    ax.set_title('(b) Upwelling Attenuation Ku', fontweight='bold')
    ax.invert_yaxis()
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=7, ncol=2)
    
    # Ko
    ax = axes[1, 0]
    for i, wl in enumerate(wavelengths):
        data = df[df['wavelength'] == wl]
        ax.plot(data['Ko'], data['depth'], '-o', color=colors[i], 
                label=f'{int(wl)} nm', markersize=4)
    ax.set_xlabel('Ko (1/m)', fontsize=10)
    ax.set_ylabel('Depth (m)', fontsize=10)
    ax.set_title('(c) Scalar Irradiance Attenuation Ko', fontweight='bold')
    ax.invert_yaxis()
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=7, ncol=2)
    
    # KLu
    ax = axes[1, 1]
    for i, wl in enumerate(wavelengths):
        data = df[df['wavelength'] == wl]
        ax.plot(data['KLu'], data['depth'], '-o', color=colors[i], 
                label=f'{int(wl)} nm', markersize=4)
    ax.set_xlabel('KLu (1/m)', fontsize=10)
    ax.set_ylabel('Depth (m)', fontsize=10)
    ax.set_title('(d) Upwelling Radiance Attenuation KLu', fontweight='bold')
    ax.invert_yaxis()
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=7, ncol=2)
    
    plt.tight_layout()
    output_file = output_dir / 'Kfunctions_vs_depth.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Saved: {output_file}")
    plt.close()


def plot_R_vs_wavelength(df, output_dir):
    """Depth별 Irradiance Reflectance vs Wavelength 플롯"""
    if df.empty:
        print("No irradiances data to plot")
        return
    
    print("\nPlotting Irradiance Reflectance vs Wavelength...")
    depths = sorted(df['z_m'].unique())
    colors = plt.cm.viridis(np.linspace(0, 1, len(depths)))
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    for i, depth in enumerate(depths):
        data = df[df['z_m'] == depth].sort_values('wavelength')
        ax.plot(data['wavelength'], data['R'], '-o', color=colors[i], 
                linewidth=2, markersize=4, label=f'{depth:.1f} m')
    
    ax.set_xlabel('Wavelength (nm)', fontsize=12)
    ax.set_ylabel('Irradiance Reflectance R = Eu/Ed', fontsize=12)
    ax.set_title('Irradiance Reflectance vs Wavelength by Depth', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=9, title='Depth', ncol=2)
    
    plt.tight_layout()
    output_file = output_dir / 'R_vs_wavelength_by_depth.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Saved: {output_file}")
    plt.close()


def plot_Lu_vs_wavelength(df, output_dir):
    """Depth별 Upwelling Radiance vs Wavelength 플롯"""
    if df.empty:
        print("No radiances data to plot")
        return
    
    print("\nPlotting Upwelling Radiance vs Wavelength...")
    depths = sorted(df['z'].unique())
    colors = plt.cm.viridis(np.linspace(0, 1, len(depths)))
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    for i, depth in enumerate(depths):
        data = df[df['z'] == depth].sort_values('wavelength')
        ax.plot(data['wavelength'], data['Lu'], '-o', color=colors[i], 
                linewidth=2, markersize=4, label=f'{depth:.1f} m')
    
    ax.set_xlabel('Wavelength (nm)', fontsize=12)
    ax.set_ylabel('Upwelling Radiance Lu [W/(m² sr nm)]', fontsize=12)
    ax.set_title('Upwelling Radiance vs Wavelength by Depth', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=9, title='Depth', ncol=2)
    
    plt.tight_layout()
    output_file = output_dir / 'Lu_vs_wavelength_by_depth.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Saved: {output_file}")
    plt.close()


def plot_Ed_vs_wavelength(df, output_dir):
    """Depth별 Downward Irradiance vs Wavelength 플롯"""
    if df.empty:
        print("No irradiances data to plot")
        return
    
    print("\nPlotting Downward Irradiance vs Wavelength...")
    depths = sorted(df['z_m'].unique())
    colors = plt.cm.viridis(np.linspace(0, 1, len(depths)))
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    for i, depth in enumerate(depths):
        data = df[df['z_m'] == depth].sort_values('wavelength')
        ax.plot(data['wavelength'], data['Ed'], '-o', color=colors[i], 
                linewidth=2, markersize=4, label=f'{depth:.1f} m')
    
    ax.set_xlabel('Wavelength (nm)', fontsize=12)
    ax.set_ylabel('Downward Irradiance Ed [W/(m² nm)]', fontsize=12)
    ax.set_title('Downward Irradiance vs Wavelength by Depth', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=9, title='Depth', ncol=2)
    
    plt.tight_layout()
    output_file = output_dir / 'Ed_vs_wavelength_by_depth.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Saved: {output_file}")
    plt.close()


def plot_Lu_Ed_ratio_vs_wavelength(irradiances_df, radiances_df, output_dir):
    """Depth별 Lu/Ed 비율 vs Wavelength 플롯"""
    if irradiances_df.empty or radiances_df.empty:
        print("No data to plot Lu/Ed ratio")
        return
    
    print("\nPlotting Lu/Ed Ratio vs Wavelength...")
    
    # 두 데이터프레임을 병합 (depth 컬럼명이 다르므로 주의)
    # irradiances: z_m, radiances: z
    irr_subset = irradiances_df[['wavelength', 'z_m', 'Ed']].copy()
    rad_subset = radiances_df[['wavelength', 'z', 'Lu']].copy()
    
    # 컬럼명 통일
    irr_subset.rename(columns={'z_m': 'depth'}, inplace=True)
    rad_subset.rename(columns={'z': 'depth'}, inplace=True)
    
    # 병합
    merged = pd.merge(irr_subset, rad_subset, on=['wavelength', 'depth'], how='inner')
    
    # Lu/Ed 계산
    merged['Lu_Ed_ratio'] = merged['Lu'] / merged['Ed']
    
    # 플롯
    depths = sorted(merged['depth'].unique())
    colors = plt.cm.viridis(np.linspace(0, 1, len(depths)))
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    for i, depth in enumerate(depths):
        data = merged[merged['depth'] == depth].sort_values('wavelength')
        ax.plot(data['wavelength'], data['Lu_Ed_ratio'], '-o', color=colors[i], 
                linewidth=2, markersize=4, label=f'{depth:.1f} m')
    
    ax.set_xlabel('Wavelength (nm)', fontsize=12)
    ax.set_ylabel('Lu/Ed Ratio [sr⁻¹]', fontsize=12)
    ax.set_title('Lu/Ed Ratio vs Wavelength by Depth', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=9, title='Depth', ncol=2)
    
    plt.tight_layout()
    output_file = output_dir / 'Lu_Ed_ratio_vs_wavelength_by_depth.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Saved: {output_file}")
    plt.close()


def main():
    # 로그 파일 설정
    log_file = open('P03_execution.log', 'w', encoding='utf-8')
    
    def log_print(msg):
        print(msg)
        log_file.write(msg + '\n')
        log_file.flush()
    
    log_print("="*50)
    log_print("P03_parse_HL_results.py STARTED")
    log_print("="*50)
    
    # 파일 경로
    data_file = Path(r"C:\HE60\cursor\data\PExe05.txt")
    # 파일명에서 확장자를 제거하여 출력 폴더명 생성
    file_name = data_file.stem  # 'PExe01'
    output_dir = Path(r"C:\HE60\cursor\results\P03_parse_HL_results") / file_name
    
    log_print(f"\nData file: {data_file}")
    log_print(f"Output directory: {output_dir}")
    
    # 출력 디렉토리 생성
    output_dir.mkdir(parents=True, exist_ok=True)
    log_print("Output directory created")
    
    # 파일 파싱
    data = parse_hydrolight_file(data_file)
    
    # 플롯 생성
    print("\n" + "="*50)
    print("Creating plots...")
    print("="*50)
    
    plot_iops(data['iops'], output_dir)
    plot_irradiances(data['irradiances'], output_dir)
    plot_radiances(data['radiances'], output_dir)
    plot_kfunctions(data['kfunctions'], output_dir)
    
    # 추가 플롯: wavelength별 depth 비교
    plot_R_vs_wavelength(data['irradiances'], output_dir)
    plot_Lu_vs_wavelength(data['radiances'], output_dir)
    plot_Ed_vs_wavelength(data['irradiances'], output_dir)
    plot_Lu_Ed_ratio_vs_wavelength(data['irradiances'], data['radiances'], output_dir)
    
    print("\n" + "="*50)
    print("All plots completed!")
    print("="*50)
    print(f"\nResults saved in: {output_dir}")


if __name__ == "__main__":
    main()

