import re
import pandas as pd
import numpy as np
from pathlib import Path

def section_indices(start_phrase, end_phrases, raw_lines):
    start = None
    for i, line in enumerate(raw_lines):
        if start_phrase in line:
            start = i
            break
    if start is None:
        return None, None
    end = len(raw_lines)
    for j in range(start+1, len(raw_lines)):
        if any(ep in raw_lines[j] for ep in end_phrases):
            end = j
            break
    return start, end

def parse_irradiances(raw_lines):
    start, end = section_indices("Spectral Irradiances [units of W/(m^2 nm)]", ["Selected Spectral Radiances", "Spectral Radiances Just Above"], raw_lines)
    if start is None:
        return pd.DataFrame()
    data_start = None
    for i in range(start, end):
        if "R = Eu/Ed" in raw_lines[i]:
            data_start = i + 1
            break
    if data_start is None:
        return pd.DataFrame()
    rows = []
    for line in raw_lines[data_start:end]:
        s = line.strip()
        if not s:
            break
        if s.startswith("in air"):
            continue
        nums = re.findall(r"[-+]?\d*\.\d+(?:[Ee][-+]?\d+)?|[-+]?\d+(?:\.\d+)?(?:[Ee][-+]?\d+)?", s)
        if len(nums) >= 12:
            vals = nums[-12:]
            rows.append([float(x) for x in vals])
    cols = ["iz","z_m","zeta","Eou","Eod","Eo","Eu","Ed","mubar_u","mubar_d","mubar","R"]
    return pd.DataFrame(rows, columns=cols)

def parse_iops(raw_lines):
    start, end = section_indices("Summary of Inherent Optical Properties", ["Linf, the shape", "Spectral Irradiances ["], raw_lines)
    if start is None:
        return pd.DataFrame()
    data_start = None
    for i in range(start, end):
        if "total bb/b" in raw_lines[i]:
            data_start = i + 1
            break
    if data_start is None:
        return pd.DataFrame()
    rows = []
    for line in raw_lines[data_start:end]:
        s = line.strip()
        if not s:
            break
        nums = re.findall(r"[-+]?\d*\.\d+(?:[Ee][-+]?\d+)?|[-+]?\d+(?:\.\d+)?(?:[Ee][-+]?\d+)?", s)
        if len(nums) >= 10:
            vals = nums[-10:]
            rows.append([float(x) for x in vals])
    cols = ["iz","Geo_Depth","Opt_Depth","total_a","total_b","total_c","albedo","total_bb","total_bb_over_b"]
    df = pd.DataFrame(rows, columns=cols[:len(rows[0])]) if rows else pd.DataFrame()
    if not df.empty and "Geo_Depth" in df.columns:
        return df[["iz","Geo_Depth","Opt_Depth","total_a","total_b","total_c","albedo","total_bb","total_bb_over_b"]]
    return df

def parse_selected_radiances(raw_lines):
    start, end = section_indices("Selected Spectral Radiances", ["Spectral Radiances Just Above", "K-functions"], raw_lines)
    if start is None:
        return pd.DataFrame()
    data_start = None
    for i in range(start, end):
        if "(theta,phi)" in raw_lines[i]:
            j = i+1
            while j < end and raw_lines[j].strip() == "":
                j += 1
            data_start = j
            break
    if data_start is None:
        return pd.DataFrame()
    rows = []
    for line in raw_lines[data_start:end]:
        s = line.strip()
        if not s:
            break
        if s.startswith("in air"):
            continue
        nums = re.findall(r"[-+]?\d*\.\d+(?:[Ee][-+]?\d+)?|[-+]?\d+(?:\.\d+)?(?:[Ee][-+]?\d+)?", s)
        if len(nums) >= 10:
            vals = nums[-10:]
            rows.append([float(x) for x in vals])
    cols = ["iz","z","zeta","Lu","Ld","Lh0","Lh90","Lh180","Lu_over_Ed","Q"]
    return pd.DataFrame(rows, columns=cols)

def parse_band_eo(raw_lines):
    start, end = section_indices("Band-integrated Eo as a function of depth", ["Band-integrated quantum", "PAR and broadband"], raw_lines)
    if start is None:
        return pd.DataFrame()
    wl = None
    for i in range(start, end):
        line = raw_lines[i].strip()
        if line.startswith("depth"):
            parts = line.split()
            wl = parts[-1] if len(parts) >= 2 else "band"
            data_start = i+1
            break
    else:
        return pd.DataFrame()
    rows = []
    for line in raw_lines[data_start:end]:
        s = line.strip()
        if not s or s.startswith("in air"):
            continue
        tokens = s.split()
        if len(tokens) >= 2:
            try:
                depth = float(tokens[0])
                val = float(tokens[1])
                rows.append((depth, val))
            except:
                pass
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows, columns=["depth_m", f"Eo_{wl}"])
