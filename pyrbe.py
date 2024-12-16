

class MatchResult:
    def __init__(self, clause:str, matched_token:list[list[str]], offset:int, length:int, variables:list[list[str]]):
        # the offset of the match, the number of matched tokens, and a list of the variable values
        self.clause = clause
        self.matched_tokens = matched_tokens
        self.offset = offset
        self.length = length
        self.variables = variables

    def __str__(self):
        return f"MatchResult:\nMatched clause: {self.clause}\nMatched Tokens: {self.matched_tokens}\nOffset: {self.offset}\nLength: {self.length}\nVariables: {self.variables}"

    def __repr__(self):
        return self.__str__()


class Rule:
    def __init__(self, clauses:list[str], condition:str):
        self.clauses = clauses
        self.condition = condition

        self.metrics = []
        self.parse_metrics()

        print("\nCOMPILING:")
        self.compiled = [self.compile_clause(x) for x in self.clauses]
        # if the condition is checkable, check it
        # if condition is true or not checkable, start matching


    def parse_metrics(self):
        for i in range(len(self.clauses)):
            curr = self.clauses[i]
            # get the part that is made up of metrics
            j = len(curr) - 1
            metrics = ""
            while j > 0:
                if curr[j] == '"':
                    break
                metrics = curr[j] + metrics
                j -= 1
            self.clauses[i] = self.clauses[i][:j+1]
            metrics = [x for x in metrics.split(":") if x != ""]
            self.metrics.append(metrics)


    def compile_clause(self, clause:str):
        # convert a clause into a much faster list of instructions
        # should be able to call this as a function
        # input a list of tokens -> where the match was found and the length of the match
        instructions = []
        clause = clause.strip('"').split(" ")
        store = []
        get = []
        min_repetitions = [1] * len(clause)
        max_repetitions = [1] * len(clause)
        print(clause)
        print(min_repetitions)
        print(max_repetitions)

        for x in clause:
            if "$" in x:
                pass
        
        pass


    def match(self, tokens:list[str]):
        # match a list of tokens against this rule
        # return the matched clause, which tokens were matched (as a list of lists), 
        # the offset of the match, the number of matched tokens, and a list of the variable values
        pass
        

    def __str__(self):
        return f"RULE: {' eq '.join(self.clauses)} if {self.condition if len(self.condition) else 'True'}"

    def __repr__(self):
        return self.__str__()



class RBE:
    def __init__(self):
        self.rules:list[Rule] = []

        self.file_data = self.read_from_file("test.rbe")
        print(self.file_data)
        rbe_string =  self.parse_rbe_string(self.file_data)
        self.rules = self.parse_rules(rbe_string)
        print("\nRULES:")
        [print(x) for x in self.rules]


    # should allow reading rules from a human readable file
    def read_from_file(self, filename:str) -> str:
        try:
            with open(filename, "r") as f:
                the_file = f.read()
        except:
            print(f"Could not open file ({the_file})")
            exit(0)

        return the_file


    def parse_rbe_string(self, data:str) -> list[Rule]:
        i = 0
        n = len(data)
        result = []

        backslashes = 0

        while i < n:
            curr = data[i]
            if data[i] == "\\":
                backslashes += 1

            if data[i] == '"' and backslashes % 2 == 0:
                # combine until "
                i += 1
                backslashes = 0
                while i < n:
                    curr += data[i]
                    if data[i] == '"' and backslashes % 2 == 0:
                        break
                    elif data[i] == "\\":
                        backslashes += 1
                    else:
                        backslashes = 0
                    i += 1
            elif data[i] == "#":
                # ignore until #
                i += 1
                while i < n:
                    if data[i] == "\n":
                        break
                    i += 1
                backslashes = 0
                continue

            if i < n and data[i] != "\\":
                backslashes = 0

            result.append(curr)
            i += 1

        # combine tokens between \n and spaces
        i = 0
        n = len(result)
        while i < n:
            while i + 1 < n and result[i] not in ["\n", " "] and result[i+1] not in ["\n", " "]:
                result[i] += result[i+1]
                del result[i+1]
                n -= 1
            i += 1

        # remove spaces
        result = [x for x in result if x != " "]

        print(f"RESULT: {result}")

        return result


    def parse_rules(self, tokens:list[str]) -> list[Rule]:
        """
        Rule types:
        "..." eq <\n> "..." <if> <condition> \n
        """
        i = 0
        n = len(tokens)

        result = []

        clauses = []
        condition = ""

        while i < n:
            if tokens[i] == "\n":
                if len(clauses) > 0:
                    result.append(Rule(clauses, condition))
                    clauses = []
                    condition = ""
            elif len(tokens[i]) > 0 and tokens[i][0] == '"':
                # this is a clause
                clauses.append(tokens[i])
            elif tokens[i] == "if":
                if i + 1 >= n:
                    print("ERROR: expected conditional after if")
                    exit(1)
                i += 1
                while i < n:
                    if tokens[i] == "\n":
                        break
                    condition += tokens[i]
                    i += 1
                continue
            elif tokens[i] == "eq":
                i += 1
                while i < n and tokens[i] == "\n":
                    i += 1
                if i >= n or len(tokens[i]) == 0 or tokens[i][0] != '"':
                    print("ERROR: expected clause after eq")
                    exit(1)
                continue

            i += 1

        return result


if __name__ == "__main__":
    rbe = RBE()

