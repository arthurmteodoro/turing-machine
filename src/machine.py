from src.parser import Parser
from src.utils import Utils


class Machine(object):
    def __init__(self, header="()"):
        self.__tape = ["_" for _ in range(500)]
        self.__code = None
        self.__state = -1
        self.__tape_index = 250
        self.__stack = []
        self.__complete_compute = False

        self.__parser = Parser()
        self.__header = [header[0], header[1]]
        self.__stop_breakpoint = False

    @property
    def keep_run(self):
        return not self.__complete_compute and not self.__stop_breakpoint

    @property
    def state(self):
        return self.__state

    @property
    def block(self):
        return self.__stack[-1][0].name

    @property
    def tape(self):
        return self.__tape

    @property
    def tape_index(self):
        return self.__tape_index

    @property
    def output(self):
        block_name_len = len(self.__stack[-1][0].name)
        block = "." * (16 - block_name_len)
        block += self.__stack[-1][0].name

        state_len = len(str(self.__state))
        state = "0" * (4 - state_len)
        state += str(self.__state)

        left_tape = "".join(self.__tape[self.__tape_index-20:self.__tape_index])
        header = self.__header[0] + self.__tape[self.__tape_index] + self.__header[1]
        right_tape = "".join(self.__tape[self.__tape_index+1:self.__tape_index+21])

        return block + "." + state + ": " + left_tape + header + right_tape

    def load_code(self, file_name):
        self.__code = self.__parser.parse_file(file_name)
        self.__state = self.__code["main"].initial_state
        self.__stack.append((self.__code["main"], -1))

    def load_word(self, word):
        self.__tape[self.__tape_index:len(word)] = word

    def step(self):
        char_head = self.__tape[self.__tape_index]
        this_state = self.__state
        block = self.__stack[-1][0]
        self.__stop_breakpoint = False

        if not self.__complete_compute:
            if this_state in block.commands:
                possible_transitions = block.commands[this_state]

                possible_transitions.sort(key=lambda trans: trans[0])
                possible_transitions.reverse()

                compute = False

                for transition in possible_transitions:
                    if transition[-1]:
                        self.__stop_breakpoint = True

                    if transition[0] == char_head:
                        if transition[1] == "*":
                            self.__tape[self.__tape_index] = self.__tape[self.__tape_index]
                        else:
                            self.__tape[self.__tape_index] = transition[1]

                        if transition[2] == "e":
                            self.__tape_index -= 1
                        elif transition[2] == "d":
                            self.__tape_index += 1

                        if transition[3] == "*":
                            self.__state = self.__state
                        elif transition[3] == "pare":
                            self.__complete_compute = True
                        elif transition[3] == "retorne":
                            self.__state = self.__stack[-1][1]
                            self.__stack.pop()
                        else:
                            self.__state = transition[3]

                        compute = True
                        break
                    elif transition[0] in self.__code:
                        new_state = self.__code[transition[0]]
                        self.__stack.append((new_state, transition[1]))
                        self.__state = new_state.initial_state
                        compute = True
                        break
                    elif transition[0] == "*":
                        if transition[1] == "*":
                            self.__tape[self.__tape_index] = self.__tape[self.__tape_index]
                        else:
                            self.__tape[self.__tape_index] = transition[1]

                        if transition[2] == "e":
                            self.__tape_index -= 1
                        elif transition[2] == "d":
                            self.__tape_index += 1

                        if transition[3] == "*":
                            self.__state = self.__state
                        elif transition[3] == "pare":
                            self.__complete_compute = True
                        elif transition[3] == "retorne":
                            if self.__stack[-1][1] == "pare":
                                self.__complete_compute = True
                            else:
                                self.__state = self.__stack[-1][1]
                            self.__stack.pop()
                        else:
                            self.__state = transition[3]

                        compute = True
                        break
                if not compute:
                    raise Exception(Utils.Colors.FAIL + "Not transition found" + Utils.Colors.ENDC)
            else:
                raise Exception(Utils.Colors.FAIL + "State %s not exists" % (this_state, ) + Utils.Colors.ENDC)


if __name__ == '__main__':
    a = Machine()

    try:
        a.load_code("../palindromo.MT")

        word_input = input("Digite a palavra de entrada: ")
        a.load_word(word_input)

        print(a.output)
        while a.keep_run:
                a.step()
                print(a.output)

    except Exception as err:
        print(err)