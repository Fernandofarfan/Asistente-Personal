
def check_indentation(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    for i, line in enumerate(lines):
        if line.strip():
            if '\t' in line:
                print(f"Line {i+1} contains tabs: {repr(line)}")
            if line.startswith(' ') and len(line) - len(line.lstrip()) % 4 != 0:
                 print(f"Line {i+1} has irregular indentation: {repr(line)}")

check_indentation('gui.py')
