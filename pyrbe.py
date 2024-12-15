

class Rule:
    def __init__(self):
        pass


class RBE:
    def __init__(self):
        self.rules:list[Rule] = []

    # should allow reading rules from a human readable file
    def read_from_file(self, filename:str) -> list[Rule]:
        try:
            with open(filename, "r") as f:
                the_file = f.read()
        except:
            print(f"Could not open file ({the_file})")
            exit(0)

        return result






if __name__ == "__main__":
    rbe = RBE()

