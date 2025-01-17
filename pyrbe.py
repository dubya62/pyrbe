

class MatchResult:
    def __init__(self, clause:str, matched_tokens:list[list[str]], offset:int, length:int, variables:list[list[str]]):
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


    def partial_match(self, clause_index, tokens, current_matches):
        # perform the first part of a match. 
        # once matched, try to match the rest of the tokens with all but the first part of the clause
        
        # match the first token of the clause with all possible token matches
        print(f"partial_match: {clause_index} {self.clause[clause_index]} {tokens} {self.clause[clause_index+1:]}")
        matches = []
        matcher = self.matchers[clause_index]
        print(f"Matcher: {matcher}")

        start_reps = self.min_repetitions[clause_index]
        if start_reps is None:
            start_reps = 0

        end_reps = self.max_repetitions[clause_index]
        if end_reps is None:
            end_reps = len(tokens)+1
        print(f"start: {start_reps}\tend: {end_reps}")

        # first, match with the minimum number
        i = 0
        while i < start_reps:
            if i >= len(tokens):
                # there are not enough tokens to even start: return None
                return None
            # check if this matches
            matches = matcher(tokens[i])
            if not matches:
                # we cannot even start matching.
                return None
            i += 1

        print(f"current_matches: {current_matches}")
        # we have now matched with the minimum number
        result = []
        while i <= end_reps:
            # if it does match, recursively call
            print(f"remaining: {tokens[i:]}")
            if clause_index + 1 < len(self.matchers):
                print(f"SENT TO CHILD")
                new_matches = current_matches + [(self.clause[clause_index], tokens[:i])]
                child_result = self.partial_match(clause_index + 1, tokens[i:], new_matches)
                result.append(child_result)
            else:
                print("NO CHILD REMAINING")


            if i < len(tokens):
                # if out of tokens, return the result
                matches = matcher(tokens[i])
                print(matches, tokens[i], matcher)
            else:
                if clause_index == len(self.clause) - 1:
                    print(f"MADE IT TO THE END: {current_matches + [(self.clause[clause_index], result)]}")
                    return ("END", current_matches + [(self.clause[clause_index], tokens)])
                print("NO CHILD REMAINING")
                return result

            # if it doesn't match, then we are done for this token
            if not matches:
                return result
            i += 1


        return result


    def parse_matches(self, matches):
        results = []
        print(f"matches: {matches}")
        if matches is not None:
            for match in matches:
                if issubclass(type(match), list): 
                    print(f"match {match}")
                    result = self.parse_matches(match)
                    if result is not None:
                        results += result
                elif match != None:
                    if match[0] == "END":
                        return [match[1]]

        if len(results) > 0:
            return results
        return None


    def match(self, tokens) -> list[MatchResult]:
        # attempt to match a list of tokens. and return all possible matches as a list of MatchResult
        i = 0
        n = len(tokens)
        print(self.clause)

        results = []
        while i < n:
            result = self.partial_match(0, tokens[i:], [])

            # parse the result for matches
            parsed = self.parse_matches(result)
            print(f"parsed: {parsed}")
            if parsed is not None:
                # convert the results into a MatchResult
                for x in parsed:
                    matched_tokens = []
                    length = 0
                    for y in x:
                        matched_tokens.append(y[1])
                        length += len(y[1])

                    # get the variable mappings
                    variable_mappings = []
                    for store in self.store:
                        variable_mappings.append(None)
                        if store is not None:
                            variable_mappings[-1] = matched_tokens[store]

                    match_result = MatchResult(self.clause, matched_tokens, i, length, variable_mappings)
                    results.append(match_result)
            i += 1

        print("\n\n\n")
        print("ALL POSSIBLE MATCHES:")
        print(results)
        print("\n\n\n")
        return results


