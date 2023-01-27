from typing import *
import math
import warnings
import copy
import re


# May God have mercy with whoever has to read this abomination


def kwargs_handler(kwarg_in: Dict[Any, Any], base_kwarg_dict: Dict[Any, Any],
                   test_for_type: bool = True) -> Dict[Any, Any]:
    base_kwarg_dict = copy.deepcopy(base_kwarg_dict)
    for y in kwarg_in:
        if y in base_kwarg_dict.keys():
            if test_for_type and not isinstance(kwarg_in[y], type(base_kwarg_dict[y])):
                raise TypeError(f"wrong type for {y} (is {type(kwarg_in[y])} should be {type(base_kwarg_dict[y])})")
            base_kwarg_dict[y] = kwarg_in[y]
        else:
            raise ValueError(f"wrong kwarg {y} (possible kwargs: {base_kwarg_dict.keys()})")
    return base_kwarg_dict


def kwargs_handler_2(kwarg_in: Dict[Any, Any], base_kwarg: Dict[Any, Any], test_type: bool = True) -> Dict[Any, Any]:
    bkd = copy.deepcopy(base_kwarg)
    for y0, y1 in kwarg_in.items():
        no_match = False
        try:
            a = bkd[y0]
            if test_type:
                if len(a) == 2 and isinstance(a, tuple
                                              ) and re.match(r"^<class 'typing\.+\w+'>$", str(type(a[0]))):
                    e = str(a[0])
                    if e == "typing.Any":
                        continue
                    b = re.search(r"[\[,]+.*[],]", e)
                    if b:
                        c = b.group()[1:-1].split(", ")
                        if "NoneType" in c:
                            c[c.index("NoneType")] = "None"
                        exec(rf"d = isinstance(y1, tuple(c))")
                    else:
                        no_match = True
                else:
                    d = type(a)
                if not isinstance(y1, d):
                    no_match = True
                if no_match:
                    raise TypeError(rf"wrong type for {y0} (is {type(y1)} should be {type(a)})")
        except KeyError:
            no_match = True
            raise ValueError(f"wrong kwarg {y0} (possible kwargs: {base_kwarg.keys()})")
        finally:
            if not no_match:
                bkd[y0] = y1
    return bkd


def make_set_len(a: str, lenlen: int, fill_str: str = "0", side: str = "left") -> str:
    side = {"left": (1, 0), "right": (0, 1)}[side]
    return fill_str * ((lenlen - len(a)) * side[0]) + a + fill_str * ((lenlen - len(a)) * side[1])


def make_set_len_4(a: str, lenlen: int) -> str:
    return "0" * (lenlen - len(a)) + a


def make_set_len_2(a: int, lenlen: Optional[int] = None, prefix: Optional[str] = "") -> str:
    if lenlen is None:
        lenlen = a.bit_length()
    c = 1 << lenlen-1
    return prefix + "".join(["1" if (a << y) & c else "0" for y in range(lenlen)])


def make_set_len_3(a: int, lenlen: Optional[int] = None, prefix: Optional[str] = "") -> str:
    if lenlen is None:
        lenlen = a.bit_length()
    return prefix + "".join(["1" if (a >> y) & 1 else "0" for y in range(lenlen)])


def str_to_bytes(a: str, encoding: str = "utf8") -> bytes:
    return bytes(a, encoding=encoding)


def get_key(val: Any, search_dict: Dict[Any, Any]) -> Any:
    return list(search_dict.keys())[list(search_dict.values()).index(val)]


class ValBitsReadWarning(Warning):
    pass


def write_val_bits(a: Union[Tuple[int, ...], List[int]], **kwargs) -> str:
    base_kwarg_dict = {"0": "0", "1": "10", "end": "11"}
    kwargs, list1 = kwargs_handler(kwargs, base_kwarg_dict, True), []
    for y in a:
        for yy in bin(y)[2:][::-1]:
            list1.append(kwargs[yy])
        list1.append(kwargs["end"])
    return "".join(list1)


