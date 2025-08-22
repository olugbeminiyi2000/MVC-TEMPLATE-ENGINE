"""
Compiles regex patterns and matches them against the template content.
"""
import re
from typing import List, Tuple, Pattern, Match, Union
from engine_core.patterns import Patterns

def compile_and_match_patterns(template_content: str) -> Tuple[Union[List[Tuple[str, Match]], List[Tuple[str, Match]], List[Tuple[str, Match]]]]:
    """
    Compiles all possible patterns and finds all matches in the template content.
    Args:
        template_content (str): The template string.
    Returns:
        Tuple[Union[str, Pattern, List[Tuple[str, Match]], List[Tuple[str, Match]], List[Tuple[str, Match]]]]s.
    """
    patterns = Patterns()
    total_possible_patterns: str = "|".join(patterns.pattern_sequence)
    compiled_possible_patterns: Pattern = re.compile(total_possible_patterns, flags=re.IGNORECASE)
    possible_patterns_match: List[Tuple[str, Match]] = []
    condition_blocks: List[Tuple[str, Match]] = []
    loop_blocks: List[Tuple[str, Match]] = []

    # Checking for all form of possible match (variables, conditions, and loops for now)
    for match in compiled_possible_patterns.finditer(template_content):
        possible_patterns_match.append((match.lastgroup, match))

    return (possible_patterns_match, condition_blocks, loop_blocks)
