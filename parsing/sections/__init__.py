from __future__ import annotations

from .consistency_rules import parse_consistency_rules
from .data_flow import parse_data_flow_architecture
from .entity_relationships import parse_entity_relationships
from .error_data import parse_error_data_structure
from .form_to_vo import parse_form_to_vo_mapping
from .processing_patterns import parse_processing_patterns
from .session_management import parse_session_data_management
from .validation_rules import parse_validation_rules

SECTION_PARSERS = (
    parse_entity_relationships,
    parse_data_flow_architecture,
    parse_processing_patterns,
    parse_form_to_vo_mapping,
    parse_validation_rules,
    parse_session_data_management,
    parse_error_data_structure,
    parse_consistency_rules,
)

__all__ = [
    "SECTION_PARSERS",
    "parse_consistency_rules",
    "parse_data_flow_architecture",
    "parse_entity_relationships",
    "parse_error_data_structure",
    "parse_form_to_vo_mapping",
    "parse_processing_patterns",
    "parse_session_data_management",
    "parse_validation_rules",
]
