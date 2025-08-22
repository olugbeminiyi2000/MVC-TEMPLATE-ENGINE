from typing import Any, Dict
from engine.error_checker import check_pattern_errors
from engine.file_loader import load_template_file
from engine.iterable_manager import run_iterable_manager
from engine.parser import parse_template_components
from engine.pattern_matcher import compile_and_match_patterns
from engine.renderer import render_output
from engine.structure_checker import check_condition_structure, check_loop_structure
from engine.validator import validate_placeholders


def run_template_engine(template_filename: str, context_data: Dict[str, Any]) -> str:
    template_content = load_template_file(template_filename)
    possible_patterns_match, condition_blocks, loop_blocks = compile_and_match_patterns(template_content)
    check_pattern_errors(possible_patterns_match, condition_blocks, loop_blocks)
    check_condition_structure(condition_blocks)
    check_loop_structure(loop_blocks)
    parsed_components = parse_template_components(template_content, possible_patterns_match)
    rendered_iter_variables, rendered_iterables, iterables_list, variable_pattern_list, condition_pattern_list, loop_pattern_list, parsed_components_len = validate_placeholders(parsed_components, context_data)
    run_iterable_manager(iterables_list, context_data, rendered_iterables)
    rendered_output = render_output(
        parsed_components=parsed_components,
        context_data=context_data,
        rendered_iter_variables=rendered_iter_variables,
        rendered_iterables=rendered_iterables,
        variable_pattern_list=variable_pattern_list,
        condition_pattern_list=condition_pattern_list,
        loop_pattern_list=loop_pattern_list,
        template_content=template_content,
        parsed_components_len=parsed_components_len
    )
    print(rendered_output)


context_data: Dict[str, Any] = {"A": True, "B": False, "C": True, "D": True, "E": True, "F": False, "G": False, "first_name": "Emmanuel", "last_name": "Obolo", "farms": [[], [4, 5, 6], [7, 8, 9]], "tomatoes": {"tomato1": 1, "tomato2": 2, "tomato3": 3}, "containers": (10, 11, 12), "labels": {100, "biscuits", "Orange"}}
run_template_engine("template.txt", context_data)