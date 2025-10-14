from __future__ import annotations

import sys
from dataclasses import dataclass


@dataclass
class ProgressBar:
    total: int
    prefix: str = ""

    def __post_init__(self) -> None:
        self.total = max(1, self.total)
        self._current = 0

    def advance(self, description: str = "") -> None:
        self._current = min(self.total, self._current + 1)
        self._render(description)

    def _render(self, description: str) -> None:
        fraction = self._current / self.total
        bar_width = 30
        filled = int(fraction * bar_width)
        bar = "#" * filled + "-" * (bar_width - filled)
        message = f"{self.prefix} [{bar}] {fraction * 100:6.2f}% {description}"
        sys.stdout.write(f"\r{message}")
        if self._current >= self.total:
            sys.stdout.write("\n")
        sys.stdout.flush()
