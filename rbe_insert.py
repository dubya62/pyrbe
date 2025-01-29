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

# runs the compiled program with 'perf stat' and collects metrics. 
# return the metrics as a tuple as integers. 
def run_perf_stat(output_file): 
    try: 
        result = subprocess.run( 
            ["perf", "stat", f"./{output_file}"],
            stderr=subprocess.PIPE,
            text=True
        )
        perf_output = result.stderr
        print("Perf output captured")
        
        # do metrics 
        metric1, metric2 = 20, 13 # dummy (haha me) values 
        return metric1, metric2 
    except Exception as e: 
        print(f"Failed to run with perf: {e}")
        sys.exit(1)   
    
# read the IR file to extracts tokens as a rule string.     
def read_ir_file(ir_file): 
    try: 
        with open(ir_file, "r") as f: 
            ir_tokens = f.read().strip()
        return ir_tokens 
    except Exception as e: 
        print(f"Error reading IR file: {e}")
        sys.exit(1)

# I don't what to do with this yet (救我呀 快救救我)
def insert_rule_into_database(rule_db, rule_name, metrics, insert_ine):
    with open(rule_db, 'a') as f:
        f.write(f'"{rule}":{metrics}\n')


# the main function haha get it "main" function (not sorry) to handle the process 
def main(c_source_file, ir_file, rule_database_file, insert_line, rule_name): 
    
    # compile the c source file 
    compile_c_source(c_source_file)
    
    # run the compiled file with perf stat to gather metrics 
    metrics = run_perf_stat("a.out")
    
    # insert the rule with the metrics into the rule database
    insert_rule_into_database(rule_database_file, rule_name, metrics, insert_line)
    
    print("Process completed")

# if __name__ == "main": 
#     if len(sys)