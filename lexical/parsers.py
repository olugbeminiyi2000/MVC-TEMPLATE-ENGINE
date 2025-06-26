import re

# text string
txt = "Hello, {{firstname}} {{       lastName       }}! {{middlename}}"

# Task 1
# patterns
extract_placeholders = re.compile('{{[A-Za-z_]+[A-Za-z0-9]*}}|{{\s*[A-Za-z_]+[A-Za-z0-9]*\s*}}')
cleanup_placeholders = re.compile('[A-Za-z0-9]+')

# Task 2
# list data structures
components, splits = [], []
static_text = ""
current_idx = 0

# extract placeholders
for match in extract_placeholders.finditer(txt):
    splits.append(match)

# static and dynamic text list in sequential order
splits_size = len(splits)
for char_idx in range(len(txt)):
    if current_idx < splits_size:
        match_obj = splits[current_idx]
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
        static_text += txt[char_idx]
else:
    if static_text:
        components.append(static_text)
        static_text = ""

# Task 3: Replacing Placeholders with Data
rendered_string = ""
render_data = { "firstname": "Alice", "lastName": "Smith", "middlename": "Green"}
for component in components:
    matched_result = extract_placeholders.search(component)
    try:
        if matched_result:
            placeholder = cleanup_placeholders.search(matched_result.group())
            rendered_string += render_data[placeholder.group()]
        else:
            rendered_string += component
    except KeyError as e:
        raise KeyError("Variable {0} not found".format(placeholder.group()))
    except Exception as e:
        raise
print(txt)
print(components)
print(rendered_string)