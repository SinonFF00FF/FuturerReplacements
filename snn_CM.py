import io
import traceback
import inspect
import warnings
import snn_grl
from typing import *
from datetime import datetime
from copy import deepcopy
from time import time
import sys
import os
import snn_cry


class IOMP:
    _store_obj = []  # for log stuff

    def __init__(self, save: bool, st: str, pios: str):
        self.save_IO, self.show_time_IO, self.pre_ios = save, st, pios

    @classmethod
    def save(cls) -> str:
        return "".join(cls._store_obj)

    @classmethod
    def edit_base_kwargs(cls, **kwargs):
        cls._base_kwargs = snn_grl.kwargs_handler(kwargs, cls._base_kwargs, True)


class input_M(IOMP):
    __sep_chars = {"S0": " ", "S1": "()", "S2": "[]", "S3": "{}"}
    # S0 must be one char, Sx must be two different chars
    _base_kwargs = {"disable_int_convert": False, "disable_bool_convert": False, "disable_None_convert": False,
                    "show_time": "%X", "pre_input_str": ">>", "save": True,
                    "convert_to_True": "True", "convert_to_False": "False", "convert_to_None": "None"}

    @classmethod
    def __make_kwargs_default(cls) -> Dict[str, Union[bool, str]]:
        a = deepcopy(cls._base_kwargs)
        for y in cls.__sep_chars.keys():
            a[f"disable_{y}"] = False  # prio 1
            a[f"overwrite_{y}"] = ""  # prio 2, empty str for no overwrite
        return a

    def __init__(self, **kwargs):
        self.d, a = {}, snn_grl.kwargs_handler(kwargs, self.__make_kwargs_default(), True)
        super().__init__(save=a["save"], st=a["show_time"], pios=a["pre_input_str"])
        if sum([not (y in self._base_kwargs.keys()) for y in kwargs.keys()]):  # just for making it faster
            for y0, y1 in self.__sep_chars.items():
                if not a.get(f"disable_{y0}"):
                    c = a.get(f"overwrite_{y0}")
                    self.d[y0] = c if c else y1
        else:
            self.d = self.__sep_chars
        self.int_convert, self.bool_convert = not a["disable_int_convert"], not a["disable_bool_convert"]
        self.main_sep, self.sep_srt, self.sep_end, self.sep_chars = "", {}, {}, {}
        self.cT, self.cF, self.cN = a["convert_to_True"], a["convert_to_False"], a["convert_to_None"]
        for y0, y1 in self.d.items():
            if y1 is not None:
                if len(y1) > 1:
                    self.sep_chars[f"{y0}_srt"], self.sep_chars[f"{y0}_end"] = y1[0], y1[1]
                    self.sep_srt[y0], self.sep_end[y0] = y1[0], y1[1]
                else:
                    self.main_sep = y1

    def input(self, show_str: Optional[str] = None) -> List[Union[str, int, bool]]:
        d = f"{datetime.now().strftime(self.show_time_IO) if self.show_time_IO else ''} " \
            f"{'' if show_str is None else show_str + ' '}{self.pre_ios} "
        a, list1, list2, b = input(d), [], [], 0
        search3, h = None, len(a) - 1 + len(self.main_sep)
        if self.save_IO:
            IOMP._store_obj.append(f"{d}{a}\n")
        for iy, y in enumerate(a + self.main_sep):
            if y in self.sep_chars.values() and self.main_sep:
                if search3 is None:
                    search3 = self.d[snn_grl.get_key(y, self.sep_chars).split("_")[0]]
                if y in search3:
                    if y == search3[0]:
                        b += 1
                    else:
                        b -= 1
            elif (y == self.main_sep and not b) or iy == h:
                c = "".join(list1)
                if c:
                    if c[0] in self.sep_srt.values() and c[-1] in self.sep_end.values() and self.main_sep:
                        c = c[1:-1]
                if (c == self.cT or c == self.cF) and self.bool_convert:
                    c = c == self.cT
                elif c.isnumeric() and self.int_convert:
                    c = int(c)
                elif c == self.cN:
                    c = None
                list2.append(c)
                search3, list1 = None, []
                continue
            list1.append(y)
        return list2

    @classmethod
    def add_sep(cls, sep_start: str, sep_end: str):
        """needs to be called before you create an input_M obj else the added chars will not be in the obj"""
        if sum([len(y) == 1 for y in [sep_end, sep_start]]):
            raise ValueError("the sep chars must be one char each")
        cls.__sep_chars[f"S{len(cls.__sep_chars) + 1}"] = f"{sep_start}{sep_end}"


