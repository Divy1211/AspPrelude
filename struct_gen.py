from pathlib import Path
from typing import get_type_hints, Type, get_origin, get_args, Annotated


def get_type_default(type_: Type) -> str:
    if type_ is int:
        return "-1"
    if type_ is float:
        return "-1.0"
    if type_ is bool:
        return "false"
    if type_ is str:
        return '""'
    if get_origin(type_) is list or getattr(type_, "__has_xs_struct__", False):
        return "-1"
    raise TypeError(f"Type {type_} is not supported")

def get_type_name(type_: Type, array: bool = False) -> str:
    if type_ is int:
        return "Int" if array else "int"
    if type_ is float:
        return "Float" if array else "float"
    if type_ is bool:
        return "Bool" if array else "bool"
    if type_ is str:
        return "String" if array else "string"
    if get_origin(type_) is list or getattr(type_, "__has_xs_struct__", False):
        return "Int" if array else "int"
    raise TypeError(f"Type {type_} is not supported")

def def_list_type(
    camel_case_name: str,
    attr_array_name: str,
    type_: Type,
    str_repr: list[str],
    readers: list[str],
    writers: list[str],
    includes: set[str],
    depth: int = 0,
):
    inner_obj = "self" if depth == 0 else f"{attr_array_name}_i{depth - 1}"

    if get_origin(type_) is list:
        inner, *_ = get_args(type_)
        str_repr.append(' ' * (4*depth) + f'int {camel_case_name} = xsArrayGetInt(xsArrayGetInt({attr_array_name}, {inner_obj}));')
        str_repr.append(' ' * (4*depth) + f"int {camel_case_name}_size{depth} = xsArrayGetSize({camel_case_name});")
        str_repr.append(' ' * (4*depth) + f'string {camel_case_name}_str = "[";')
        str_repr.append(' ' * (4*depth) + f"for({camel_case_name}_i{depth} = 0; < {camel_case_name}_size{depth}) {{")

        readers.append(' ' * (4*depth) + f"int {camel_case_name}_size{depth} = xsReadInt();")
        readers.append(' ' * (4*depth) + f"int {camel_case_name} = xsArrayCreateInt({camel_case_name}_size{depth});")
        readers.append(' ' * (4*depth) + f"for({camel_case_name}_i{depth} = 0; < {camel_case_name}_size{depth}) {{")

        writers.append(' ' * (4*depth) + f'int {camel_case_name} = xsArrayGetInt(xsArrayGetInt({attr_array_name}, {inner_obj}));')
        writers.append(' ' * (4*depth) + f"int {camel_case_name}_size{depth} = xsArrayGetSize({camel_case_name});")
        writers.append(' ' * (4*depth) + f"xsWriteInt({camel_case_name}_size{depth});")
        writers.append(' ' * (4*depth) + f"for({camel_case_name}_i{depth} = 0; < {camel_case_name}_size{depth}) {{")

        def_list_type(camel_case_name + f"{depth + 1}", camel_case_name, inner, str_repr, readers, writers, includes, depth + 1)

        str_repr.append(' ' * (4*depth) + f"    {camel_case_name}_str = {camel_case_name}_str + {camel_case_name}{depth + 1}_str;")
        str_repr.append(' ' * (4*depth) + f"    if({camel_case_name}_i{depth} < {camel_case_name}_size{depth}) {{")
        str_repr.append(' ' * (4*depth) + f'        {camel_case_name}_str = {camel_case_name}_str + ", ";')
        str_repr.append(' ' * (4*depth) + f"    }}")
        str_repr.append(' ' * (4*depth) + f"}}")
        str_repr.append(' ' * (4*depth) + f'{camel_case_name}_str = "]";')

        readers.append(' ' * (4*depth) + f"    xsArraySetInt({camel_case_name}, {camel_case_name}_i{depth}, {camel_case_name}{depth + 1});")
        readers.append(' ' * (4*depth) + f"}}")

        writers.append(' ' * (4*depth) + f"}}")
        return
    if getattr(type_, "__has_xs_struct__", False):
        inner_name = type_.__name__
        includes.add(f"{inner_name}.h.xs")
        str_repr.append(' ' * (4*depth) + f"int {camel_case_name} = xsArrayGetInt({attr_array_name}, {inner_obj});")
        str_repr.append(' ' * (4*depth) + f"int {camel_case_name}_size{depth} = xsArrayGetSize({camel_case_name});")
        str_repr.append(' ' * (4*depth) + f'string {camel_case_name}_str = "[";')
        str_repr.append(' ' * (4*depth) + f"for({camel_case_name}_i{depth} = 0; < {camel_case_name}_size{depth}) {{")
        str_repr.append(' ' * (4*depth) + f"    {camel_case_name}_str = {camel_case_name}_str + {inner_name}_show(xsArrayGetInt({camel_case_name}, {camel_case_name}_i{depth}));")
        str_repr.append(' ' * (4*depth) + f"    if({camel_case_name}_i{depth} < {camel_case_name}_size{depth}) {{")
        str_repr.append(' ' * (4*depth) + f'        {camel_case_name}_str = {camel_case_name}_str + ", ";')
        str_repr.append(' ' * (4*depth) + f"    }}")
        str_repr.append(' ' * (4*depth) + f"}}")
        str_repr.append(' ' * (4*depth) + f'{camel_case_name}_str = "]";')

        readers.append(' ' * (4*depth) + f"int {camel_case_name}_size{depth} = xsReadInt();")
        readers.append(' ' * (4*depth) + f"int {camel_case_name} = xsArrayCreateInt({camel_case_name}_size{depth});")
        readers.append(' ' * (4*depth) + f"for({camel_case_name}_i{depth} = 0; < {camel_case_name}_size{depth}) {{")
        readers.append(' ' * (4*depth) + f"    xsArraySetInt({camel_case_name}, {camel_case_name}_i{depth}, {inner_name}_read(version));")
        readers.append(' ' * (4*depth) + f"}}")

        writers.append(' ' * (4*depth) + f"int {camel_case_name} = xsArrayGetInt({attr_array_name}, {inner_obj});")
        writers.append(' ' * (4*depth) + f"int {camel_case_name}_size{depth} = xsArrayGetSize({camel_case_name});")
        writers.append(' ' * (4*depth) + f"xsWriteInt({camel_case_name}_size{depth});")
        writers.append(' ' * (4*depth) + f"for({camel_case_name}_i{depth} = 0; < {camel_case_name}_size{depth}) {{")
        writers.append(' ' * (4*depth) + f"    {inner_name}_write(xsArrayGetInt({camel_case_name}, {camel_case_name}_i{depth}));")
        writers.append(' ' * (4*depth) + f"}}")
        return
    if type_ is not int and type_ is not float and type_ is not bool and type_ is not str:
        raise TypeError(f"Type {type_} is not supported")

    includes.add("ArrayUnits.xs")
    str_repr.append(' ' * (4*depth) + f"string {camel_case_name}_str = ArrayUtils_showArray{get_type_name(type_, True)}(xsArrayGetInt({attr_array_name}, {inner_obj}));")
    readers.append(' ' * (4*depth) + f"int {camel_case_name} = ArrayUtils_readArray{get_type_name(type_, True)}(version);")
    writers.append(' ' * (4*depth) + f"ArrayUtils_writeArray{get_type_name(type_, True)}(xsArrayGetInt({attr_array_name}, {inner_obj}));")

