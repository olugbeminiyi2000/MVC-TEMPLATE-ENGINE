from re import Match, Pattern
from typing import Any, Dict, List, Tuple, Union
from engine_core.condition_truthy_falsy import get_truthy_falsy_logic, get_truthy_falsy_no_logic
from engine_core.exceptions import PlacementError, VariableError
from engine_core.iterable_utils import create_iterable_linked_list, validate_iterables
from engine_core.logic_condition import get_logic_chain
from engine_core.logic_nodes import andNode, logicNode, notNode, orNode
from engine_core.patterns import Patterns


def render_output(**kwargs) -> List[Any]:
    """
    Renders the output for the template engine. Accepts all arguments as keyword arguments (kwargs) and extracts them inside the function.
    Expected kwargs keys:
        parsed_components, context_data, rendered_iter_variables, rendered_iterables,
        variable_pattern_list, condition_pattern_list, loop_pattern_list, template_content, parsed_components_len
    """
    parsed_components: List[Tuple[str, Union[Match[str], None]]] = kwargs["parsed_components"]
    context_data: Dict[str, Any] = kwargs["context_data"]
    rendered_iter_variables: Dict[str, Any] = kwargs["rendered_iter_variables"]
    rendered_iterables: Dict[str, Any] = kwargs["rendered_iterables"]
    variable_pattern_list: List[Pattern] = kwargs["variable_pattern_list"]
    condition_pattern_list: List[Pattern] = kwargs["condition_pattern_list"]
    loop_pattern_list: List[Pattern] = kwargs["loop_pattern_list"]
    template_content: str = kwargs["template_content"]
    parsed_components_len: int = kwargs["parsed_components_len"]
    indentation_rule = 4
    should_render: bool = True
    previous_indent_level: Union[int, None] = None
    indent_level_eval_map: Dict[int, Dict[str, bool]] = {}
    rendered_output_list: str = ""
    component_counter: int = 0
    if_block_depth: int = 0
    if_block_indent_level: Union[int, None] = None
    for_endfor_pair: Dict[int, List[int]] = {}
    state_before_loop_dict: Dict[int, Tuple[Union[bool, int]]] = {}


    patterns: Patterns = Patterns()
    while component_counter <= parsed_components_len - 1:
        """
        Second: After successfully checking the variables if they exist in the rendered data,
        we have to check if logic exists or not(for if and elif), then (else/endif) is always True and also find the condition statement is True or False
        then also we would be substituting variables and normal strings if they are
        allowed to be showed
        """
        if loop_pattern_list[0].search(parsed_components[component_counter][0]):
            # TODO 1: check indentation level of this node
            index = parsed_components[component_counter][1].span()[0]
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
                raise PlacementError("The FOR BlockNode {} is not correctly placed at column {}, line {}. It should be a multiple of {}".format(parsed_components[component_counter][1].group(), column_number + 1, line_number, indentation_rule))
            else:
                curr_indentation_level = column_number // indentation_rule

            # If no identation errors, for an identation level store the component counter (for node index)
            # leave a place holder for the enfor node index, and also the number of iterations for that for node
            # but the values of the iteration and storing depends if it is the first iteration or consistent ones
            if curr_indentation_level in for_endfor_pair:
                for_endfor_pair[curr_indentation_level][-1] = for_endfor_pair.get(curr_indentation_level)[-1] + 1
            else:
                for_endfor_pair[curr_indentation_level] = [component_counter, None, 1]
            
            # now let us extract iter_variable and the iterable
            iter_variable: str = loop_pattern_list[1].search(parsed_components[component_counter][0]).group()
            iterable: str = loop_pattern_list[2].search(parsed_components[component_counter][0]).group()
            
            # save should render state before commencing in this loop
            state_before_loop_dict[curr_indentation_level] = (should_render, curr_indentation_level)

            if iterable in rendered_iterables:
                # now check the current value of the iterable if it is None or a IterableLinkedList
                next_iteration = rendered_iterables[iterable][-1]
                # next_iteration is None
                if not next_iteration:
                    # assign the endfor-index + 1 to the component_counter using this for indentation level to find it in for_endfor_pair
                    # and also delete that current identation level to free it up and prevent errors down the template
                    enfor_index: Union[int, None] = for_endfor_pair[curr_indentation_level][1]
                    if not enfor_index:
                        component_counter += 1
                    else:
                        component_counter = for_endfor_pair[curr_indentation_level][1] + 1
                        del state_before_loop_dict[curr_indentation_level]

                    del for_endfor_pair[curr_indentation_level]
                    # set the traversal head node to the stagnant head node for reset
                    rendered_iterables[iterable][-1] = rendered_iterables[iterable][0]
                else:
                    current_iteration_data = rendered_iterables[iterable][-1].data
                    # store current_iteration data which is basically the value of our iter_variable, inside render_iter_variables
                    rendered_iter_variables[iter_variable] = current_iteration_data
                    # change the traversal head node to the next node or None
                    rendered_iterables[iterable][-1] = rendered_iterables[iterable][-1].next
                    component_counter += 1
                
                if iter_variable in rendered_iterables:
                    del rendered_iterables[iter_variable]

            else:
                if iterable in rendered_iter_variables:
                    # CREATE ITERABLES LINKEDLIST AND PUT VERY POWERFUL CHECKS
                    validate_iterables(iterable, rendered_iter_variables, rendered_iterables)
                    create_iterable_linked_list(iterable, rendered_iter_variables, rendered_iterables)
                    # now check the current value of the iterable if it is None or a IterableLinkedList
                    next_iteration = rendered_iterables[iterable][-1]
                    # next_iteration is None
                    if not next_iteration:
                        # assign the endfor-index + 1 to the component_counter using this for indentation level to find it in for_endfor_pair
                        # and also delete that current identation level to free it up and prevent errors down the template
                        enfor_index: Union[int, None] = for_endfor_pair[curr_indentation_level][1]
                        if not enfor_index:
                            component_counter += 1
                        else:
                            component_counter = for_endfor_pair[curr_indentation_level][1] + 1
                            del state_before_loop_dict[curr_indentation_level]                    
                            del for_endfor_pair[curr_indentation_level]
                            # set the traversal head node to the stagnant head node for reset
                            rendered_iterables[iterable][-1] = rendered_iterables[iterable][0]
                    else:
                        current_iteration_data = rendered_iterables[iterable][-1].data
                        # store current_iteration data which is basically the value of our iter_variable, inside render_iter_variables
                        rendered_iter_variables[iter_variable] = current_iteration_data
                        # change the traversal head node to the next node or None
                        rendered_iterables[iterable][-1] = rendered_iterables[iterable][-1].next
                        component_counter += 1

                else:
                    raise VariableError("Iterable {} is not found in either rerendered_iterables or rendered_iter_variables.".format(iterable))
                

        elif loop_pattern_list[3].search(parsed_components[component_counter][0]):
            # TODO 1: check indentation level of this node
            index = parsed_components[component_counter][1].span()[0]
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
                raise PlacementError("The ENDFOR BlockNode {} is not correctly placed at column {}, line {}. It should be a multiple of {}".format(parsed_components[component_counter][1].group(), column_number + 1, line_number, indentation_rule))
            else:
                curr_indentation_level = column_number // indentation_rule

            # save the index of the endfor i.e the component_counter in the for_endfor pair of that current indentation level
            # i.e as the second element of the list value of the for_endfor pair of that current indentation level
            for_endfor_pair[curr_indentation_level][1] = component_counter
            component_counter = for_endfor_pair[curr_indentation_level][0]

            should_render = state_before_loop_dict[curr_indentation_level][0]



        elif condition_pattern_list[0].search(parsed_components[component_counter][0]):
            component_list = patterns.extract_if_var_and_condition.findall(parsed_components[component_counter][0])
            # return logic_node of type logicNode or None
            logic_node = get_logic_chain(component_list)
            if logic_node:
                boolean: bool = get_truthy_falsy_logic(logic_node, component_list, context_data, rendered_iter_variables)
            else:
                boolean: bool = get_truthy_falsy_no_logic(component_list, context_data, rendered_iter_variables)
            # NOTE always reset and clean up the (NOT, AND, OR, LOGIC) linkedlist(head, current) to None
            notNode.reset_not_head()
            andNode.reset_and_head()
            orNode.reset_or_head()
            logicNode.reset_logic_head()

            # TODO 1: check indentation level of this node
            index = parsed_components[component_counter][1].span()[0]
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
                raise PlacementError("The IF BlockNode {} is not correctly placed at column {}, line {}. It should be a multiple of {}".format(parsed_components[component_counter][1].group(), column_number + 1, line_number, indentation_rule))
            else:
                curr_indentation_level = column_number // indentation_rule

            # TODO: set start_if for the first if and increase it by 1
            # to stop adding other if, and then assign the end_if to 
            # current_identation_level
            if if_block_depth == 0:
                if_block_depth += 1
                if_block_indent_level = curr_indentation_level

            if not should_render:
                # TODO 4: compare current identation level to the prev_identation_level
                """
                if current > prev (identation level):
                add empty string to the list
                if current < prev (identation level):
                perform the change show and level operation
                """
                if curr_indentation_level > previous_indent_level:
                    pass
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
                    if curr_indentation_level in indent_level_eval_map:
                        should_render = False
                        previous_indent_level = curr_indentation_level
                    else:
                        if boolean:
                            # saving curr
                            indent_level_eval_map[curr_indentation_level] = {"evaluated": True}
                            # assigning show and prev_indentation_level
                            should_render = True
                            previous_indent_level = curr_indentation_level
                        else:
                            # assigning show and prev_indentation_level7
                            should_render = False
                            previous_indent_level = curr_indentation_level

            else:
                # TODO 6: change show and prev(indentation level)
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
                if curr_indentation_level in indent_level_eval_map:
                    should_render = False
                    previous_indent_level = curr_indentation_level
                else:
                    if boolean:
                        # saving curr
                        indent_level_eval_map[curr_indentation_level] = {"evaluated": True}
                        # assigning show and prev_indentation_level
                        should_render = True
                        previous_indent_level = curr_indentation_level
                    else:
                        # assigning show and prev_indentation_level7
                        should_render = False
                        previous_indent_level = curr_indentation_level
            component_counter += 1

        elif condition_pattern_list[1].search(parsed_components[component_counter][0]):
            component_list = patterns.extract_elseif_var_and_condition.findall(parsed_components[component_counter][0])
            # return logic_node of type logicNode or None
            logic_node = get_logic_chain(component_list)
            if logic_node:
                boolean: bool = get_truthy_falsy_logic(logic_node, component_list, context_data, rendered_iter_variables)
            else:
                boolean: bool = get_truthy_falsy_no_logic(component_list, context_data, rendered_iter_variables)
            # NOTE always reset and clean up the (NOT, AND, OR, LOGIC) linkedlist(head, current) to None
            notNode.reset_not_head()
            andNode.reset_and_head()
            orNode.reset_or_head()
            logicNode.reset_logic_head()

            # TODO 1: check indentation level of this node
            index = parsed_components[component_counter][1].span()[0]
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
                raise PlacementError("The ELIF BlockNode {} is not correctly placed at column {}, line {}. It should be a multiple of {}".format(parsed_components[component_counter][1].group(), column_number, line_number, indentation_rule))
            else:
                curr_indentation_level = column_number // indentation_rule

            if not should_render:
                # TODO 4: compare current identation level to the prev_identation_level
                """
                if current > prev (identation level):
                add empty string to the list
                if current < prev (identation level):
                perform the change show and level operation
                """
                if curr_indentation_level > previous_indent_level:
                    pass
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
                    if curr_indentation_level in indent_level_eval_map:
                        should_render = False
                        previous_indent_level = curr_indentation_level
                    else:
                        if boolean:
                            # saving curr
                            indent_level_eval_map[curr_indentation_level] = {"evaluated": True}
                            # assigning show and prev_indentation_level
                            should_render = True
                            previous_indent_level = curr_indentation_level
                        else:
                            # assigning show and prev_indentation_level
                            should_render = False
                            previous_indent_level = curr_indentation_level

            else:
                # TODO 6: change show and prev(indentation level)
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
                if curr_indentation_level in indent_level_eval_map:
                    should_render = False
                    previous_indent_level = curr_indentation_level
                else:
                    if boolean:
                        # saving curr
                        indent_level_eval_map[curr_indentation_level] = {"evaluated": True}
                        # assigning show and prev_indentation_level
                        should_render = True
                        previous_indent_level = curr_indentation_level
                    else:
                        # assigning show and prev_indentation_level7
                        should_render = False
                        previous_indent_level = curr_indentation_level
            component_counter += 1

        elif condition_pattern_list[2].search(parsed_components[component_counter][0]):
            boolean: bool = True

            # TODO 1: check indentation level of this node
            index = parsed_components[component_counter][1].span()[0]
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
                raise PlacementError("The ELSE BlockNode {} is not correctly placed at column {}, line {}. It should be a multiple of {}".format(parsed_components[component_counter][1].group(), column_number, line_number, indentation_rule))
            else:
                curr_indentation_level = column_number // indentation_rule

            # TODO 3: check previous show for true or false
            if not should_render:
                # TODO 4: compare current identation level to the prev_identation_level
                """
                if current > prev (identation level):
                add empty string to the list
                if current < prev (identation level):
                perform the change show and level operation
                """
                if curr_indentation_level > previous_indent_level:
                    pass
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
                    if curr_indentation_level in indent_level_eval_map:
                        should_render = False
                        previous_indent_level = curr_indentation_level
                    else:
                        if boolean:
                            # saving curr
                            indent_level_eval_map[curr_indentation_level] = {"evaluated": True}
                            # assigning show and prev_indentation_level
                            should_render = True
                            previous_indent_level = curr_indentation_level
                        else:
                            # assigning show and prev_indentation_level7
                            should_render = False
                            previous_indent_level = curr_indentation_level
            else:
                # TODO 6: change show and prev(indentation level)
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
                if curr_indentation_level in indent_level_eval_map:
                    should_render = False
                    previous_indent_level = curr_indentation_level
                else:
                    if boolean:
                        # saving curr
                        indent_level_eval_map[curr_indentation_level] = {"evaluated": True}
                        # assigning show and prev_indentation_level
                        should_render = True
                        previous_indent_level = curr_indentation_level
                    else:
                        # assigning show and prev_indentation_level7
                        should_render = False
                        previous_indent_level = curr_indentation_level
            component_counter += 1

        elif condition_pattern_list[3].search(parsed_components[component_counter][0]):
            boolean: bool = True

            # TODO 1: check indentation level of this node
            index = parsed_components[component_counter][1].span()[0]
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
                raise PlacementError("The ENDIF BlockNode {} is not correctly placed at column {}, line {}. It should be a multiple of {}".format(parsed_components[component_counter][1].group(), column_number, line_number, indentation_rule))
            else:
                curr_indentation_level = column_number // indentation_rule

            # TODO 3: check previous show for true or false
            if not should_render:
                # TODO 4: compare current identation level to the prev_identation_level
                """
                if current > prev (identation level):
                add empty string to the list
                if current < prev (identation level):
                perform the change show and level operation
                """
                if curr_indentation_level > previous_indent_level:
                    pass
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
                    if curr_indentation_level in indent_level_eval_map:
                        should_render = False
                        previous_indent_level = curr_indentation_level
                    else:
                        if boolean:
                            # saving curr
                            indent_level_eval_map[curr_indentation_level] = {"evaluated": True}
                            # assigning show and prev_indentation_level
                            should_render = True
                            previous_indent_level = curr_indentation_level
                        else:
                            # assigning show and prev_indentation_level7
                            should_render = False
                            previous_indent_level = curr_indentation_level

            else:
                # TODO 6: change show and prev(indentation level)
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
                if curr_indentation_level in indent_level_eval_map:
                    should_render = False
                    previous_indent_level = curr_indentation_level
                else:
                    if boolean:
                        # saving curr
                        indent_level_eval_map[curr_indentation_level] = {"evaluated": True}
                        # assigning show and prev_indentation_level
                        should_render = True
                        previous_indent_level = curr_indentation_level
                    else:
                        # assigning show and prev_indentation_level7
                        should_render = False
                        previous_indent_level = curr_indentation_level

            # TODO 7 delete the identation level
            try:
                del indent_level_eval_map[curr_indentation_level]
            except KeyError:
                pass
            
            # TODO 7 check if the current endif indentation is the same as the
            # indentation in end_if.
            """
                if it is reset show to True, prev_identation_level to None,
                node_level_exist_dict to {}, start_if to 0 and end_if to None
            """
            if if_block_indent_level == curr_indentation_level:
                should_render = True
                previous_indent_level = None
                indent_level_eval_map = {}
                if_block_depth = 0
                if_block_indent_level = None
            component_counter += 1

        elif variable_pattern_list[0].search(parsed_components[component_counter][0]):
            matched_var_obj: Match[str] = variable_pattern_list[0].search(parsed_components[component_counter][0])
            cleaned_up_var_obj: Match[str] = variable_pattern_list[1].search(matched_var_obj.group())
            if should_render:
                try:
                    rendered_output_list += str(context_data[cleaned_up_var_obj.group()])
                except KeyError:
                    rendered_output_list += str(rendered_iter_variables[cleaned_up_var_obj.group()])
            component_counter += 1

        else:
            if should_render:
                if not isinstance(parsed_components[component_counter], Tuple):
                    rendered_output_list += str(parsed_components[component_counter])
                else:
                    rendered_output_list += str(parsed_components[component_counter][0])
            component_counter += 1
    
    return rendered_output_list
