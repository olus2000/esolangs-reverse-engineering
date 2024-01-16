from dataclasses import dataclass, field


@dataclass
class BCTState:
    program : list[int]
    ip : int = 0
    data : list[int] = field(default_factory=lambda: [1])
    consumed : int = 0

    def tick(self):
        self.ip = (self.ip + 1) % len(self.program)

    def steppable(self):
        return len(self.data) > self.consumed

    def step(self):
        if not self.steppable():
            raise Exception('Unsteppable state!\n' + str(self))
        if self.program[self.ip]:
            self.tick()
            if self.data[self.consumed]:
                self.data.append(self.program[self.ip])
        else:
            self.consumed += 1
        self.tick()



def int_to_list(i):
    ans = []
    while i:
        ans.append(i % 2)
        i //= 2
    return list(reversed(ans))


def generate_tags(l=2):
    n = 2**l
    while True:
        yield BCTState(int_to_list(n))
        n += 1


def generate_halting(l=2):
    gen = generate_tags(l)
    tags = []
    i = 0
    while True:
        if i < len(tags):
            if tags[i].steppable():
                tags[i].step()
                i += 1
            else:
                yield tags[i]
                tags.pop(i)
        else:
            tags.append(next(gen))
            i = 0
