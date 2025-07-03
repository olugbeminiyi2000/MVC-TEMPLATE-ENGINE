import os
import re
from typing import List, Match, Pattern, Tuple, Dict, Any, Union
from lexical.logic_nodes import logicNode, orNode, andNode, notNode
from lexical.logic_condition import get_logic_chain
from lexical.placeholder_validation import all_placeholders_exist, variable_exists
from lexical.condition_truthy_falsy import get_truthy_falsy_logic, get_truthy_falsy_no_logic
from lexical.patterns import Patterns
from lexical.exceptions import VariableError, ConditionError, StructureError, PlacementError


# EXTRACT details from files
base_path = os.path.dirname(__file__)
file_path = os.path.join(base_path, "template.txt")
with open(file_path, "r") as f:
    template_content = f.read()

patterns = Patterns()
total_possible_patterns: str = "|".join(patterns.pattern_list)
compiled_possible_patterns: Pattern = re.compile(total_possible_patterns, flags=re.IGNORECASE)
possible_patterns_match: List[Tuple[str, Match]] = []
condition_blocks: List[Tuple[str, Match]] = []


# Checking for all form of possible match (variable and conditions for now)
for match in compiled_possible_patterns.finditer(template_content):
    possible_patterns_match.append((match.lastgroup, match))


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
                pass
            elif patterns.extract_actual_if_placeholders_with_logic.search(match.group()):
                condition_blocks.append((match.lastgroup, match))
                pass
            else:
                raise ConditionError("The IF BlockNode {} from column {} to {} is not written properly, here is the syntax {{% IF placholder %}}".format(match.group(), match.span()[0], match.span()[1]))
        elif match_group == "elif_statement":
            if patterns.extract_actual_elseif_placeholders.search(match.group()):
                condition_blocks.append((match.lastgroup, match))
                pass
            elif patterns.extract_actual_elseif_placeholders_with_logic.search(match.group()):
                condition_blocks.append((match.lastgroup, match))
                pass      
            else:
                raise ConditionError("The ELIF BlockNode {} from column {} to {} is not written properly, here is the syntax {{% ELIF placholder %}}".format(match.group(), match.span()[0], match.span()[1]))
        elif match_group == "else_statement":
            actual_match = patterns.extract_actual_else_placeholders.search(match.group())
            if not actual_match:
                raise ConditionError("The ELSE BlockNode {} from column {} to {} is not written properly, here is the syntax {{% ELSE %}}".format(match.group(), match.span()[0], match.span()[1]))
            else:
                condition_blocks.append((match.lastgroup, match))
                pass          
        elif match_group == "endif_statement":
            actual_match = patterns.extract_actual_endif_placeholders.search(match.group())
            if not actual_match:
                raise ConditionError("The ENDIF BlockNode {} from column {} to {} is not written properly, here is the syntax {{% ENDIF %}}".format(match.group(), match.span()[0], match.span()[1]))
            else:
                condition_blocks.append((match.lastgroup, match))
                pass
    except VariableError:
        raise
    except ConditionError:
        raise

print(condition_blocks)
# checking for structure error in conditions in a template string
condition_position: int = 0
condition_length: int = len(condition_blocks)
last_condition_position: int = condition_length - 1
condition_start_dict: List[Tuple[str, Match]] = []
condition_start: int = 0
while condition_position <= last_condition_position:
    try:
        if condition_start == 0:
            initial_condition_tuple = condition_blocks[condition_position]
            if initial_condition_tuple[0] != "if_statement":
                raise StructureError("Block should start with {{% IF STATEMENT %}} not {}".format(initial_condition_tuple[1].group()))
            
        current_condition_tuple = condition_blocks[condition_position]
        if current_condition_tuple[0] == "if_statement":
            condition_start += 1
            condition_start_dict.append(current_condition_tuple)
        elif current_condition_tuple[0] == "endif_statement":
            condition_start -= 1
            del condition_start_dict[-1]
        
        condition_position += 1
    except StructureError:
        raise
else:
    try:
        if condition_start != 0:
            raise StructureError("Missing a {{% ENDIF %}} block for {} at {}".format(condition_start_dict[-1][1].group(), condition_blocks[-1][1].group()))
    except StructureError:
        raise


