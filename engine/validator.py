from typing import List, Match, Tuple, Union, Any, Dict, Pattern
from engine_core.iterable_linkedlist import IterableLinkedList
from engine_core.patterns import Patterns
from engine_core.exceptions import VariableError
from engine_core.placeholder_validation import all_placeholders_exist, variable_exists
import re

def validate_placeholders(parsed_components: List[Tuple[str, Union[Match[str], None]]], context_data: Dict[str, Any]) -> Tuple[Union[Dict[str, Any], Dict[str, List[IterableLinkedList]]], List[str], List[Pattern], int]:
    current_component: int = 0
    parsed_components_len: int = len(parsed_components)
    rendered_iter_variables: Dict[str, Any] = {}
    rendered_iterables: Dict[str, List[IterableLinkedList]] = {}
    iterables_list: List[str] = []

    patterns: Patterns = Patterns()
    while current_component <= parsed_components_len - 1:
        # TODO 1. Address conditions, loops, and placeholders
        """
        First: I have to check if the variables/placeholders in if and elseif condition
        per component exist and throw an error if it is not seen in the data needed to
        be rendered.
        Also do that for normal placeholders not in if or elseif conditions
        """
        condition_pattern_list: List[Pattern] = [re.compile(patterns.extract_possible_if_placeholders), re.compile(patterns.extract_possible_elseif_placeholders), re.compile(patterns.extract_possible_else_placeholders), re.compile(patterns.extract_possible_endif_placeholders)]
        variable_pattern_list: List[Pattern] = [patterns.extract_actual_variables, patterns.cleanup_actual_variables]
        loop_pattern_list: List[Pattern] = [patterns.extract_actual_for_loop_placeholders, patterns.extract_iter_variable, patterns.extract_iterable, patterns.extract_actual_endfor_loop_placeholders]

        try:
            if loop_pattern_list[0].search(parsed_components[current_component][0]):
                iter_variable_obj: Match[str] = loop_pattern_list[1].search(parsed_components[current_component][0])
                iterable_obj: Match[str] = loop_pattern_list[2].search(parsed_components[current_component][0])
                iter_variable_str = iter_variable_obj.group()
                iterable_str = iterable_obj.group()
                
                if iterable_str in context_data:
                    if iterable_str not in iterables_list:
                        iterables_list.append(iterable_str)
                elif iterable_str in rendered_iter_variables:
                    pass
                else:
                    raise VariableError("\x1b[1m\x1b[31mVariable\x1b[0m \x1b[35m{}\x1b[0m \x1b[31mis not found checked rendered data argument to verify\x1b[0m".format(iterable_str))
                rendered_iter_variables[iter_variable_str] = None
            if condition_pattern_list[0].search(parsed_components[current_component][0]):
                component_list: List[str] = patterns.extract_if_var_and_condition.findall(parsed_components[current_component][0])
                exist, result = all_placeholders_exist(context_data, component_list, rendered_iter_variables)
                if not exist:
                    raise VariableError("\x1b[1m\x1b[31mVariable\x1b[0m \x1b[35m{}\x1b[0m \x1b[31mis not found checked rendered data argument to verify\x1b[0m".format(result))
            elif condition_pattern_list[1].search(parsed_components[current_component][0]):
                component_list: List[str] = patterns.extract_elseif_var_and_condition.findall(parsed_components[current_component][0])
                exist, result = all_placeholders_exist(context_data, component_list, rendered_iter_variables)
                if not exist:
                    raise VariableError("\x1b[1m\x1b[31mVariable\x1b[0m \x1b[35m{}\x1b[0m \x1b[31mis not found checked rendered data argument to verify\x1b[0m".format(result))
            elif variable_pattern_list[0].search(parsed_components[current_component][0]):
                matched_var_obj: Match[str] = variable_pattern_list[0].search(parsed_components[current_component][0])
                cleaned_up_var_obj: Match[str] = variable_pattern_list[1].search(matched_var_obj.group())
                var_string: str = cleaned_up_var_obj.group()
                exist, result = variable_exists(context_data, rendered_iter_variables, var_string)
                if not exist:
                    raise VariableError("\x1b[1m\x1b[31mVariable\x1b[0m \x1b[35m{}\x1b[0m \x1b[31mis not found checked rendered data argument to verify\x1b[0m".format(result))
        except VariableError:
            raise
        else:
            current_component += 1

    return (rendered_iter_variables, rendered_iterables, iterables_list,variable_pattern_list, condition_pattern_list, loop_pattern_list, parsed_components_len)