class output_M(IOMP):
    _base_kwargs = {"show_time": "%X", "pre_output_str": "<< ", "save": True}

    def __init__(self, **kwargs):
        a = snn_grl.kwargs_handler(kwargs, self._base_kwargs, True)
        super().__init__(save=a["save"], st=a["show_time"], pios=a["pre_output_str"])

    def output(self, show_str: Optional[str] = None, end: str = "") -> None:
        b = f"{datetime.now().strftime(self.show_time_IO)} " if self.show_time_IO else ""
        c, e = " " * (len(b) + len(self.pre_ios)), show_str.count("\n")
        g = f"\n{c + end}\n" if end else "\n"
        for iy, y in enumerate(show_str.split("\n")):
            a = f"{f'{b}{self.pre_ios}' if not iy else c}{y}"
            d = g if iy == e else "\n"
            print(a, end=d)
            if self.save_IO:
                IOMP._store_obj.append(a + d)


class progress_bar:
    # I will write all this progress_bar stuff later after I finished the snn_mad_science module
    _base_kwargs = {"auto_end": True, "bar_len": 50, "show_%": True, "update_after": 0.1}

    def __init__(self, kwarg_dict: dict):
        a = snn_grl.kwargs_handler(kwarg_in=kwarg_dict, base_kwarg_dict=self._base_kwargs, test_for_type=True)
        self.auto_end = a["auto_end"]
        self.var_len = a["bar_len"]
        self.show_p = a["show_%"]
        self.update_time = a["update_after"]
        self.is_running = False

    def __bool__(self):
        return self.is_running

    def start(self):
        self.is_running = True
        pass

    def end(self):
        self.is_running = False
        pass

    def __update(self):
        pass


class progress_track(progress_bar):
    def __init__(self, end_at: Union[int, SupportsFloat, SupportsInt], mode: bool = True, **kwargs):
        super().__init__(kwargs)
        if mode:
            self.end_at = end_at
        else:
            self.track_var = id(end_at)

    def update(self, a: int):
        pass

    def __auto_update(self):
        pass

    def get_track_var(self) -> Any:
        pass


class progress_time(progress_bar):
    def __init__(self, end_after: float, **kwargs):
        super().__init__(kwargs)
        self.end_after_real = self.end_after = end_after

    def start(self):
        super().start()
        self.end_after_real += time()


def _access_check(func):
    def IN(self, *args, **kwargs):
        out_kwargs = [kwargs["key"] if "key" in kwargs else args[0]]
        try:
            out_kwargs.append(kwargs["value"] if "value" in kwargs else args[1])
        except IndexError:
            pass
        if out_kwargs[0] in self.no:
            warnings.warn(
                self.ConfigNoOverwriteWarning(f"{out_kwargs[0]} can not be overwritten/deleted (no changes are made)"))
        else:
            func(self, *out_kwargs)

    return IN