def read_val_bits(a: Union[str, Generator[str, None, None]], int_count: int, **kwargs) -> List[int]:
    base_kwarg_dict = {"0": "0", "1": "10", "end": "11"}
    list1, list2, b, kwargs = [], [], "", kwargs_handler(kwargs, base_kwarg_dict, True)
    for y in a:
        b += y
        if b in kwargs.values():
            if b == kwargs["end"]:
                list2.append(int("".join(list1), 2))
                if len(list2) == int_count:
                    break
                list1 = []
            else:
                list1.append(get_key(y, kwargs))
            b = ""
    else:
        warnings.warn("no enough items are found")
    return list2


def bitstr_to_bytes_2(a: str) -> bytes:
    a = bytes([int(a[y:y + 8], 2) for y in range(len(a)) if not y % 8])
    for iy, y in enumerate(a[::-1]):
        if y != 0:
            return a[:-iy] if iy else a
    return b''


def bitstr_to_bytes(a: str) -> bytes:
    return bytes([int(a[y:y + 8], 2) for y in range(len(a)) if not y % 8])


def bitstr_to_bytes_3(a: str) -> bytes:
    return bytes([int(make_set_len(a[y * 8:(y + 1) * 8], 8, side="right"), 2) for y in range((len(a) + 7) // 8)])


def bitstr_to_bytes_gen(a: str) -> Generator[bytes, None, None]:
    for y in range(len(a) // 8):
        yield bytes(int(a[y * 8:(y + 1) * 8], 2))


def bytes_to_bitstr(a: bytes) -> str:
    return "".join([make_set_len(bin(y)[2:], 8) for y in a])


def bytes_to_bitstr_gen(a: bytes) -> Generator[str, None, None]:
    for y in a:
        for yy in make_set_len(bin(y), 8):
            yield yy


def snn_split(a: Union[str, list, bytes], b: int) -> List[Union[str, list, bytes]]:
    return [a[y * b: (y + 1) * b] for y in range((len(a) + b - 1) // b)]


def snn_split_gen(a: Union[str, list, bytes], b: int) -> Generator[Union[str, list, bytes], None, None]:
    for y in range((len(a) + b - 1) // b):
        yield a[y * b: (y + 1) * b]


def gen_prime() -> Generator[int, None, None]:
    a, i = [], 3
    yield 2
    while True:
        for y in a:
            if not (i % y):
                break
        else:
            yield i
            a.append(i)
        i += 2


def all_primes_to_number(a: int) -> List[int]:
    b, a, c = [False, False] + [True] * (a - 1), a + 1, int(math.sqrt(a) + 1)
    for y in range(2, c):
        if b[y]:
            for yy in range(y << 1, a, y):
                b[yy] = False
    return [iy for iy, y in enumerate(b) if y]


def all_primes_to_number_2(to_number: int) -> List[int]:
    b, a, c, l1 = [False, False] + [True] * (to_number - 1), to_number + 1, int(to_number ** 0.5 + 1), [2]
    for y in range(3, c, 2):
        if b[y]:
            for yy in range(y << 1, a, y):
                b[yy] = False
            l1.append(y)
    return l1


def pfz(a: int) -> List[int]:
    b, list1 = all_primes_to_number(a), []
    while a > 1:
        for y in list(b):
            if not (a % y):
                a //= y
                b = [y] + b
                break
            else:
                b.remove(y)
    return list1


class typing_match:
    """if you want to lower my self-esteem even more show me the build in func that does the same
     that I couldn't find"""

    class Node:
        def __init__(self, *args):
            self.next_node = None
            self.contains = args

        def node_check(self, a: Any):
            pass

    def __init__(self, a):
        """a should be a typing obj"""
        self.contains = [[], []]
        working = tuple([a])
        is_inst = [False, False]
        while not all(is_inst):
            fake_w = []
            for iy, y in enumerate(working):
                if not is_inst[iy]:
                    try:
                        print(f"{iy}, {y}")
                        y = y.__dict__
                        print("dict: ", y)
                        is_inst[iy] = y["_inst"]
                        org = y["__origin__"]
                        if isinstance(org, type):
                            self.contains[iy].append(org)
                            is_inst[iy] = True
                        y_args = y["__args__"]
                        self.contains[iy].append(y_args)
                        fake_w += list(y_args)
                        dummy = 0
                    except KeyError:
                        pass
            working = tuple(fake_w)

    def check(self, a: Any) -> bool:
        pass

    @classmethod
    def check2(cls, a: Any, b) -> bool:
        """b should be a typing obj"""
        return cls(b).check(a)
