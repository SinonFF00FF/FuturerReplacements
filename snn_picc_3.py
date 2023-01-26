import copy
from typing import *
from PIL import Image
import snn_grl
import os
import warnings


# May God have mercy with whoever has to read this abomination


class __Var:
    bit_map = {"0": "0", "1": "10", "end": "11"}  # pls dont change
    data_index = 1
    cc_index = 1


class BaseICInitWarning(Warning):
    pass


class BaseICFormatWaring(Warning):
    pass


def _bytes_gen(a: bytes, max_len: int) -> Generator[str, None, None]:
    store_item = []
    for y in a:
        for yy in snn_grl.make_set_len(bin(y)[2:], 8):
            store_item.append(yy)
            if len(store_item) == max_len:
                yield "".join(store_item)
                store_item = []
    if store_item:
        yield snn_grl.make_set_len("".join(store_item), max_len, side="right")


def _make_cc_mpb(a: Union[Tuple[int, ...], List[int], bytes]) -> Tuple[List[List[int]], int]:
    b = [[yy for yy in range(y.bit_length()) if y & 1 << yy] for y in a]
    return b, sum([len(y) for y in b])


def _make_data(func):
    def IN(*arg, **kwargs):
        try:
            a = kwargs.get("data", None)
            if a is None:
                arg = list(arg)
                a = arg[__Var.data_index]
                arg.remove(a)
            else:
                kwargs.pop("data")
        except (IndexError, KeyError, TypeError):
            raise ValueError("no data given")
        return func(*arg, data=snn_grl.bitstr_to_bytes_3(
            snn_grl.write_val_bits([len(a)], **__Var.bit_map)) + a, **kwargs)

    return IN


def _read_data(a: Union[Generator[bytes, None, None], bytes]) -> bytes:
    """should work with bytes to (in my head/before I did some changes didn't tested if after that)"""
    b, list1, d = "", [], not isinstance(a, bytes)
    for iy, y in enumerate(a):
        if d:
            y = int.from_bytes(y, "little")
        for yy in snn_grl.make_set_len(bin(y)[2:], 8):
            b += yy
            if len(b) > 2:
                raise OverflowError("no data len found")
            if b in __Var.bit_map.values():
                if b == __Var.bit_map["end"]:
                    c = int("".join(list1[::-1]), 2)
                    break
                else:
                    list1.append(snn_grl.get_key(b, __Var.bit_map))
                b = ""
        else:
            continue
        break
    else:
        raise OverflowError("no data len found")
    if d:
        list2 = []
        for iyy, yy in enumerate(a):
            if iyy == c:
                break
            list2.append(yy)
        return b''.join(list2)
    else:
        return a[iy + 1:iy + 1 + c]


def make_cc(func):
    def IN(*args, **kwargs):
        try:
            a = kwargs.get("cc", None)
            if a is None:
                args = list(args)
                a = args[__Var.cc_index]
                args.remove(a)
            else:
                kwargs.pop("cc")
        except (IndexError, KeyError, TypeError):
            raise ValueError("no data given")
        return func(*args, cc=_make_cc_mpb(a), **kwargs)

    return IN


