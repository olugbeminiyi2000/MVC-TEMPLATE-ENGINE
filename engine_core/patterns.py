"""
Regex Patterns for Template Parsing

This file contains all regular expressions used to parse variable placeholders and logic blocks in template files.
"""

import re
import regex

class Patterns:
    """
    Holds all regex patterns for extracting variables and logic blocks from templates.
    - extract_possible_variables: Matches any variable placeholder (e.g., {{ variable }}).
    - extract_actual_variables: Matches valid variable names inside placeholders.
    - cleanup_actual_variables: Cleans up variable names for validation.
    - extract_possible_if_placeholders: Matches IF logic blocks.
    - extract_actual_if_placeholders: Matches valid IF blocks with a single variable.
    - extract_actual_if_placeholders_with_logic: Matches IF blocks with logic (AND, OR, NOT).
    - extract_possible_elseif_placeholders: Matches ELIF logic blocks.
    - extract_actual_elseif_placeholders: Matches valid ELIF blocks with a single variable.
    - extract_actual_elseif_placeholders_with_logic: Matches ELIF blocks with logic.
    - extract_possible_else_placeholders: Matches ELSE blocks.
    - extract_actual_else_placeholders: Matches valid ELSE blocks.
    - extract_possible_endif_placeholders: Matches ENDIF blocks.
    - extract_actual_endif_placeholders: Matches valid ENDIF blocks.
    - extract_elseif_var_and_condition: Extracts variables and logic operators from ELIF blocks.
    - extract_if_var_and_condition: Extracts variables and logic operators from IF blocks.
    """
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

    # pattern for matching for loop
    extract_possible_for_loop_placeholders = r"(?P<for_loop_statement>{\s*%\s*FOR\s*.*?\s*%\s*})"
    extract_actual_for_loop_placeholders = re.compile('{%\s+FOR\s+[A-Za-z_]+[A-Za-z0-9_]*\s+IN\s+[A-Za-z_]+[A-Za-z0-9_]*\s+%}')
    extract_iter_variable = regex.compile('[A-Za-z_]+[A-Za-z0-9_]*(?=\s+IN)')
    extract_iterable = regex.compile('(?<=IN\s+)[A-Za-z_]+[A-Za-z0-9_]*')

    # pattern for matching endfor loop
    extract_possible_endfor_loop_placeholders = r"(?P<endfor_loop_statement>{\s*%\s*ENDFOR\s*.*?\s*%\s*})"
    extract_actual_endfor_loop_placeholders = re.compile('{%\s+ENDFOR\s+%}')


    def __init__(self):
        self.pattern_sequence = [
            Patterns.extract_possible_variables,
            Patterns.extract_possible_if_placeholders,
            Patterns.extract_possible_endif_placeholders,
            Patterns.extract_possible_elseif_placeholders,
            Patterns.extract_possible_else_placeholders,
            Patterns.extract_possible_for_loop_placeholders,
            Patterns.extract_possible_endfor_loop_placeholders,
        ] 