def xs_struct(mod_dir: str | Path, *, sub_dir: str = None, debug: bool = False):
    def gen_xs_struct(cls: Type):
        cls.__has_xs_struct__ = True
        hints = get_type_hints(cls, include_extras = True)

        extras = {}
        names = []
        array_names = []
        arrays = []
        arrays_init = []
        arrays_resize = []
        str_repr = []
        cons_inst = []
        cons_params = []
        getter_setter = []
        readers = []
        writers = []
        defaults = []

        includes = set()

        cls_name = cls.__name__
        for name, type_hint in hints.items():
            min_ver = None
            max_ver = None
            if get_origin(type_hint) is Annotated:
                try:
                    type_hint, min_ver = get_args(type_hint)
                except ValueError:
                    type_hint, min_ver, max_ver = get_args(type_hint)

            camel_case_name = "".join([word.title() if i > 0 else word for i, word in enumerate(name.split("_"))])
            camel_case_name = ("_" if name.startswith("_") else "") + camel_case_name + ("_" if name.endswith("_") else "")
            names.append(camel_case_name)
            array_names.append(camel_case_name)
            attr_array_name = f"_{camel_case_name.removesuffix('_')}"

            readers_index = -1
            if min_ver is not None:
                if max_ver is not None:
                    readers.append(f"if(version >= {min_ver} && version <= {max_ver}) {{")
                else:
                    readers.append(f"if(version >= {min_ver}) {{")
                readers_index = len(readers)

            writers_index = -1
            str_repr_index = -1
            if max_ver is not None:
                writers_index = len(writers)
                str_repr_index = len(str_repr)

            if get_origin(type_hint) is list:
                inner, *_ = get_args(type_hint)
                extras[camel_case_name] = "_str"
                def_list_type(camel_case_name, attr_array_name, inner, str_repr, readers, writers, includes)
                if min_ver is not None and max_ver is None:
                    defaults.append(f"    {camel_case_name} = xsArrayCreate{get_type_name(type_hint, True)}(0);")
            elif getattr(type_hint, "__has_xs_struct__", False):
                inner_name = type_hint.__name__
                includes.add(f"{inner_name}.h.xs")
                str_repr.append(f'string {camel_case_name} = "" + {inner_name}_show(xsArrayGetInt({attr_array_name}, self));')
                readers.append(f"int {camel_case_name} = {inner_name}_read(version);")
                writers.append(f"{inner_name}_write(xsArrayGetInt({attr_array_name}, self));")
                if min_ver is not None and max_ver is None:
                    defaults.append(f"    {camel_case_name} = {inner_name}_new();")
            else:
                str_repr.append(f'string {camel_case_name} = "" + xsArrayGet{get_type_name(type_hint, True)}({attr_array_name}, self);')

                io_type = get_type_name(type_hint, True)
                extra = ""
                if io_type == "Bool":
                    io_type = "Int"
                    extra = " != 0"
                if name == "version":
                    readers.append(f"version = xsReadInt();")
                else:
                    readers.append(f"{get_type_name(type_hint)} {camel_case_name} = xsRead{io_type}(){extra};")
                writers.append(f"xsWrite{io_type}(xsArrayGet{get_type_name(type_hint, True)}({attr_array_name}, self));")
                if min_ver is not None and max_ver is None:
                    defaults.append(f"    {camel_case_name} = {get_type_default(type_hint)};")

            if min_ver is not None:
                for i, line in enumerate(readers[readers_index:], start = readers_index):
                    readers[i] = f"    {line}"
                if max_ver is None:
                    readers.append(f"}} else {{")
                    readers.extend(defaults)
                    defaults.clear()
                readers.append(f"}}")

            if max_ver is not None:
                del writers[writers_index:]
                del str_repr[str_repr_index:]
                names.pop()
                array_names.pop()
                continue

            arrays.append(f"int {attr_array_name} = -1;")
            arrays_init.append(f"{attr_array_name} = xsArrayCreate{get_type_name(type_hint, True)}(0);")
            arrays_resize.append(f"xsArrayResize{get_type_name(type_hint, True)}({attr_array_name}, {cls_name}_size);")

            if name.startswith("_"):
                continue

            if name == "version":
                ver = getattr(cls, "__ver__")
                if not isinstance(ver, int):
                    raise ValueError(f"struct default version must be an int")
                cons_inst.append(f"xsArraySet{get_type_name(type_hint, True)}({attr_array_name}, size, {ver});")
                continue

            if get_origin(type_hint) is list:
                inner, *_ = get_args(type_hint)
                cons_inst.append(f"if({camel_case_name} == -1) {{")
                cons_inst.append(f"    {camel_case_name} = xsArrayCreate{get_type_name(inner, True)}(0);")
                cons_inst.append(f"}}")
            elif getattr(type_hint, "__has_xs_struct__", False):
                inner_name = type_hint.__name__
                cons_inst.append(f"if({camel_case_name} == -1) {{")
                cons_inst.append(f"    {camel_case_name} = {inner_name}_new();")
                cons_inst.append(f"}}")

            cons_inst.append(f"xsArraySet{get_type_name(type_hint, True)}({attr_array_name}, size, {camel_case_name});")
            if (default_value := getattr(cls, name, None)) is not None:
                try:
                    # this code is cursed, but I have no idea if there's a better way to do this...
                    from bfp_rs import Retriever, BaseStruct
                    if isinstance(default_value, Retriever):
                        inst = cls()
                        default_value = getattr(inst, name)
                        # Apparently I don't expose a bfp-rs list type...
                        if isinstance(default_value, BaseStruct) or hasattr(default_value, "append"):
                            default_value = -1
                        if isinstance(default_value, bool):
                            default_value = "true" if default_value else "false"
                except ImportError:
                    Retriever = None
                    BaseStruct = None
            else:
                default_value = get_type_default(type_hint)
            cons_params.append(f"{get_type_name(type_hint)} {camel_case_name} = {default_value}")

            getter_setter.append("\n".join([
                f"mutable {get_type_name(type_hint)} {cls_name}_get{camel_case_name.removesuffix('_').title()}(int self = -1) {{",
                f"    return (xsArrayGet{get_type_name(type_hint, True)}({attr_array_name}, self));",
                f"}}",
                f""
                f"mutable void {cls_name}_set{camel_case_name.removesuffix('_').title()}(int self = -1, {get_type_name(type_hint)} value = {get_type_default(type_hint)}) {{",
                f"    xsArraySet{get_type_name(type_hint, True)}({attr_array_name}, self, value);",
                f"}}",
            ]))

        dir_path = Path(mod_dir) / "resources" / "_common" / "xs"
        inc_sdir = ""
        if sub_dir is not None:
            dir_path /= sub_dir
            inc_sdir = f"{sub_dir}\\"
        dir_path.mkdir(parents = True, exist_ok = True)
        file_path = dir_path / f"{cls_name}.h.xs"
        with open(file_path, "w", encoding = "utf-8") as f:

            if len(includes) > 0:
                f.write("\n".join([f'include "{inc_sdir}{i}";' for i in includes]) + "\n")
                f.write("\n")
            f.write("\n".join(arrays) + "\n")
            f.write("\n")
            f.write(f"bool {cls_name}_initDone = false;\n")
            f.write(f"mutable void {cls_name}_init() {{\n")
            f.write(f"    {cls_name}_initDone = true;\n")
            f.write("    " + "\n    ".join(arrays_init) + "\n")
            f.write(f"}}\n")
            f.write("\n")
            f.write(f"int {cls_name}_size = 0;\n")
            f.write(f"mutable int {cls_name}_new(\n    {",\n    ".join(cons_params)}\n) {{\n")
            f.write(f"    if({cls_name}_initDone == false) {{\n")
            f.write(f"        {cls_name}_init();\n")
            f.write(f"    }}\n")
            f.write(f"    int size = {cls_name}_size;\n")
            f.write(f"    {cls_name}_size++;\n")
            f.write("    " + "\n    ".join(arrays_resize) + "\n")
            f.write("\n")
            f.write("    " + "\n    ".join(cons_inst) + "\n")
            f.write(f"    return ({cls_name}_size-1);\n")
            f.write(f"}}\n")
            f.write("\n")
            f.write("\n".join(getter_setter) + "\n")
            f.write("\n")
            f.write(f"mutable int {cls_name}_read(int version = -1) {{\n")
            f.write("    " + "\n    ".join(readers) + "\n")
            f.write(f'    return ({cls_name}_new(\n')
            f.write(f"        " + "\n        ".join([f'{n},' for n in names if n != "version"])+"\n")
            f.write(f'    ));\n')
            f.write(f"}}\n")
            f.write("\n")
            f.write(f"mutable void {cls_name}_write(int self = -1) {{\n")
            f.write("    " + "\n    ".join(writers) + "\n")
            f.write(f"}}\n")
            f.write("\n")
            f.write(f"mutable string {cls_name}_show(int self = -1) {{\n")
            f.write(f"    " + "\n    ".join(str_repr) + "\n")
            f.write(f'    return (\n')
            f.write(f'        "{cls_name}("\n')
            f.write(f"        + " + "\n        + ".join([f'"{n} = " + {n}{extras.get(n, "")} + ", "' for n in names])+"\n")
            f.write(f'        + ")"\n')
            f.write(f'    );\n')
            f.write(f"}}\n")

        return cls
    return gen_xs_struct
