from __future__ import annotations
from typing import Dict, Any, Union, List, Tuple, Set
from engine_core.iterable_linkedlist import IterableLinkedList


def create_iterable_linked_list_chain(iterable: str, iterable_value: Union[List, Tuple, str, Dict, Set], rendered_iterables: Dict[str, Tuple[IterableLinkedList]]):
    for iter_value in iterable_value:
        iter_node: IterableLinkedList = IterableLinkedList(iter_value)
        IterableLinkedList.add_new_iterable_node(iter_node)

    # print the iterable chain formed for debugging purposes
    IterableLinkedList.display_iterable_chain()
    
    # Add that iterable variable to rendered_iterables
    iterable_head_node = IterableLinkedList.get_iterable_head()
    rendered_iterables[iterable] = [iterable_head_node, iterable_head_node] # first element for stagnant head node,  second element for traversing head node

    # Reset the iterable class head(head, current) after the creation of an iterable linked list
    IterableLinkedList.reset_iterable_head()