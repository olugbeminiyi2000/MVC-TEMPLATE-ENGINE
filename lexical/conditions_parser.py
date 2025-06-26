import re
import regex
from typing import List, Match, Pattern, Tuple, Dict, Any
from lexical.logic_condition import get_logic_chain, logicNode, orNode, andNode, notNode
from lexical.condition_helper_funcs import does_placeholder_exist
from lexical.condition_truthy_falsy import get_truthy_falsy_logic, get_truthy_falsy_no_logic

template_string = ""

# condition_string = """
# {{ valid_variable }}, {{ 123invalid }}, {{ another_valid_one }}, {{ special-char@ }}, {{ _leading_underscore }},
# {{ space in name }}, {{ camelCaseValid }}, {{ !invalid_start }}, {{ variable_with_numbers123 }}, {{ $invalid_char_in_variable }}, 

# {% IF valid_variable %}, {% IF123invalid %}, {% if another_valid_one %}, {% IF special-char@ %}, {% if _leading_underscore %}, 
# {% IF space in name %}, {% IFcamelCaseValid %}, {% IF !invalid_start %}, {% IF variable_with_numbers123 %}, {% IF $invalid_char_in_variable %},

# {% ELIF valid_variable %}, {%ELIF123invalid %}, {% elif another_valid_one %}, {% ELIF special-char@ %}, {% elif _leading_underscore %},
# {% ELIF space in name %}, {% ELIFcamelCaseValid %}, {% ELIF !invalid_start %}, {% ELIF variable_with_numbers123 %}, {% ELIF $invalid_char_in_variable %},

# {% ELSE %}, {% ELSE123invalid %}, {% else invalid_another_valid_one %}, {% ELSE special-char@ %}, {% else _leading_underscore %},
# {% ELSE space in name %}, {% ELSEcamelCaseValid %}, {% ELSE !invalid_start %}, {% ELSE invalid_as_variable_with_numbers123 %}, {% ELSE $invalid_char_in_variable %},

# {% ENDIF %}, {% ENDIF valid_variable %}, {% ENDIF123invalid %}, {% endif another_valid_one %}, {% ENDIF special-char@ %}, {% endif _leading_underscore %},
# {% ENDIF space in name %}, {% ENDIFcamelCaseValid %}, {% ENDIF !invalid_start %}, {% ENDIF variable_with_numbers123 %}, {% ENDIF $invalid_char_in_variable %},

# {% IF valid_variable AND variableB %}, {% IF valid_variable AND variableB OR variableC %}, {% IF valid_variable AND variableB NOT variableC %}, 
# {% IF valid_variable AND variableB AND (NOT variableC) %}, {% IF valid_variable OR another_valid_one %}, {% IF NOT valid_variable %},

# {% ELIF valid_variable AND variableB %}, {% ELIF valid_variable OR another_valid_one %}, {% ELIF NOT valid_variable %}, 
# {% ELIF valid_variable AND variableB NOT variableC %}, {% ELIF valid_variable AND variableB AND (NOT variableC) %}, 

# {% ELSE valid_variable %}, {% ELSE123invalid %}, {% ELSE special-char@ %}, {% ELSE_variable_not_valid %}, {% ELSE space in name %}, 

# { % ENDIF missing_percent_space %}, {%ENDIF no_space_between_ENDIF_and_placeholder % }, {% ENDIF-missing_space_between_ENDIF_and_placeholder %}, 
# {% ENDIF_invalid-char$ %}
# """

# condition_string = """
# {{ valid_variable }}, {{ another_valid_one }}, {{ camelCaseValid }}, {{ variable_with_numbers123 }}, {{ _leading_underscore }},
# {{ space_in_name }}, {{ uppercaseVARIABLE }}, {{ mixedCASE_example }}

# {% IF valid_variable %}, {% IF variable_with_numbers123 %}, {% IF camelCaseValid %}, {% IF another_valid_one %}, {% IF space_in_name %},
# {% IF uppercaseVARIABLE %}, {% IF mixedCASE_example %}

# {% ELIF valid_variable %}, {% ELIF variable_with_numbers123 %}, {% ELIF camelCaseValid %}, {% ELIF another_valid_one %}, {% ELIF space_in_name %},
# {% ELIF uppercaseVARIABLE %}, {% ELIF mixedCASE_example %}

