# You are given:
#     filename of C source code
#     filename IR of that C file (given from compiler)
#     filename of rule database
#     line number to insert on

# Compile the C source with gcc
# Run the Compiled program with perf stat to get metrics
# Insert the rules like this

# Existing Database file
# ```
# "else if":1:2 eq "else { if }":3:4
# ```

# After insert of "elif" on line 1 of that file with metrics 20 and 13
# ```
# "elif":20:13 eq "else if":1:2 eq "else { if }":3:4
# ```

import subprocess
import os 
import sys 

# compiles the c source file using gcc and outputs it to a.out
def compile_c_source(c_source_file, output_file="a.out"): 
    try: 
        subprocess.run(["gcc", c_source_file, "-o", output_file], check=True)
        print(f"Compiled {c_source_file} to {output_file}.")
    except: 
        print(f"Error compiling {c_source_file}.")
        sys.exit(1)


# I don't what to do with this yet (救我呀 快救救我)
def insert_rule(rule_db, rule, metrics):
    with open(rule_db, 'a') as f:
        f.write(f'"{rule}":{metrics}\n')

