import re
import regex

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
        self.pattern_list = [
            Patterns.extract_possible_variables,
            Patterns.extract_possible_if_placeholders,
            Patterns.extract_possible_endif_placeholders,
            Patterns.extract_possible_elseif_placeholders,
            Patterns.extract_possible_else_placeholders
        ] 