# srcvul/db.py

from dataclasses import dataclass, asdict
from typing import List
import json

from .vectors import VSVect


@dataclass
class VulDBEntry:
    """
    A single entry in the vulnerability DB.

    For now we store:
      - vsvector (SC, SCvg, SI, SS)
      - some metadata to identify where it came from
      - a 'vuln_id' field (e.g., CVE ID or a simple label)
    """
    vuln_id: str
    file_path: str
    function: str
    variable: str

    sc: float
    scvg: float
    si: float
    ss: float

    patch: str = ""

    @classmethod
    def from_vsvect(cls, v: VSVect, vuln_id: str, patch: str = "") -> "VulDBEntry":
        return cls(
            vuln_id=vuln_id,
            file_path=v.file_path,
            function=v.function,
            variable=v.variable,
            sc=v.sc,
            scvg=v.scvg,
            si=v.si,
            ss=v.ss,
            patch=patch,
        )

    def to_vsvect(self) -> VSVect:
        from .vectors import VSVect  # avoid circular import at module import time
        return VSVect(
            file_path=self.file_path,
            function=self.function,
            variable=self.variable,
            sc=self.sc,
            scvg=self.scvg,
            si=self.si,
            ss=self.ss,
        )


def save_db(path: str, entries: List[VulDBEntry]) -> None:
    data = [asdict(e) for e in entries]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def load_db(path: str) -> List[VulDBEntry]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [VulDBEntry(**d) for d in data]