class Rule:
    def __init__(self, clauses:list[str], condition:str):
        self.clauses = clauses
        self.condition = condition

        self.metrics = []
        self.parse_metrics()

        print("\nCOMPILING:")
        self.compiled = [self.compile_clause(x) for x in self.clauses]


    def match(self, tokens):
        print("Matching tokens against rule")


    def minimize(self, metric, tokens):
        print(f"Minimizing metric {metric} for tokens: {tokens}")
        # if the condition is checkable, check it
        print(f"Checking the condition: {self.condition}")
        # TODO: check the condition
        condition = True

        # if condition is true or not checkable, start matching
        # iterate through the compiled clauses
        if condition:
            print(f"Condition was True. Matching against compiled clauses.")
            print(f"Minimizing metric {metric}: ({self.metrics})")

            # try matching each compiled clause
            clause = 0
            num_clauses = len(self.compiled)
            while clause < num_clauses:
                print(f"Checking against clause: {self.compiled[clause]}")
                match_results = self.compiled[clause].match(tokens)
                print(f"Matching results: {match_results}")

                # we now have the match results. now look for a clause that is cheaper than this one
                if len(match_results) > 0:
                    print("We have found a match")
                    my_metric = self.metrics[clause][metric]
                    if my_metric == "_":
                        my_metric = 10000000000000000000
                    my_metric = int(my_metric)
                    print(f"Current metric: {my_metric}")

                    min_metric_index = clause
                    min_metric = my_metric
                    for i in range(len(self.metrics)):
                        other_metric = self.metrics[i][metric]
                        if other_metric == "_":
                            other_metric = 10000000000000000001
                        other_metric = int(other_metric)

                        print(f"Other metric: {other_metric}, My metric: {my_metric}")
                        if other_metric < min_metric:
                            min_metric = other_metric
                            min_metric_index = i

                    print(f"Cheapest found metric: {min_metric}     - saves {my_metric - min_metric}")
                    print(f"Replacing clause {clause} with {min_metric_index}") 

                    # use the match result to perform the substitution
                    tokens = self.perform_substitution(tokens, match_results[0], min_metric_index)

                    return tokens

                clause += 1
        

        # if the condition was false, just quit
        return tokens


    def perform_substitution(self, tokens:list[str], match_result:MatchResult, substitution_clause):
        result = tokens[:match_result.offset] 

        comp = self.compiled[substitution_clause]
        print(f"comp: {comp}")

        print(f"vars: {match_result.variables}")

        sub = []
        for tok in range(len(comp.clause)):
            subbed = False
            if len(comp.store) > tok and comp.store[tok] is not None:
                if len(match_result.variables) > comp.store[tok]:
                    sub += match_result.variables[comp.store[tok]]
                    print(f"Subbing: {sub}")
                    subbed = True
            else:
                for get_index, get in enumerate(comp.get):
                    if tok in get:
                        print(f"get found: {tok}")
                        sub += match_result.variables[get_index]
                        subbed = True

            if not subbed:
                sub.append(comp.clause[tok])

        result += sub
        result += tokens[match_result.offset+match_result.length+1:]
        print(f"Substituted into {self.clauses[substitution_clause]}")
        print(f"Substitution Result: {result}")
        return result



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
        self.match_tokens = []
        for i in range(len(clause)):
            self.match_tokens.append([])

        def ANY(token:str):
            return True

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
                        match_tokens.append(match_token.strip("\\"))
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
                match_tokens.append(match_token.strip("\\"))

            if the_fun == None:
                self.match_tokens[current_token] = list(match_tokens)

                matchers[current_token] = self.create_contains(match_tokens)
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


    def create_contains(self, match_tokens):
        new_match_tokens = []
        for x in match_tokens:
            new_match_tokens.append(x)
        return lambda tok: tok in new_match_tokens


    def match(self, tokens:list[str]):
        # match a list of tokens against this rule
        # return the matched clause, which tokens were matched (as a list of lists), 
        # the offset of the match, the number of matched tokens, and a list of the variable values

        for clause in self.compiled:
            print(f"Matching clause {clause}")
            clause.match(tokens)

        

    def __str__(self):
        return f"RULE: {' eq '.join(self.clauses)} if {self.condition if len(self.condition) else 'True'}"

    def __repr__(self):
        return self.__str__()



class RBE:
    def __init__(self):
        self.rules:list[Rule] = []

        self.file_data = self.read_from_file("test.rbe")
        print(self.file_data)
        rbe_string = self.parse_rbe_string(self.file_data)
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


    def minimize_metric(self, metric, tokens):
        # using my rules, minimize the given metric

        # match against each rule in order
        rule = 0
        num_rules = len(self.rules)
        while rule < num_rules:
            # attempt to reduce this metric using this rule
            current_rule = self.rules[rule]

            tokens = current_rule.minimize(metric, tokens)
            
            rule += 1

        return tokens



if __name__ == "__main__":
    rbe = RBE()

    test_tokens = ["if", "(", "x", ">", "0", ")", "{", "printf", "(", ")", ";", "}"]

    test_result = rbe.minimize_metric(0, test_tokens)

    print(f"\nTest Case: \n{test_tokens}\n=>\n{test_result}")