# TODO: arrange variables and conditions in a list
# using the possible pattern list, to sequentially order static, dynamic, and condition blocks if no error is thrown
static_text: str = ""
current_idx: int = 0
parsed_components: List[Tuple[str, Union[Match, None]]] = []
possible_patterns_size: int = len(possible_patterns_match)

for char_idx in range(len(template_content)):
    if current_idx < possible_patterns_size:
        match_obj = possible_patterns_match[current_idx][1]
        match_span = match_obj.span()
        start = match_span[0]
        end = match_span[1] - 1
    if char_idx >= start and char_idx <= end:
        if char_idx == match_span[1] - 1:
            parsed_components.append((static_text, ))
            parsed_components.append((match_obj.group(), match_obj))
            current_idx += 1
            static_text = ""
    else:
        static_text += template_content[char_idx]
else:
    if static_text:
        parsed_components.append(static_text)
        static_text = ""

print(end="\n\n")
print(parsed_components)
rendered_output: Dict[str, Any] = {"A": True, "B": False, "C": True, "D": True, "E": True, "F": False, "G": False, "first_name": "Emmanuel", "last_name": "Obolo"}

indentation_rule = 4
current_indent_level: Union[int, None] = None
previous_indent_level: Union[int, None] = None
indent_level_evaluated: Dict[int, Dict[str, bool]] = {}
render_component: List = []
count: int = 0
start_if: int = 0
end_if: Union[int, None] = None

