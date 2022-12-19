import pickle
import itertools


def weight(a):
    return a.weight()


class MoneyOpen:
    def __init__(self, filename):
        self._filename = filename

    def _load(self):
        with open(self._filename, mode="rb") as f:
            self._list = pickle.load(f)
        return self._list

    def _dump(self):
        self._list.dump(self._filename)

    def __enter__(self):
        return self._load()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._dump()


class Money_list:
    def __init__(self, names):
        self._names_list = names
        self._names_dict = {names[i]: i for i in range(len(names))}
        self._data = [0 for i in range(len(names) - 1)]
        self._payment_state = False

    def __str__(self):
        if self._payment_state:
            self._change_sequence()
            self._payment_state = False
        lines = []
        for i in range(len(self._data)):
            x = round(self._data[i])
            if x == 0:
                continue
            if x > 0:
                line = self._names_list[i] + "  >>>  " + str(x) + "  >>>  " + self._names_list[i + 1]
            else:
                line = self._names_list[i] + "  <<<  " + str(abs(x)) + "  <<<  " + self._names_list[i + 1]
            lines.append(line)
        return "\n\n".join(lines)

    def dump(self, filename):
        with open(filename, mode="wb") as f:
            pickle.dump(self, f)

    def pay(self, payer, recipient, value):
        if payer == recipient:
            return
        self._payment_state = True
        if recipient == "all":
            value /= len(self._names_list)
            for name in self._names_list:
                self.pay(payer, name, value)
            return
        start = self._names_dict[recipient]
        finish = self._names_dict[payer]
        if start < finish:
            for i in range(start, finish):
                self._data[i] += value
        else:
            for i in range(start - 1, finish - 1, -1):
                self._data[i] -= value

    def clear(self):
        for i in range(len(self._data)):
            self._data[i] = 0

    def weight(self):
        return sum((abs(x) for x in self._data))

    def _change_sequence(self):
        Money_lists = []
        for sequence in itertools.permutations(self._names_list):
            new_list = Money_list(list(sequence))
            for i in range(len(self._data)):
                new_list.pay(self._names_list[i + 1], self._names_list[i], self._data[i])
            Money_lists.append(new_list)
        top = min(Money_lists, key=weight)
        self._names_list = top._names_list
        self._names_dict = top._names_dict
        self._data = top._data



# if __name__ == "__main__":
    # with MoneyOpen("data.bin") as work:
    #     work.pay("Ilya", "Valek", 3180)
    #     print(work)