# {% ELSE %}, {% ELSE %}, {% ELSE %}

# {% ENDIF %}, {% ENDIF %}, {% ENDIF %}
# """

# condition_string = """
# {% IF user_logged_in %}
#     Welcome, {{ username }}!
# {% ELSE %}
#     Please log in first.
# {% ELIF user_is_admin %}  # Incorrect: ELIF after ELSE
#     You have admin access.
# {% ENDIF %}

# {% IF user_is_member %}
#     Membership perks available.
#     {% ELIF user_is_guest %}
#         Limited access granted.
# {% ENDIF %}

# {% IF cart_has_items %}
#     You have items in your cart.
#     {% ELSE %}
#         Your cart is empty.
#     {% ENDIF %}  # Correct structure

# {% IF order_pending %}
#     Your order is being processed.
#     {% IF order_shipped %}  # Error: Nested IF without closing the first block properly
#         Your order is on the way.
#     {% ENDIF %}
# {% ELSE %}
#     No orders found.
# {% ENDIF %}

# {% IF discount_applied %}
#     Special discount applied!
# {% ELSE %}
#         Seasonal discount available!
# {% ENDIF %}
# """

condition_string = """
{% IF (X AND NOT Y) OR (Z AND (NOT W OR Q)) %}
Condition evaluated to TRUE
{% ENDIF %}
"""



class VariableError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message

class ConditionError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message

class StructureError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message

class Patterns:
    # patterns for (variable)
    extract_possible_variables = r"(?P<variables>{{\s*.*?\s*}})"
    extract_actual_variables = re.compile('{{[A-Za-z_]+[A-Za-z0-9_]*}}|{{\s*[A-Za-z_]+[A-Za-z0-9_]*\s*}}')
    cleanup_actual_variables = re.compile('[A-Za-z0-9_]+')

    # patterns for (if condition)
    extract_possible_if_placeholders = r"(?P<if_statement>{\s*%\s*IF\s*.*?\s*%\s*})"
    extract_actual_if_placeholders = re.compile('{%\s+IF\s+[A-Za-z_]+[A-Za-z0-9_]*\s+%}')
    extract_actual_if_placeholders_with_logic = re.compile("{%\s+IF\s+(?:NOT\s+)?([A-Za-z_]+[A-Za-z0-9_]*)((?:\s+(AND|OR|==)\s+)(?:([A-Za-z_]+[A-Za-z0-9_]*)|(?:\(*?\s*NOT\s+[A-Za-z_]+[A-Za-z0-9_]*\s*\)*?)))*\s+%}")

    # patterns for (else if condition)
    extract_possible_elseif_placeholders = r"(?P<elif_statement>{\s*%\s*ELIF\s*.*?\s*%\s*})"
    extract_actual_elseif_placeholders = re.compile('{%\s+ELIF\s+[A-Za-z_]+[A-Za-z0-9_]*\s+%}')
    extract_actual_elseif_placeholders_with_logic = re.compile("{%\s+ELIF\s+(?:NOT\s+)?([A-Za-z_]+[A-Za-z0-9_]*)((?:\s+(AND|OR|==)\s+)(?:([A-Za-z_]+[A-Za-z0-9_]*)|(?:\(*?\s*NOT\s+[A-Za-z_]+[A-Za-z0-9_]*\s*\)*?)))*\s+%}")

    # pattern for (else) condition
    extract_possible_else_placeholders = r"(?P<else_statement>{\s*%\s*ELSE\s*.*?\s*%\s*})"
    extract_actual_else_placeholders = re.compile('{%\s+ELSE\s+%}')

    # pattern for (end if) condition
    extract_possible_endif_placeholders = r"(?P<endif_statement>{\s*%\s*ENDIF\s*.*?\s*%\s*})"
    extract_actual_endif_placeholders = re.compile('{%\s+ENDIF\s+%}')

    # pattern for matching all variables and logical operators in if and elif
    extract_elseif_var_and_condition = regex.compile('(?:AND|OR|NOT)|(?<=ELIF\s+)[A-Za-z_]+[A-Za-z0-9_]*|(?<=AND\s+|OR\s+|NOT\s+)[A-Za-z_]+[A-Za-z0-9_]*')
    extract_if_var_and_condition = regex.compile('(?:AND|OR|NOT)|(?<=IF\s+)[A-Za-z_]+[A-Za-z0-9_]*|(?<=AND\s+|OR\s+|NOT\s+)[A-Za-z_]+[A-Za-z0-9_]*')


    

    def __init__(self):
        self.pattern_list = [Patterns.extract_possible_variables, Patterns.extract_possible_if_placeholders, Patterns.extract_possible_endif_placeholders, Patterns.extract_possible_elseif_placeholders, Patterns.extract_possible_else_placeholders]