for component in parsed_components:
    # TODO 1. Address conditions
    """
    First: I have to check if the variables/placeholders in if and elseif condition
    per component exist and throw an error if it is not seen in the data needed to
    be rendered.
    Also do that for normal placeholders not in if or elseif conditions
    """
    condition_pattern_list: List[Pattern] = [re.compile(patterns.extract_possible_if_placeholders), re.compile(patterns.extract_possible_elseif_placeholders), re.compile(patterns.extract_possible_else_placeholders), re.compile(patterns.extract_possible_endif_placeholders)]

    variable_pattern_list: List[Pattern] = [patterns.extract_actual_variables, patterns.cleanup_actual_variables]

    try:
        if condition_pattern_list[0].search(component[0]):
            component_list: List[str] = patterns.extract_if_var_and_condition.findall(component[0])
            exist, result = all_placeholders_exist(rendered_output, component_list)
            if not exist:
                raise VariableError("Varaible {} is not found checked rendered data argument to verify".format(result))
        elif condition_pattern_list[1].search(component[0]):
            component_list: List[str] = patterns.extract_elseif_var_and_condition.findall(component[0])
            exist, result = all_placeholders_exist(rendered_output, component_list)
            if not exist:
                raise VariableError("Varaible {} is not found checked rendered data argument to verify".format(result))
        elif variable_pattern_list[0].search(component[0]):
            matched_var_obj: Match[str] = variable_pattern_list[0].search(component[0])
            cleaned_up_var_obj: Match[str] = variable_pattern_list[1].search(matched_var_obj.group())
            var_string: str = cleaned_up_var_obj.group()
            exist, result = variable_exists(rendered_output, var_string)
            if not exist:
                raise VariableError("Varaible {} is not found checked rendered data argument to verify".format(result))         

        
        
    except VariableError:
        raise

    """
    Second: After successfully checking the variables if they exist in the rendered data,
    we have to check if logic exists or not(for if and elif), then (else/endif) is always True and also find the condition statement is True or False
    then also we would be substituting variables and normal strings if they are
    allowed to be showed
    """
    if condition_pattern_list[0].search(component[0]):
        component_list = patterns.extract_if_var_and_condition.findall(component[0])
        # return logic_node of type logicNode or None
        logic_node = get_logic_chain(component_list)
        if logic_node:
            boolean: bool = get_truthy_falsy_logic(logic_node, component_list, rendered_output)
        else:
            boolean: bool = get_truthy_falsy_no_logic(component_list, rendered_output)
        # NOTE always reset and clean up the (NOT, AND, OR, LOGIC) linkedlist(head, current) to None
        notNode.reset_not_head()
        andNode.reset_and_head()
        orNode.reset_or_head()
        logicNode.reset_logic_head()

        # TODO 1: check indentation level of this node
        index = component[1].span()[0]
        line_number = template_content.count('\n', 0, index) + 1
        column_number = index - template_content.rfind('\n', 0, index) - 1
        # TODO 2: check if column number remainder is Zero
        """
        If zero: it means it is correctly placed.
        if not zero: it means it is incorrectly placed throw an error,
        using the component[1].group(), column_number, line_number, and identation
        rule.
        """
        check_placement = column_number % indentation_rule
        if check_placement != 0:
            raise PlacementError("The IF BlockNode {} is not correctly placed at column {}, line {}. It should be a multiple of {}".format(component[1].group(), column_number + 1, line_number, indentation_rule))
        else:
            curr_indentation_level = column_number // indentation_rule

        # TODO: set start_if for the first if and increase it by 1
        # to stop adding other if, and then assign the end_if to 
        # current_identation_level
        if start_if == 0:
            start_if += 1
            end_if = curr_indentation_level

        # TODO 3: check previous show for true or false
        if current_indent_level is None or current_indent_level < curr_indentation_level:
            current_indent_level = curr_indentation_level
        else:
            # TODO 5: change show and prev(indentation level)
            """
            if curr (indentation level) exist in node_level_exist_dict set show to false
            if curr doesn't exist:
                get the evaluated boolean
                if evaluated boolean is true: save the curr so that the node level exits in
                node_level_exist_dict as {curr: {"evaluated": True}}, then set show to True and
                prev (indentation level) to curr (indentation level)
                if evaluated boolean is false: do not save
                then set show to False and prev to curr.
            """
            if curr_indentation_level in indent_level_evaluated:
                current_indent_level = None
            elif boolean:
                # saving curr
                indent_level_evaluated[curr_indentation_level] = {"evaluated": True}
                # assigning show and prev_indentation_level
                current_indent_level = curr_indentation_level

    elif condition_pattern_list[1].search(component[0]):
        component_list = patterns.extract_elseif_var_and_condition.findall(component[0])
        # return logic_node of type logicNode or None
        logic_node = get_logic_chain(component_list)
        if logic_node:
            boolean: bool = get_truthy_falsy_logic(logic_node, component_list, rendered_output)
        else:
            boolean: bool = get_truthy_falsy_no_logic(component_list, rendered_output)
        # NOTE always reset and clean up the (NOT, AND, OR, LOGIC) linkedlist(head, current) to None
        notNode.reset_not_head()
        andNode.reset_and_head()
        orNode.reset_or_head()
        logicNode.reset_logic_head()

        # TODO 1: check indentation level of this node
        index = component[1].span()[0]
        line_number = template_content.count('\n', 0, index) + 1
        column_number = index - template_content.rfind('\n', 0, index) - 1
        # TODO 2: check if column number remainder is Zero
        """
        If zero: it means it is correctly placed.
        if not zero: it means it is incorrectly placed throw an error,
        using the component[1].group(), column_number, line_number, and identation
        rule.
        """
        check_placement = column_number % indentation_rule
        if check_placement != 0:
            raise PlacementError("The IF BlockNode {} is not correctly placed at column {}, line {}. It should be a multiple of {}".format(component[1].group(), column_number, line_number, indentation_rule))
        else:
            curr_indentation_level = column_number // indentation_rule

        # TODO 3: check previous show for true or false
        if current_indent_level is None or current_indent_level < curr_indentation_level:
            current_indent_level = curr_indentation_level
        else:
            # TODO 5: change show and prev(indentation level)
            """
            if curr (indentation level) exist in node_level_exist_dict set show to false
            if curr doesn't exist:
                get the evaluated boolean
                if evaluated boolean is true: save the curr so that the node level exits in
                node_level_exist_dict as {curr: {"evaluated": True}}, then set show to True and
                prev (indentation level) to curr (indentation level)
                if evaluated boolean is false: do not save
                then set show to False and prev to curr.
            """
            if curr_indentation_level in indent_level_evaluated:
                current_indent_level = None
            elif boolean:
                # saving curr
                indent_level_evaluated[curr_indentation_level] = {"evaluated": True}
                # assigning show and prev_indentation_level
                current_indent_level = curr_indentation_level

    elif condition_pattern_list[2].search(component[0]):
        boolean: bool = True

        # TODO 1: check indentation level of this node
        index = component[1].span()[0]
        line_number = template_content.count('\n', 0, index) + 1
        column_number = index - template_content.rfind('\n', 0, index) - 1
        # TODO 2: check if column number remainder is Zero
        """
        If zero: it means it is correctly placed.
        if not zero: it means it is incorrectly placed throw an error,
        using the component[1].group(), column_number, line_number, and identation
        rule.
        """
        check_placement = column_number % indentation_rule
        if check_placement != 0:
            raise PlacementError("The IF BlockNode {} is not correctly placed at column {}, line {}. It should be a multiple of {}".format(component[1].group(), column_number, line_number, indentation_rule))
        else:
            curr_indentation_level = column_number // indentation_rule

        # TODO 3: check previous show for true or false
        if current_indent_level is None or current_indent_level < curr_indentation_level:
            current_indent_level = curr_indentation_level
        else:
            # TODO 5: change show and prev(indentation level)
            """
            if curr (indentation level) exist in node_level_exist_dict set show to false
            if curr doesn't exist:
                get the evaluated boolean
                if evaluated boolean is true: save the curr so that the node level exits in
                node_level_exist_dict as {curr: {"evaluated": True}}, then set show to True and
                prev (indentation level) to curr (indentation level)
                if evaluated boolean is false: do not save
                then set show to False and prev to curr.
            """
            if curr_indentation_level in indent_level_evaluated:
                current_indent_level = None
            elif boolean:
                # saving curr
                indent_level_evaluated[curr_indentation_level] = {"evaluated": True}
                # assigning show and prev_indentation_level
                current_indent_level = curr_indentation_level

    elif condition_pattern_list[3].search(component[0]):
        boolean: bool = True

        # TODO 1: check indentation level of this node
        index = component[1].span()[0]
        line_number = template_content.count('\n', 0, index) + 1
        column_number = index - template_content.rfind('\n', 0, index) - 1
        # TODO 2: check if column number remainder is Zero
        """
        If zero: it means it is correctly placed.
        if not zero: it means it is incorrectly placed throw an error,
        using the component[1].group(), column_number, line_number, and identation
        rule.
        """
        check_placement = column_number % indentation_rule
        if check_placement != 0:
            raise PlacementError("The IF BlockNode {} is not correctly placed at column {}, line {}. It should be a multiple of {}".format(component[1].group(), column_number, line_number, indentation_rule))
        else:
            curr_indentation_level = column_number // indentation_rule


        # TODO 3: check previous show for true or false
        if current_indent_level is None or current_indent_level < curr_indentation_level:
            current_indent_level = curr_indentation_level
        else:
            # TODO 5: change show and prev(indentation level)
            """
            if curr (indentation level) exist in node_level_exist_dict set show to false
            if curr doesn't exist:
                get the evaluated boolean
                if evaluated boolean is true: save the curr so that the node level exits in
                node_level_exist_dict as {curr: {"evaluated": True}}, then set show to True and
                prev (indentation level) to curr (indentation level)
                if evaluated boolean is false: do not save
                then set show to False and prev to curr.
            """
            if curr_indentation_level in indent_level_evaluated:
                current_indent_level = None
            elif boolean:
                # saving curr
                indent_level_evaluated[curr_indentation_level] = {"evaluated": True}
                # assigning show and prev_indentation_level
                current_indent_level = curr_indentation_level
        
        # TODO check if the current endif indentation is the same as the
        # indentation in end_if.
        """
            if it is reset show to True, prev_identation_level to None,
            node_level_exist_dict to {}, start_if to 0 and end_if to None
        """
        if end_if == curr_indentation_level:
            current_indent_level = None
            indent_level_evaluated = {}
            start_if = 0
            end_if = None

    elif variable_pattern_list[0].search(component[0]):
        matched_var_obj: Match[str] = variable_pattern_list[0].search(component[0])
        cleaned_up_var_obj: Match[str] = variable_pattern_list[1].search(matched_var_obj.group())
        if current_indent_level is not None:
            render_component.append(rendered_output[cleaned_up_var_obj.group()])

    else:
        if current_indent_level is not None:
            if not isinstance(component, Tuple):
                render_component.append(component)
            else:
                render_component.append(component[0])
    count += 1

print(current_indent_level, start_if, end_if, indent_level_evaluated)
print("\n")
print(render_component)