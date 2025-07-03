with open("template.txt", "r") as f:
    content = f.read()

index = 44  # Finds the first 'l'
line_number = content.count('\n', 0, index) + 1
column_number = index - content.rfind('\n', 0, index) - 1
print(index, line_number, column_number)


{"A": True, "B": False, "C": True, "D": True, "E": True, "F": False, "G": False}