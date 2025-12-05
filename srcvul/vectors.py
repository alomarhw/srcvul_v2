# srcvul/vectors.py

from dataclasses import dataclass
from typing import List

import numpy as np

from .slices import SliceProfile


@dataclass
class VSVect:
    """
    Vulnerability Slicing Vector (vsvector), simplified version.
    We follow the paper's idea: a small set of metrics capturing the slice.
    """
    file_path: str
    function: str
    variable: str

    sc: float   # slice count / module size
    scvg: float # coverage (slice size / module size)
    si: float   # identifier-based metric
    ss: float   # spatial metric (distance between first and last line / module size)

    def as_array(self) -> np.ndarray:
        return np.array([self.sc, self.scvg, self.si, self.ss], dtype=float)


def compute_vsvector(profile: SliceProfile, module_size: int) -> VSVect:
    """
    Compute a simple vsvector for a single SliceProfile.
    
    module_size: total number of lines in the 'module' (file / snippet),
                 including whitespace. For now we pass it explicitly.
    
    This is a simplified interpretation:
      - SC   = (# slice profiles for this vrslice) / module_size
               (here we assume one profile per vrslice, so SC = 1 / module_size)
      - SZ   = number of distinct lines in this slice (def ∪ use)
      - SCvg = SZ / module_size
      - SI   = (# unique identifiers across dvars ∪ ptrs ∪ cfuncs) / module_size
      - SS   = (max_line - min_line) / module_size
    """
    if module_size <= 0:
        raise ValueError("module_size must be positive")

    slice_lines = profile.slice_lines
    if not slice_lines:
        # Empty slice: everything zero.
        return VSVect(
            file_path=profile.file_path,
            function=profile.function,
            variable=profile.variable,
            sc=0.0,
            scvg=0.0,
            si=0.0,
            ss=0.0,
        )

    # 1) SC: assume one slice profile per vrslice for now.
    sc = 1.0 / module_size

    # 2) SZ: number of lines in the slice.
    sz = len(slice_lines)

    # 3) SCvg: coverage = SZ / module_size.
    scvg = sz / module_size

    # 4) SI: identifier-based metric
    identifiers = set(profile.dvars + profile.ptrs + [name for name, _ in profile.cfuncs])
    si = len(identifiers) / module_size

    # 5) SS: spatial metric = (max_line - min_line) / module_size.
    min_line = min(slice_lines)
    max_line = max(slice_lines)
    ss = (max_line - min_line) / module_size

    return VSVect(
        file_path=profile.file_path,
        function=profile.function,
        variable=profile.variable,
        sc=sc,
        scvg=scvg,
        si=si,
        ss=ss,
    )


def compute_vsvectors_for_file(profiles: List[SliceProfile], module_size: int) -> List[VSVect]:
    """
    Compute vsvectors for all slice profiles in a file (same module_size).
    """
    return [compute_vsvector(p, module_size) for p in profiles]