class Base_config:
    __kwargs_default = {"no_overwrite": [], "default_config": {}}
    __type_str_map = {"str": 's', "int": 'i', "bytes": 'b', "bool": 'B', "NoneType": 'N'}

    # if you want to change the __type_str_map also change the read, write and __type_str_decode methods

    class ConfigNoOverwriteWarning(Warning):
        pass

    def __init__(self, **kwargs):
        a = snn_grl.kwargs_handler(kwargs, self.__kwargs_default, True)
        self.contains: Dict[str, Union[str, int, bytes, bool, None, list]] = a["default_config"]
        self.no: List[str] = a["no_overwrite"]

    def __getitem__(self, item) -> Any:
        return self.contains[item]

    def __bool__(self) -> bool:
        return bool(self.contains)

    @_access_check
    def __delitem__(self, key: str) -> None:
        del self.contains[key]

    @_access_check
    def __setitem__(self, key: str, value: Union[str, int, bytes, bool, None, list]) -> None:
        self.contains[key] = value

    def read(self, a: bytes) -> None:
        for iy, y in enumerate(a.split(b'\x0A')):
            a = y.decode("utf8").split(" = ", maxsplit=1)
            key, val = a[0], self.__type_str_decode(a[1])
            if key in self.contains:
                if not isinstance(self.contains[key], list):
                    self.contains[key] = [self.contains[key]]
                self.contains[key].append(val)
            else:
                self.contains[key] = val

    @staticmethod
    def __type_str_decode(a: str):
        _id, _val = a[0], a[2:-1]
        if _id == "i":
            return int(_val)
        elif _id == "B" and _val in ["True", "False"]:
            return _val == "True"
        elif _id == "N" and _val == "None":
            return None
        elif _id == "b" and _val[:2] == "b'" and _val[-1] == "'":
            b0 = _val[2:-1].split(r"\x")
            return b''.join([bytes(b0[0], encoding="utf8")] + [int(y[:2], 16).to_bytes(1, "little") + bytes(
                y[2:], encoding="utf8") for y in b0[1:]])
        elif _id == "s":
            return _val
        raise ValueError(f"no decode method for {a} found")

    def write(self) -> bytes:
        return b'\n'.join([bytes(f"{y0} = " + f"\n{y0} = ".join(
            [rf"{self.__type_str_map[str(type(yy))[8:-2]]}'{yy}'" for yy in (
                y1 if isinstance(y1, list) else [y1])]), encoding="utf8") for y0, y1 in self.contains.items()])

    def make(self, a: Dict[str, Union[str, int, bytes, bool, None, list]]) -> None:
        self.contains = a

    def append(self, a: Any, key: Any) -> None:
        if not (key in self.no):
            self.contains[key] = a
        else:
            warnings.warn(self.ConfigNoOverwriteWarning(f"you can not overwrite {key} (no changes are made)"))

    def remove(self, a: Any, is_item: bool = False) -> None:
        key = snn_grl.get_key(a, self.contains) if is_item else a
        if not (key in self.no):
            del self.contains[key]
        else:
            warnings.warn(self.ConfigNoOverwriteWarning(f"you can not overwrite {key} (no changes are made)"))


class config_cry(Base_config):
    """don't use this for imported stuff its really unsafe"""

    # I really don't know why super does not work here but idc rn (and it works now so how cares .... right?(me))
    # and bad stuff that works is good stuff ... right? (no it's not, but I don't want to change this rn )
    def read(self, a: bytes, key: bytes) -> None:
        Base_config.read(self, snn_cry.snn_crypt_sym.decode(a, key, True))

    def write(self, key: bytes) -> bytes:
        return snn_cry.snn_crypt_sym.encode(Base_config.write(self), key, True)


