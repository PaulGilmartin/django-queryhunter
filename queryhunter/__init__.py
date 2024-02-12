from pathlib import Path

from .context_manager import queryhunter
from .reporting import QueryHunterReportingOptions


def default_base_dir(file) -> str:
    return str(Path(file).resolve().parent.parent)