patternObj: Patterns = Patterns()
total_possible_patterns: str = "|".join(patternObj.pattern_list)
compiled_possible_patterns: Pattern = re.compile(total_possible_patterns, flags=re.IGNORECASE)
possible_patterns_match: List[Tuple[str, Match]] = []
condition_blocks: List[Tuple[str, Match]] = []
conditions_possibilities: Dict[str, List[str]] = {"if_statement": ["if_statement", "elif_statement", "else_statement"], "elif_statement": ["elif_statement", "else_statement", "endif_statement"], "else_statement": ["endif_statement"], "endif_statement": ["if_statement"]}

# Checking for all form of possible match (variable and conditions for now)
for match in compiled_possible_patterns.finditer(condition_string):
    possible_patterns_match.append((match.lastgroup, match))


# Checking for possible error in the matched objects
for match_group, match in possible_patterns_match:
    try:
        if match_group == "variables":
            actual_match = patternObj.extract_actual_variables.search(match.group())
            if not actual_match:
                raise VariableError("The placeholder {} from column {} to {} is not of python standard.".format(match.group(), match.span()[0], match.span()[1]))
            else:
                print(actual_match.group())
        elif match_group == "if_statement":
            if patternObj.extract_actual_if_placeholders.search(match.group()):
                condition_blocks.append((match.lastgroup, match))
                print(match.group())
            elif patternObj.extract_actual_if_placeholders_with_logic.search(match.group()):
                condition_blocks.append((match.lastgroup, match))
                print(match.group())
            else:
                raise ConditionError("The IF BlockNode {} from column {} to {} is not written properly, here is the syntax {{% IF placholder %}}".format(match.group(), match.span()[0], match.span()[1]))
        elif match_group == "elif_statement":
            if patternObj.extract_actual_elseif_placeholders.search(match.group()):
                condition_blocks.append((match.lastgroup, match))
                print(match.group())
            elif patternObj.extract_actual_elseif_placeholders_with_logic.search(match.group()):
                condition_blocks.append((match.lastgroup, match))
                print(match.group())      
            else:
                raise ConditionError("The ELIF BlockNode {} from column {} to {} is not written properly, here is the syntax {{% ELIF placholder %}}".format(match.group(), match.span()[0], match.span()[1]))
        elif match_group == "else_statement":
            actual_match = patternObj.extract_actual_else_placeholders.search(match.group())
            if not actual_match:
                raise ConditionError("The ELSE BlockNode {} from column {} to {} is not written properly, here is the syntax {{% ELSE %}}".format(match.group(), match.span()[0], match.span()[1]))
            else:
                condition_blocks.append((match.lastgroup, match))
                print(actual_match.group())          
        elif match_group == "endif_statement":
            actual_match = patternObj.extract_actual_endif_placeholders.search(match.group())
            if not actual_match:
                raise ConditionError("The ENDIF BlockNode {} from column {} to {} is not written properly, here is the syntax {{% ENDIF %}}".format(match.group(), match.span()[0], match.span()[1]))
            else:
                condition_blocks.append((match.lastgroup, match))
                print(actual_match.group())
    except VariableError as e:
        print(e)
    except ConditionError as e:
        print(e)

# checking for structure error in conditions in a template string
condition_position: int = 0
condition_length: int = len(condition_blocks)
last_condition_position: int = condition_length - 1

