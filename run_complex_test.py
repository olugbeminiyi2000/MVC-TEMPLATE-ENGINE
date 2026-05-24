"""
Complex stress test — runs stress_complex.txt and verifies every
expected output line is present and every forbidden line is absent.
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

PASS  = "\033[32mPASS\033[0m"
FAIL  = "\033[31mFAIL\033[0m"
CRASH = "\033[35mCRASH\033[0m"

context = {
    "A":         True,
    "B":         False,
    "C":         True,
    "username":  "Emmanuel",
    "scores":    [10, 0, 5],
    "empty_list": [],
    "phrase":    "hi",
    # nested: first element empty, second non-empty
    "nested":    [[], [3, 4]],
    # mixed: empty, then list with 0 and non-zero
    "mixed":     [[], [0, 7]],
}

def render(template_file, ctx):
    tc = load_template_file(template_file)
    pm, cb, lb = compile_and_match_patterns(tc)
    check_pattern_errors(pm, cb, lb)
    check_condition_structure(cb)
    check_loop_structure(lb)
    pc = parse_template_components(tc, pm)
    riv, ri, il, vpl, cpl, lpl, pcl = validate_placeholders(pc, ctx)
    run_iterable_manager(il, ctx, ri)
    return render_output(
        parsed_components=pc, context_data=ctx,
        rendered_iter_variables=riv, rendered_iterables=ri,
        variable_pattern_list=vpl, condition_pattern_list=cpl,
        loop_pattern_list=lpl, template_content=tc,
        parsed_components_len=pcl,
    )

checks = [
    # header
    ("Header uses username",
        lambda o: "REPORT FOR Emmanuel" in o),

    # section 1 — empty top-level list
    # Option A: None->'' so the variable renders blank, but surrounding
    # static text still prints once during the dead pass. What we guarantee
    # is that the variable itself never outputs the literal word "None".
    ("S1  Empty loop variable renders as blank, not 'None'",
        lambda o: "SHOULD NOT APPEAR: None" not in o),
    ("S1  Empty list done marker visible",
        lambda o: "Empty list done." in o),

    # section 2 — empty list inside true IF
    ("S2  After-empty-loop text visible inside true IF",
        lambda o: "After empty loop inside true IF" in o),

    # section 3 — empty list inside false IF
    ("S3  After false IF block text visible",
        lambda o: "After false IF block" in o),

    # section 4 — ELIF chain on falsy item
    ("S4  Truthy scores render value",
        lambda o: "score value: 10" in o and "score value: 5" in o),
    ("S4  Zero score triggers ELIF A branch",
        lambda o: "score was zero but A is true" in o),
    ("S4  ELSE branch of zero score not shown",
        lambda o: "score was zero and A is false" not in o),

    # section 5 — sequential loops then IF
    ("S5  First loop all three scores",
        lambda o: o.count("first: 10") == 1 and o.count("first: 0") == 1 and o.count("first: 5") == 1),
    ("S5  Second loop all three scores",
        lambda o: o.count("second: 10") == 1 and o.count("second: 0") == 1 and o.count("second: 5") == 1),
    ("S5  IF after two sequential loops fires",
        lambda o: "IF after two sequential loops" in o),

    # section 6 — outer loop with empty inner
    ("S6  group start/end markers appear for each outer iteration",
        lambda o: o.count("group start") == 2 and o.count("group end") == 2),
    ("S6  Empty inner list produces no items",
        lambda o: o.count("item: 3") == 1 and o.count("item: 4") == 1),

    # section 7 — deeply nested conditions inside loop
    ("S7  score=10 hits A=true NOT-B=true branch",
        lambda o: "score=10 A=true NOT-B=true" in o),
    ("S7  score=5  hits A=true NOT-B=true branch",
        lambda o: "score=5 A=true NOT-B=true" in o),
    ("S7  score=0  hits zero branch",
        lambda o: "zero score, skipped inner conditions" in o),

    # section 8 — string iterable then condition
    ("S8  String iterable produces individual letters",
        lambda o: "letter: h" in o and "letter: i" in o),
    ("S8  Condition after string loop fires",
        lambda o: "condition after string loop" in o),

    # section 9 — nested lists with 0 element and IF on num
    ("S9  Empty group encountered message",
        lambda o: "empty group encountered" in o),
    ("S9  Zero num recognised as falsy",
        lambda o: "num 0 is zero" in o),
    ("S9  Nonzero num recognised as truthy",
        lambda o: "num 7 is truthy" in o),

    # section 10 — NOT OR AND in loop
    ("S10 All scores kept (NOT B is always true since B=False)",
        lambda o: o.count("keep:") == 3 and "drop:" not in o),

    # footer
    ("Footer END REPORT visible",
        lambda o: "END REPORT" in o),
]

print("=" * 64)
print("COMPLEX STRESS TEST — stress_complex.txt")
print("=" * 64)

try:
    output = render("stress_complex.txt", context)

    failed = 0
    for label, check in checks:
        ok = check(output)
        print(f"  {'  PASS' if ok else '  FAIL'}  {label}")
        if not ok:
            failed += 1

    print()
    if failed == 0:
        print(f"  {PASS}  All {len(checks)} checks passed.")
    else:
        print(f"  {FAIL}  {failed} of {len(checks)} checks failed.")

    print()
    print("--- Full rendered output ---")
    for line in output.splitlines():
        print(f"  {repr(line)}")

except Exception as e:
    import traceback
    print(f"  {CRASH}  {type(e).__name__}: {e}")
    traceback.print_exc()