class config_file(Base_config):
    def __init__(self, config_path: Union[os.PathLike, str], is_abs_path: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.config_path = config_path if is_abs_path else os.path.join(os.getcwd(), config_path)

    def read(self) -> None:
        with io.open(self.config_path, "rb") as f:
            super().read(f.read())

    def write(self) -> None:
        with io.open(self.config_path, "wb") as f:
            f.write(super().write())


class config_cry_file(config_cry, config_file):
    """don't use this for imported stuff its really unsafe"""

    def read(self, key: bytes) -> None:
        with io.open(self.config_path, "rb") as f:
            super().read(f.read(), key)

    def write(self, key: bytes) -> None:
        with io.open(self.config_path, "wb") as f:
            f.write(super().write(key))


class CM:
    __kwargs_default = {"save": True, "show_time": "%X", "pre_input_str": ">>",
                        "pre_output_str": "<< ", "log_path": os.path.join(os.getcwd(), "logs"),
                        "source_path": os.path.join(os.getcwd(), "source"), "quit_message": "",
                        "from_config": [], "config_path": os.path.join(os.getcwd(), "config.txt"),
                        "debug_mode": True, "make_files": False,
                        "dont_show": [], "dont_exec": []}
    __not_remove_func = ["show_all_func", "help", "info", "quit", "reread_config", "append_config",
                         "remove_from_config"]
    __no_from_config = ["from_config", "config_path"]

    def __init__(self, **kwargs):
        a = snn_grl.kwargs_handler(kwargs, self.__kwargs_default, True)
        self.config = config_file(a["config_path"])
        if a["from_config"]:
            self.config.read()
            for y in a["from_config"]:
                if y in self.__no_from_config:
                    raise ValueError(f"{y} arg can not be taken from a config file")
                a[y] = self.config[y]
                del self.config[y]
        else:
            if os.path.isfile(a["config_path"]):
                self.config.read()
            elif a["make_files"]:
                self.config.write()
        self.base_input_obj = input_M(disable_int_convert=True, disable_bool_convert=True, disable_None_convert=True,
                                      pre_input_str=a["pre_input_str"], show_time=a["show_time"], save=a["save"])
        self.base_output_obj = output_M(show_time=a["show_time"], pre_output_str=a["pre_output_str"], save=a["save"])
        self.is_running = False
        self.debug = a["debug_mode"]
        self.log_path = a["log_path"]
        self.source_path = a["source_path"]
        self.quit_message = a["quit_message"]
        self.bad_exit = True
        self.config_change = False
        self.source_change = False
        b = [y for y in dir(CM) if not (y in CM.__not_remove_func) and callable(getattr(CM, y))]  # :):
        self.fight_club_func = b + a["dont_show"]  # only for show_all_func
        self.dont_exec_func = b + a["dont_exec"]  # only for __run

    def on_close(self):
        pass

    def help(self):
        a = ["this file was created by Sinon and FF00FF",
             "if you have problems with it or you found bugs you can message us at discord or github",
             "", "P.S if you see this message the 'help' method was not overwritten",
             "(you can overwrite this to show your own text)"]
        self.base_output_obj.output("\n".join(a))

    def info(self):
        a = ["this file was created by Sinon and FF00FF",
             "if you have problems with it or you found bugs you can message us at discord or github",
             "", "P.S if you see this message the 'info' method was not overwritten ",
             "(you can overwrite this to show your own text)"]
        self.base_output_obj.output("\n".join(a))

    class ArgsPostProgressError(Exception):
        pass

    @final
    def error_message(self, a: Optional[str] = ""):
        list1 = [f"error: {a}"]
        if self.debug:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            list1 += [f"-- debug stuff: {str(exc_type)[8:-2]}: {exc_obj} --", "-" * 75
                      ] + [f"-- {str(y)[14:-1]} --" for y in traceback.extract_tb(exc_tb)]
        self.base_output_obj.output("\n".join(list1))

    @final
    def __on_close(self):
        if self.base_output_obj.save_IO:
            b = os.path.join(self.log_path, rf"clog_{datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}.txt")
            self.base_output_obj.output(rf"log will be saved at {b}")
            with io.open(b, "w") as f:
                f.write(self.base_output_obj.save())
        if self.config_change:
            self.base_output_obj.output(rf"config will be saved at {self.config.config_path}")
            self.config.write()
        if self.source_change:
            pass

    @final
    def start(self):
        self.is_running = True
        self.__run()

    @final
    def end(self):
        self.is_running = False

    @final
    def show_all_func(self, func_name: Optional[str] = None):
        if func_name is None:
            self.base_output_obj.output(r"-> " + "\n-> ".join([y for y in dir(self) if
                                                               (not (y in self.fight_club_func)) and callable(
                                                                   getattr(self, y))]))
        else:
            try:
                a = getattr(self, func_name)
                if func_name in self.fight_club_func:
                    raise AttributeError("sorry this func/attr can not be called")
                self.base_output_obj.output("doc:\n" + a.__doc__ + "\nargs:\n" + "\n".join(
                    [f"{y.name}: {y.annotation}" for y in inspect.signature(a).parameters.values()]))
            except AttributeError:
                self.error_message(f"no func with the name {func_name}")

    @final
    def change_config(self, key: str, value: Any):
        self.config_change = True
        self.config[key] = value

    @final
    def remove_from_config(self, key: str):
        self.config_change = True
        self.config.remove(key)

    @final
    def reread_config(self):
        try:
            self.config.read()
        except OSError:
            self.error_message(rf"the file {self.config.config_path} could not be found")

    @final
    def quit(self):
        if self.quit_message:
            self.base_output_obj.output(self.quit_message)
        sys.exit()

    @final
    def exit_clean_up(self):
        self.bad_exit = False
        self.on_close()
        self.__on_close()
        sys.exit()

    @final
    def fatal_error_cleanup(self):
        if self.bad_exit:
            self.debug = True
            self.error_message("fatal error:")
            self.exit_clean_up()

    @final
    def __run(self):
        while self.is_running:
            try:
                a = self.base_input_obj.input()
                if self.debug:
                    self.base_output_obj.output("\n".join(["-" * 50, "raw input:"] + a + ["-" * 50]))
                b = getattr(self, a[0])
                if not callable(b) or (a[0] in self.dont_exec_func):
                    self.base_output_obj.output("sorry this func/attr can not be called "
                                                "(call 'show_all_func' for a list of all callable funcs)")
                    continue
                try:
                    d = self.args_post_progress(a[1:], b)
                except CM.ArgsPostProgressError:
                    self.error_message("the types of the input is wrong")
                    continue
                if b(*d) and (r"->" in str(inspect.signature(b))):
                    self.base_output_obj.output("the func did not pass")
            except AttributeError:
                self.error_message(f"there is no func with the name '{a[0]}'")
            except TypeError as e:
                self.error_message(str(e))
            except (SystemExit, KeyboardInterrupt):
                self.exit_clean_up()

    @final
    def args_post_progress(self, a: List[str], b):
        # this is a really, really ugly func pls don't look
        def idk(y0, d0):
            if y0 == "None" and ("NoneType" in d0):
                return None
            elif y0.isnumeric() and ("int" in d0):
                return int(y0)
            elif y0[:2] == "b'" and y0[-1] == "'" and ("bytes" in d0):
                b0 = y0[2:-1].split(r"\x")
                return b''.join([bytes(b0[0], encoding="utf8")] + [int(y[:2], 16).to_bytes(1, "little") + bytes(
                    y[2:], encoding="utf8") for y in b0[1:]])
            elif (y0 in ["True", "False"]) and ("bool" in d0):
                return y0 == "True"
            elif "str" in d0 or d0 == ["inspect._empty"]:
                return y0
            else:
                raise CM.ArgsPostProgressError(f"arg {y0} can not be converted to one of these {d}")

        list1, g, d = [], inspect.signature(b).parameters, "NoneType"
        for iy, y in enumerate(g.values()):
            c = str(y.annotation)
            d = c.split("[", 1)[1][:-1].split(", ") if "typing.Union" in c else [c[8:-2]]
            try:
                yy = a[iy]
            except IndexError:
                if y.kind == y.VAR_POSITIONAL:
                    iy = len(a)
                    break
                yy = "None" if "NoneType" in d else ""
            list1.append(idk(yy, d))
        if len(g) < len(a):
            for y in a[iy + 1:]:
                list1.append(idk(y, d))
        return list1
