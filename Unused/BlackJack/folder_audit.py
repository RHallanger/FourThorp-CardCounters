import os

# 1. Check where Python thinks it is
cwd = os.getcwd()
print(f"Python is running from: {cwd}")

# 2. Build the path to the templates folder
templates_path = os.path.join(cwd, "templates")

if not os.path.exists(templates_path):
    print("ERROR: Python cannot find a 'templates' folder here!")
else:
    print(f"Scanning folder: {templates_path}")
    print("-" * 30)
    
    # 3. List every single file Python sees
    files = os.listdir(templates_path)
    files.sort()
    
    for f in files:
        # We print the filename wrapped in quotes ' ' so we can see hidden spaces!
        print(f"Found file: '{f}'")

    print("-" * 30)
    
    # 4. Specifically test the problem file
    problem_file = os.path.join(templates_path, "template_2.png")
    if os.path.exists(problem_file):
        print(f"✅ System confirms 'template_2.png' exists at this path.")
    else:
        print(f"❌ System says 'template_2.png' DOES NOT exist here.")