def _write_cc_header(cc: Tuple[List[List[int]], int], mpd: int) -> Generator[str, None, None]:
    a = snn_grl.bytes_to_bitstr(bytes([sum([1 << yy for yy in y]) for y in cc[0]]))
    for y in range((len(a) + mpd - 1) // mpd):
        yield a[mpd * y:mpd * (y + 1)]


class _Base_SI:
    __bd1, __bd8, __bd16 = ["1"], ["L", "P"], ["LA", "PA", "La", "I;16", "I;16L", "I;16B", "I;16N", "BGR;16"]
    __bd24, __bd32 = ["RGB", "YCbCr", "LAB", "HSV", "BGR;24"], ["I", "F", "CMYK", "RGBA", "BGR;32", "RGBa", "RGBX"]

    def __init__(self):
        self.IMG, self.bit_deep, self.filename, self.bit_deep_channel, self.gen_obj = None, 0, None, None, None

    def __get_pc(self) -> Generator[Tuple[Tuple[int, int], Tuple[int, ...]], None, None]:
        for y in range(self.IMG.height):
            for x in range(self.IMG.width):
                yield (x, y), self.IMG.getpixel((x, y))

    def open(self, a: str, abs_path: bool = False):
        self.filename = a
        return self.from_Image(Image.open(a if abs_path else os.path.join(os.getcwd(), a)))

    def from_Image(self, a: Image):
        self.IMG = copy.deepcopy(a)
        self.gen_obj = self.__get_pc()
        for iy, y in enumerate([_Base_SI.__bd1, _Base_SI.__bd8, _Base_SI.__bd16, _Base_SI.__bd24, _Base_SI.__bd32]):
            if self.IMG.mode in y:
                self.bit_deep = max(iy * 8, 1)
                self.bit_deep_channel = self.bit_deep // len(self.IMG.mode)
                break
        else:
            warnings.warn(BaseICInitWarning("image_mode isn't in bit_deep_list"
                                            " (or I forgot to add it (that's more likely))"))
        return self

    def save(self, a: str, abs_path: bool = False):
        b = getattr(self, "ok_exts", [])
        if not (os.path.splitext(a)[1] in b) and b:
            warnings.warn(BaseICFormatWaring("this ext is not fully supported"))
        self.IMG.save(a if abs_path else os.path.join(os.getcwd(), a))

    def show(self, a: bool = True):
        """only for debug stuff remove late"""
        print("\n".join(["-" * 100, "show_info:", f"bit_deep: {self.bit_deep}",
                         f"bit_deep_channel: {self.bit_deep_channel}",
                         f"size: {self.IMG.size}", f"filename: {self.filename}",
                         f"mode: {self.IMG.mode}", "-" * 100]))
        if a:
            self.IMG.show()

    def __enter__(self):
        # TODO: make this func pls
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        # TODO: make this func pls
        pass


class _Base_single_bit_IC(_Base_SI):
    ok_exts = [".png"]

    def write(self, cc: Tuple[List[List[int]], int], data: bytes) -> None:
        """only call from subclass with processed cc (and data)"""
        a, b, p = _bytes_gen(data, cc[1]), cc[0], self.IMG.load()
        try:
            for y0, y1 in self.gen_obj:
                p[y0] = self._single_encode(y1, b, next(a))
        except StopIteration:
            return
        if next(a, None) is not None:
            raise OverflowError("the img is to small for the data")

    def read(self, mpd: int, cc: List[List[int]], img0: Optional[_Base_SI] = None) -> Generator[bytes, None, None]:
        si, i, b = [], 0, [cc]
        if img0 is not None:
            b.append(img0)
        for _, y in self.gen_obj:
            i += mpd
            si.append(self._single_decode(y, *b))
            while i >= 8:
                a = "".join(si)
                yield int.to_bytes(int(a[:8], 2), 1, "little")
                si = [a[8:]]
                i -= 8

    @make_cc
    def get_max_data(self, cc) -> int:
        """for getting the max number of bytes that the img can hold with the given cc \n
        :param cc: tbh idk how to explain what cc is (it's a tuple of int in range(256)) so good luck
        :return: the number of bytes the img can hold"""
        a = ((self.IMG.width * self.IMG.height - self._get_offset()) * cc[1] + 5) // 8
        print(a)
        for y in range(a, 0, -1):
            b = len(bin(y)[2:])
            if (b + sum([1 for yy in range(b) if yy & y]) + 7) // 8 + y < a:
                return y + 1
        return 0


class IC_0(_Base_single_bit_IC):
    """for single bit swap with cc in header"""

    def from_Image(self, a: Image):
        super().from_Image(a)
        self.static_cc = [[] if y in ["a", "A"] else [0] for y in self.IMG.mode]  # dude irdc I wont make a new
        self.static_mpd = sum([len(y) for y in self.static_cc])  # __init__ for two attr that are NULL by default
        return self

    def _single_encode(self, p: Tuple[int, ...], cc: List[List[int]], d: str) -> Tuple[int, ...]:
        list1, i, b, c = [], 0, self.bit_deep_channel - 1, len(d)
        for iy, y in enumerate(p):
            list2 = []
            for iyy, yy in enumerate([y for y in snn_grl.make_set_len(bin(y)[2:], self.bit_deep_channel)]):
                if (b - iyy) in cc[iy]:
                    if i < c:
                        a = d[i]
                        i += 1
                    else:
                        a = "0"
                    list2.append(a)
                else:
                    list2.append(yy)
            list1.append(int("".join(list2), 2))
        return tuple(list1)

    def _single_decode(self, p0: Tuple[int, ...], cc: List[List[int]]) -> str:
        list1, b = [], self.bit_deep_channel - 1
        for iy, y in enumerate(p0):
            for iyy, yy in enumerate([y for y in snn_grl.make_set_len(bin(y)[2:], self.bit_deep_channel)]):
                if (b - iyy) in cc[iy]:
                    list1.append(yy)
        return "".join(list1)

    @make_cc
    @_make_data
    def encode(self, cc, data: bytes) -> None:
        """nice single bit swap encode func \n
        :param cc: tbh idk how to explain what cc is (it's a tuple of int in range(256)) so good luck
        :param data: the data you want to put into the img"""
        b, p = _write_cc_header(cc, self.static_mpd), self.IMG.load()
        for _, y in zip(range((len(self.static_cc) * 8 - 1 + self.static_mpd) // self.static_mpd), self.gen_obj):
            p[y[0]] = self._single_encode(y[1], self.static_cc, next(b))
        self.write(cc, data)

    def decode(self) -> bytes:
        """nice single bit swap decode func"""
        a = _make_cc_mpb(b''.join(
            [y for _, y in zip(range(len(self.IMG.mode)), self.read(mpd=self.static_mpd, cc=self.static_cc))]))
        return _read_data(self.read(mpd=a[1], cc=a[0]))

    def _get_offset(self) -> int:
        return (len(self.static_cc) * 8 - 1 + self.static_mpd) // self.static_mpd


class IC_1(_Base_single_bit_IC):
    """for single xor bit with cc in header"""

    def single_encode(self, cc, data, p0, p1) -> Tuple[int, ...]:
        pass

    def single_decode(self, cc, p0, p1) -> str:
        pass

    @make_cc
    @_make_data
    def encode(self, cc, data) -> None:
        pass

    def decode(self, org_img) -> bytes:
        pass

    @staticmethod
    def _get_offset() -> int:
        return 1
