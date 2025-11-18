from __future__ import annotations

import logging
from pathlib import Path

from core import GraphData

from .context import ParserContext, read_text_with_fallback
from .sections import SECTION_PARSERS

logger = logging.getLogger(__name__)


class KnowledgeGraphParser:
    """High-level orchestrator that delegates to section-level parsers."""

    def __init__(self, readme_path: Path) -> None:
        self.readme_path = readme_path
        document = read_text_with_fallback(readme_path)
        self.context = ParserContext(
            source_path=readme_path,
            document=document,
            graph=GraphData(),
        )

    def parse(self) -> GraphData:
        for section_parser in SECTION_PARSERS:
            section_parser(self.context)
        logger.debug(
            "Parsed %d nodes and %d relationships from %s",
            len(self.context.graph.nodes),
            len(self.context.graph.relationships),
            self.readme_path,
        )
        return self.context.graph