while condition_position <= last_condition_position:
    try:
        current_condition_tuple = condition_blocks[condition_position]
        if condition_position == last_condition_position:
            if current_condition_tuple[0] != "endif_statement":
                raise StructureError("The block should be ended by an ENDIF statement and not {} from column {} to {}".format(current_condition_tuple[1].group(), current_condition_tuple[1].span()[0], current_condition_tuple[1].span()[1]))
        else:
            next_condition_tuple = condition_blocks[condition_position + 1]
            if next_condition_tuple[0] in conditions_possibilities[current_condition_tuple[0]]:
                condition_position += 1
            else:
                raise StructureError("The block(s) that comes after {} should be {} not {} {} from column {} to {}".format(current_condition_tuple[1].group(), conditions_possibilities[current_condition_tuple[0]], next_condition_tuple[0], next_condition_tuple[1].group(), next_condition_tuple[1].span()[0], next_condition_tuple[1].span()[1]))
    except StructureError as e:
        print(e)
        break

# using the possible pattern list, to sequentially order static, dynamic, and condition blocks if no error is thrown
static_text: str = ""
current_idx: int = 0
components: List[str] = []
possible_patterns_size: int = len(possible_patterns_match)
for char_idx in range(len(condition_string)):
    if current_idx < possible_patterns_size:
        match_obj = possible_patterns_match[current_idx][1]
        match_span = match_obj.span()
        start = match_span[0]
        end = match_span[1] - 1
    if char_idx >= start and char_idx <= end:
        if char_idx == match_span[1] - 1:
            components.append(static_text)
            components.append(match_obj.group())
            current_idx += 1
            static_text = ""
    else:
        static_text += condition_string[char_idx]
else:
    if static_text:
        components.append(static_text)
        static_text = ""


print(components, end="\n\n")

data_to_render: Dict[str, Any] = {"A": True, "B": False, "C": True, "D": True, "E": True, "F": False, "G": False}

for component in components:
    # TODO 1. Address conditions
    """
    First: I have to check if the variables/placeholders in if and elseif condition
    per component exist and throw an error if it is not seen in the data needed to
    be rendered.
    """
    condition_pattern_list: List[Pattern] = [re.compile(patternObj.extract_possible_if_placeholders), re.compile(patternObj.extract_possible_elseif_placeholders)]

    try:
        if condition_pattern_list[0].search(component):
            component_list: List[str] = patternObj.extract_if_var_and_condition.findall(component)
            exist, result = does_placeholder_exist(data_to_render, component_list)
            if not exist:
                raise VariableError("Varaible {} is not found checked rendered data argument to verify".format(result))
        elif condition_pattern_list[1].search(component):
            component_list: List[str] = patternObj.extract_elseif_var_and_condition.findall(component)
            exist, result = does_placeholder_exist(data_to_render, component_list)
            if not exist:
                raise VariableError("Varaible {} is not found checked rendered data argument to verify".format(result))
    except VariableError:
        raise

    """
    Second: After successfully checking the variables if they exist  in the rendered data,
    we have to check if logic exists or not and also find the condition statement is truthy or falsy inorder to append them to the component back.
    """
    # if condition_pattern_list[0].search(component):
    #     component_list = patternObj.extract_if_var_and_condition.findall(component)
    #     print(component_list)
    #     # return logic_node of type logicNode or None
    #     logic_node = get_logic_chain(component_list)
    #     if logic_node:
    #         boolean: bool = get_truthy_falsy_logic(logic_node, component_list, data_to_render)
    #     else:
    #         boolean: bool = get_truthy_falsy_no_logic(component_list, data_to_render)
    #     # NOTE always reset and clean up the (NOT, AND, OR, LOGIC) linkedlist(head, current) to None
    #     notNode.reset_not_head()
    #     andNode.reset_and_head()
    #     orNode.reset_or_head()
    #     logicNode.reset_logic_head()
    #     print(boolean)

    # elif condition_pattern_list[1].search(component):
    #     component_list = patternObj.extract_elseif_var_and_condition.findall(component)
    #     print(component_list)
    #     # return logic_node of type logicNode or None
    #     logic_node = get_logic_chain(component_list)
    #     if logic_node:
    #         boolean: bool = get_truthy_falsy_logic(logic_node, component_list, data_to_render)
    #     else:
    #         boolean: bool = get_truthy_falsy_no_logic(component_list, data_to_render)
    #     # NOTE always reset and clean up the (NOT, AND, OR, LOGIC) linkedlist(head, current) to None
    #     notNode.reset_not_head()
    #     andNode.reset_and_head()
    #     orNode.reset_or_head()
    #     logicNode.reset_logic_head()
    #     print(boolean)