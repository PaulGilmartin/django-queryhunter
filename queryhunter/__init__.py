from pathlib import Path

from .context_manager import queryhunter
from .reporting import QueryHunterReportingOptions


default_base_dir = lambda: str(Path(__file__).resolve().parent.parent)


