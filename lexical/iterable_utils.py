from __future__ import annotations
from typing import Dict, Any, Union, List, Tuple
from lexical.iterable_linkedlist import IterableLinkedList
from lexical.create_iterable_linkedlist import create_iterable_linked_list_chain


def validate_iterables(iterable: Union[List, str], map_data: Dict[str, Any], rendered_iterables: Dict[str, List[IterableLinkedList]]) -> None:
    # TODO 1
    # validate the type of the variables,
    # we don't have to re-validate the iterable each element if it is a list or re-validate it if it was a string,
    # because any of these variables would have been validated before sending to check variables.
    iterable_allowed_types: Tuple[Any] = (list, str)
    if not isinstance(iterable, iterable_allowed_types):
        raise TypeError(
            f"Iterable(s) must be one of types {iterable_allowed_types}, got {type(iterable).__name__}"
        )
    if not isinstance(map_data, Dict):
        raise TypeError(
            f"Data for the iterable(s) must be of type dict, got {type(map_data).__name__}"
        )
    if not isinstance(rendered_iterables, Dict):
        raise TypeError(
            f"the rendered variable holding a iterable linked list must be of type dict, got {type(rendered_iterables).__name__}"
        )
    
    python_allowed_iterables: Tuple[Any] = (list, tuple, set, dict, str)
    # TODO 2.
    # now validating the map_data based on the iterable type i.e str or list.
    # if it is a string.
    if isinstance(iterable, str):
        # check if the iterable string given is in map_data (render_iter_variables) to prevent error from me when building.
        if iterable not in map_data:
            raise KeyError(
                f"The iterable given {iterable} does not exist in map_data {map_data}"
            )
        # now check the type of the iterable value in the map_data
        iterable_value: Any = map_data.get(iterable)
        if not isinstance(iterable_value, python_allowed_iterables):
            raise TypeError(
                f"Iterable {iterable_value} value must be one of types {python_allowed_iterables}, got {type(iterable_value).__name__}"
            )
    # TODO 3.
    if isinstance(iterable, list):
        # Iterate through the iterable list variables,
        # then check if they exist in the map_data (rendered_output) and also,
        # it's value if it is an allowed python type.
        for iter in iterable:
            if iter not in map_data:
                raise KeyError(
                    f"The iterable given {iter} does not exist in map_data {map_data}"
                )
            # now check the type of the iterable value in the map_data.
            iterable_value: Any = map_data.get(iter)
            if not isinstance(iterable_value, python_allowed_iterables):
                raise TypeError(
                    f"Iterable {iterable_value} value must be one of types {python_allowed_iterables}, got {type(iterable_value).__name__}"
                )

    return None


def create_iterable_linked_list(iterable: Union[List, str], map_data: Dict[str, Any], rendered_iterables: Dict[str, List[IterableLinkedList]]) -> None:
    if isinstance(iterable, str):
        iterable_value = map_data.get(iterable)
        create_iterable_linked_list_chain(iterable, iterable_value, rendered_iterables)
    if isinstance(iterable, list):
        for iter in iterable:
            iterable_value = map_data.get(iter)
            create_iterable_linked_list_chain(iter, iterable_value, rendered_iterables)
    return None
