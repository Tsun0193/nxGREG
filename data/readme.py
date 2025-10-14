from __future__ import annotations

import os
from pathlib import Path
from typing import Optional, Tuple


DEFAULT_README_PATH = Path("ctc-data-translated/readme-en.md")
ENV_README_PATH = "CTC_README_PATH"


def resolve_readme_path(explicit_path: Optional[Path] = None) -> Tuple[Path, str]:
    """
    Determine which README/markdown file should be used.

    Preference order:
    1. Explicit path provided to the function (e.g. CLI argument).
    2. Path from the CTC_README_PATH environment variable.
    3. Default repository README at ctc-data-translated/readme-en.md.

    Returns:
        A tuple of (resolved_path, source_description).
    """
    if explicit_path:
        resolved = explicit_path.expanduser()
        return resolved, "explicit path"

    env_readme = os.getenv(ENV_README_PATH)
    if env_readme:
        resolved = Path(env_readme).expanduser()
        return resolved, f"{ENV_README_PATH} env var"

    return DEFAULT_README_PATH, "default path"
