from typing import Any, Dict, List
from engine_core.iterable_linkedlist import IterableLinkedList
from engine_core.iterable_utils import create_iterable_linked_list, validate_iterables


def run_iterable_manager(iterables_list: List[str], context_data: Dict[str, Any], rendered_iterables: Dict[str, List[IterableLinkedList]]) -> None:
    validate_iterables(iterables_list, context_data, rendered_iterables)
    create_iterable_linked_list(iterables_list, context_data, rendered_iterables)
