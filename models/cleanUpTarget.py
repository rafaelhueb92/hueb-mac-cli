from dataclasses import dataclass
from pathlib import Path


@dataclass
class CleanupTarget:
    name: str
    path: Path
    enabled: bool = True
