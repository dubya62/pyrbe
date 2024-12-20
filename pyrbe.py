

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


class MatchRule:
    def __init__(self, clause:list[str], min_reps:list[int], max_reps:list[int], matchers:list[object], match_openers:list[bool], match_closers:list[bool], store:list[int], get:list[list[int]]):
        self.clause = clause
        self.min_repetitions = min_reps
        self.max_repetitions = max_reps
        self.matchers = matchers
        self.match_openers = match_openers
        self.match_closers = match_closers
        self.store = store
        self.get = get


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
        clause = clause.strip('"').split(" ")
        store = []
        get = []
        matchers = [None] * len(clause) # list of functions that return True or false depending on if a token matches it
        min_repetitions = [1] * len(clause)
        max_repetitions = [1] * len(clause)
        match_openers = [False] * len(clause)
        match_closers = [False] * len(clause)

        def ANY(token:str):
            return True

        def create_contains_fun(token_list:list[str]):
            return lambda tok: tok in token_list

        current_token = 0
        for x in clause:
            backslashes = 0
            match_token = ""
            match_tokens = []
            the_fun = None
            for y in range(len(x)):
                if x[y] == "\\":
                    backslashes += 1
                elif x[y] == ".":
                    if backslashes % 2 == 0:
                        the_fun = ANY
                        backslashes = 0
                        continue
                elif x[y] == "*":
                    if backslashes % 2 == 0:
                        min_repetitions[current_token] = 0
                        max_repetitions[current_token] = None
                        backslashes = 0
                        continue
                elif x[y] == "+":
                    if backslashes % 2 == 0:
                        min_repetitions[current_token] = 1
                        max_repetitions[current_token] = None
                        backslashes = 0
                        continue
                elif x[y] == "|":
                    if backslashes % 2 == 0:
                        match_tokens.append(match_token)
                        match_token = ""
                        backslashes = 0
                        continue
                elif x[y] == "$":
                    if backslashes % 2 == 0:
                        store_index = x[y+1:]
                        try:
                            store_index = int(store_index)
                        except:
                            print(f"Invalid store index '{store_index}'")
                            exit(1)
                        while len(store) <= store_index:
                            store.append(None)
                            get.append([])
                        store[store_index] = current_token
                        backslashes = 0
                        break
                elif x[y] == "%":
                    if backslashes % 2 == 0:
                        get_index = x[y+1:]
                        try:
                            get_index = int(get_index)
                        except:
                            print(f"Invalid get index '{get_index}'")
                            exit(1)
                        while len(get) <= get_index:
                            store.append(None)
                            get.append([])
                        get[get_index].append(current_token)
                        backslashes = 0
                        break
                elif x[y] == "{":
                    if backslashes % 2 == 0:
                        if y + 2 >= len(x):
                            print("ERROR: expected size after {")
                            exit(1)
                        first = ""
                        second = ""
                        switched = 0
                        for z in range(y+1, len(x)):
                            if x[z] == ",":
                                switched = 1
                                continue
                            elif x[z] == "}":
                                break
                            if switched:
                                second += x[z]
                            else:
                                first += x[z]
                        if first == "":
                            first = 1
                        if second == "":
                            second = first
                        backslashes = 0
                        break
                elif x[y] == "?":
                    if backslashes % 2 == 0:
                        match_openers[current_token] = True
                        backslashes = 0
                        break
                elif x[y] == "!":
                    if backslashes % 2 == 0:
                        match_closers[current_token] = True
                        backslashes = 0
                        break


                if x[y] != "\\":
                    backslashes = 0

                match_token += x[y]


            if len(match_token) > 0:
                match_tokens.append(match_token)

            if the_fun == None:
                matchers[current_token] = create_contains_fun(match_tokens)
            else:
                matchers[current_token] = the_fun

            print(match_tokens)


            current_token += 1


        print("Clause", clause)
        print("min_reps", min_repetitions)
        print("max_reps", max_repetitions)
        print("matchers", matchers)
        print("match_openers", match_openers)
        print("match_closers", match_closers)
        print("store", store)
        print("get", get)
        result = MatchRule(clause, min_repetitions, max_repetitions, matchers, match_openers, match_closers, store, get)
        return result


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

