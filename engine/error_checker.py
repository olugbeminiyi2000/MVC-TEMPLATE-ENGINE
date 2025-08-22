"""
Checks for errors in the matched objects (variables, conditions, loops).
"""
from typing import List, Tuple, Match
from engine_core.patterns import Patterns
from engine_core.exceptions import VariableError, ConditionError, LoopError

def check_pattern_errors(possible_patterns_match: List[Tuple[str, Match]], condition_blocks: List[Tuple[str, Match]], loop_blocks: List[Tuple[str, Match]]) -> None:
    """
    Checks for possible errors in the matched objects (variables, conditions, loops).
    Raises exceptions if errors are found.
    Args:
        possible_patterns_match (List[Tuple[str, Match]]): List of (match_group, match) tuples.
    """
    patterns: Patterns = Patterns()
    # Checking for possible error in the matched objects
    for match_group, match in possible_patterns_match:
        try:
            if match_group == "variables":
                actual_match = patterns.extract_actual_variables.search(match.group())
                if not actual_match:
                    raise VariableError("The placeholder {} from column {} to {} is not of python standard.".format(match.group(), match.span()[0], match.span()[1]))
                else:
                    pass
            elif match_group == "if_statement":
                if patterns.extract_actual_if_placeholders.search(match.group()):
                    condition_blocks.append((match.lastgroup, match))
                elif patterns.extract_actual_if_placeholders_with_logic.search(match.group()):
                    condition_blocks.append((match.lastgroup, match))
                else:
                    raise ConditionError("The IF BlockNode {} from column {} to {} is not written properly, here is the syntax {{% IF placholder %}}".format(match.group(), match.span()[0], match.span()[1]))
            elif match_group == "elif_statement":
                if patterns.extract_actual_elseif_placeholders.search(match.group()):
                    condition_blocks.append((match.lastgroup, match))
                elif patterns.extract_actual_elseif_placeholders_with_logic.search(match.group()):
                    condition_blocks.append((match.lastgroup, match))      
                else:
                    raise ConditionError("The ELIF BlockNode {} from column {} to {} is not written properly, here is the syntax {{% ELIF placholder %}}".format(match.group(), match.span()[0], match.span()[1]))
            elif match_group == "else_statement":
                actual_match = patterns.extract_actual_else_placeholders.search(match.group())
                if not actual_match:
                    raise ConditionError("The ELSE BlockNode {} from column {} to {} is not written properly, here is the syntax {{% ELSE %}}".format(match.group(), match.span()[0], match.span()[1]))
                else:
                    condition_blocks.append((match.lastgroup, match))   
            elif match_group == "endif_statement":
                actual_match = patterns.extract_actual_endif_placeholders.search(match.group())
                if not actual_match:
                    raise ConditionError("The ENDIF BlockNode {} from column {} to {} is not written properly, here is the syntax {{% ENDIF %}}".format(match.group(), match.span()[0], match.span()[1]))
                else:
                    condition_blocks.append((match.lastgroup, match))
            elif match_group == "for_loop_statement":
                actual_match = patterns.extract_actual_for_loop_placeholders.search(match.group())
                if not actual_match:
                    raise LoopError("The FOR BlockNode {} from column {} to {} is not written properly, here is the syntax {{% FOR variable IN iterable %}}".format(match.group(), match.span()[0], match.span()[1]))
                else:
                    loop_blocks.append((match.lastgroup, match))
            elif match_group == "endfor_loop_statement":
                actual_match = patterns.extract_actual_endfor_loop_placeholders.search(match.group())
                if not actual_match:
                    raise LoopError("The ENDFOR BlockNode {} from column {} to {} is not written properly, here is the syntax {{% ENDFOR %}}".format(match.group(), match.span()[0], match.span()[1]))
                else:
                    loop_blocks.append((match.lastgroup, match))
        except VariableError:
            raise
        except ConditionError:
            raise
        except LoopError:
            raise
