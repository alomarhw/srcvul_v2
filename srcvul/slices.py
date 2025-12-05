# srcvul/slices.py

from dataclasses import dataclass, field
from typing import List, Tuple


@dataclass
class SliceProfile:
    """
    Represents a single slice profile for a (file, function, variable).
    This is a simplified version aligned with the paper's notion of VR_slice.
    """
    file_path: str
    function: str
    variable: str
    def_lines: List[int] = field(default_factory=list)
    use_lines: List[int] = field(default_factory=list)
    dvars: List[str] = field(default_factory=list)
    ptrs: List[str] = field(default_factory=list)
    cfuncs: List[Tuple[str, int]] = field(default_factory=list)  # (func_name, count)

    @property
    def slice_lines(self) -> List[int]:
        """
        All line numbers involved in this slice (def + use).
        We can expand this later if we include more info.
        """
        return sorted(set(self.def_lines + self.use_lines))


def _parse_int_list(s: str) -> List[int]:
    """
    Parse something like 'def{697}' or 'use{714,716,717}' into a list of ints.
    Assumes format: name{comma-separated integers} or name{}.
    """
    if "{" not in s or "}" not in s:
        return []
    inside = s[s.find("{") + 1 : s.find("}")]
    inside = inside.strip()
    if not inside:
        return []
    return [int(x.strip()) for x in inside.split(",") if x.strip()]


def _parse_str_list(s: str) -> List[str]:
    """
    Parse something like 'dvars{a,b,c}' into a list of strings.
    """
    if "{" not in s or "}" not in s:
        return []
    inside = s[s.find("{") + 1 : s.find("}")]
    inside = inside.strip()
    if not inside:
        return []
    return [x.strip() for x in inside.split(",") if x.strip()]


def _parse_cfuncs(s: str) -> List[Tuple[str, int]]:
    """
    Parse something like 'cfuncs{list_add_tail{2},kfree{1}}'
    into [('list_add_tail', 2), ('kfree', 1)].
    This is a simple parser, we can refine it later if needed.
    """
    if "{" not in s or "}" not in s:
        return []
    inside = s[s.find("{") + 1 : s.rfind("}")]
    inside = inside.strip()
    if not inside:
        return []
    parts = [p.strip() for p in inside.split(",") if p.strip()]
    result: List[Tuple[str, int]] = []
    for p in parts:
        # expect something like 'list_add_tail{2}'
        if "{" in p and "}" in p:
            name = p[: p.find("{")].strip()
            count_str = p[p.find("{") + 1 : p.find("}")].strip()
            if count_str.isdigit():
                result.append((name, int(count_str)))
            else:
                result.append((name, 1))
        else:
            result.append((p, 1))
    return result


def parse_slice_profile_line(line: str) -> SliceProfile:
    """
    Parse a single line in a simple slice-profile text format:
    
    Example:
      Linux-5.0.10/sound/core/info.c,
      snd_info_create_entry,parent,
      def{697},use{714,716,717},
      dvars{},ptrs{},cfuncs{list_add_tail{2}}
    
    Commas separate the main fields; we assume:
      0: file_path
      1: function
      2: variable
      3: def{...}
      4: use{...}
      5: dvars{...}
      6: ptrs{...}
      7: cfuncs{...}
    """
    # Normalize whitespace and remove trailing newline
    line = line.strip()
    if not line or line.startswith("#"):
        raise ValueError("Empty or comment line")

    parts = [p.strip() for p in line.split(",")]
    if len(parts) < 3:
        raise ValueError(f"Not enough columns in slice profile line: {line}")

    file_path = parts[0]
    function = parts[1]
    variable = parts[2]

    def_lines: List[int] = []
    use_lines: List[int] = []
    dvars: List[str] = []
    ptrs: List[str] = []
    cfuncs: List[Tuple[str, int]] = []

    # The remaining parts may appear in any order; we detect by prefix.
    for p in parts[3:]:
        if p.startswith("def"):
            def_lines = _parse_int_list(p)
        elif p.startswith("use"):
            use_lines = _parse_int_list(p)
        elif p.startswith("dvars"):
            dvars = _parse_str_list(p)
        elif p.startswith("ptrs"):
            ptrs = _parse_str_list(p)
        elif p.startswith("cfuncs"):
            cfuncs = _parse_cfuncs(p)

    return SliceProfile(
        file_path=file_path,
        function=function,
        variable=variable,
        def_lines=def_lines,
        use_lines=use_lines,
        dvars=dvars,
        ptrs=ptrs,
        cfuncs=cfuncs,
    )


def parse_slice_profile_file(path: str) -> list[SliceProfile]:
    """
    Parse a file where each line is a slice profile in the above format.
    """
    profiles: list[SliceProfile] = []
    with open(path, "r", encoding="utf-8") as f:
        for lineno, raw_line in enumerate(f, start=1):
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            try:
                profiles.append(parse_slice_profile_line(line))
            except ValueError as e:
                # For now, just warn and skip malformed lines instead of crashing.
                print(f"[warn] skipping line {lineno}: {e}")
                continue
    return profiles

