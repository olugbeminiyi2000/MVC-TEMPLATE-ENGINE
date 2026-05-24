"""
Adversarial stress test runner for the template engine.
Runs all scenarios and reports PASS / FAIL / CRASH for each.
"""
import sys
sys.path.insert(0, '.')

from engine.file_loader import load_template_file
from engine.pattern_matcher import compile_and_match_patterns
from engine.error_checker import check_pattern_errors
from engine.structure_checker import check_condition_structure, check_loop_structure
from engine.parser import parse_template_components
from engine.validator import validate_placeholders
from engine.iterable_manager import run_iterable_manager
from engine.renderer import render_output

PASS = "\033[32mPASS\033[0m"
FAIL = "\033[31mFAIL\033[0m"
CRASH = "\033[35mCRASH\033[0m"


def render(template_file, context_data):
    template_content = load_template_file(template_file)
    possible_patterns_match, condition_blocks, loop_blocks = compile_and_match_patterns(template_content)
    check_pattern_errors(possible_patterns_match, condition_blocks, loop_blocks)
    check_condition_structure(condition_blocks)
    check_loop_structure(loop_blocks)
    parsed_components = parse_template_components(template_content, possible_patterns_match)
    rendered_iter_variables, rendered_iterables, iterables_list, variable_pattern_list, condition_pattern_list, loop_pattern_list, parsed_components_len = validate_placeholders(parsed_components, context_data)
    run_iterable_manager(iterables_list, context_data, rendered_iterables)
    return render_output(
        parsed_components=parsed_components,
        context_data=context_data,
        rendered_iter_variables=rendered_iter_variables,
        rendered_iterables=rendered_iterables,
        variable_pattern_list=variable_pattern_list,
        condition_pattern_list=condition_pattern_list,
        loop_pattern_list=loop_pattern_list,
        template_content=template_content,
        parsed_components_len=parsed_components_len,
    )


context_safe = {
    "A": True,
    "B": False,
    "C": True,
    "D": False,
    "username": "Tester",
    "scores": [10, 0, 5],
    "phrase": "hi",
    "nested": [[], [1, 2]],
}

context_crash = {
    "empty_list": [],
}

checks = [
    ("TEST 1  Variable substitution",          lambda o: "Hello, Tester!" in o),
    ("TEST 2  Multiple ELIF chain",             lambda o: "C is true" in o and "WRONG" not in o),
    ("TEST 3  NOT + AND logic",                 lambda o: "(NOT B) AND A is true" in o),
    ("TEST 4  OR short-circuit",                lambda o: "B OR C is true" in o),
    ("TEST 5  NOT with truthy var",             lambda o: "NOT A is false, else runs" in o),
    ("TEST 6  Sequential FOR loops",            lambda o: o.count("score: 10") == 1 and o.count("score again: 10") == 1),
    ("TEST 7  FOR then IF at same level",       lambda o: "IF after loop fires" in o),
    ("TEST 8  Falsy item in loop condition",    lambda o: "nonzero: 10" in o and "zero found" in o and "nonzero: 5" in o),
    ("TEST 9  Nested loop / empty inner list",  lambda o: "empty group" in o and "num: 1" in o and "num: 2" in o),
    ("TEST 10 String iterable",                 lambda o: "char: h" in o and "char: i" in o),
    ("TEST 11 Deeply nested conditions",        lambda o: "A and C and NOT B" in o),
    ("TEST 12 ELIF after false ELIF",           lambda o: "A true after two false ELIFs" in o),
]


print("=" * 60)
print("STRESS TEST: stress_safe.txt")
print("=" * 60)
try:
    output = render("stress_safe.txt", context_safe)
    all_passed = True
    for label, check in checks:
        status = PASS if check(output) else FAIL
        if "\033[31m" in status:
            all_passed = False
        print(f"  {status}  {label}")
    print()
    if all_passed:
        print(f"  {PASS}  All 12 tests passed.")
    else:
        print(f"  {FAIL}  One or more tests failed.")
    print()
    print("--- Raw output (first 60 lines) ---")
    for i, line in enumerate(output.splitlines()):
        if i >= 60:
            print("  ... (truncated)")
            break
        print(f"  {repr(line)}")
except Exception as e:
    import traceback
    print(f"  {CRASH}  Unexpected crash during safe test: {type(e).__name__}: {e}")
    traceback.print_exc()


print()
print("=" * 60)
print("STRESS TEST: stress_crash.txt  (expected to CRASH)")
print("=" * 60)
try:
    output = render("stress_crash.txt", context_crash)
    print(f"  {FAIL}  Expected a crash but got output:")
    print(f"  {repr(output)}")
except KeyError as e:
    print(f"  {CRASH}  KeyError: {e}")
    print(f"  DIAGNOSIS: Empty top-level iterable (empty_list=[]) causes 'del for_endfor_pair[level]'")
    print(f"             in Branch-1 (pre-created iterables). The matching ENDFOR then tries")
    print(f"             for_endfor_pair[level][1] = ... but the key was already deleted.")
    print(f"  ROOT CAUSE: renderer.py line 94 always runs 'del for_endfor_pair[level]' even")
    print(f"              when enfor_index is None (ENDFOR not yet seen), leaving ENDFOR with")
    print(f"              no entry to update, crashing with KeyError.")
except Exception as e:
    import traceback
    print(f"  {CRASH}  {type(e).__name__}: {e}")
    traceback.print_exc()
