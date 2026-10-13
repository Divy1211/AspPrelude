from io import StringIO
from pathlib import Path
from contextlib import contextmanager


class XsWriter:
    def __init__(self, path: Path | str, indent_spaces: int = 4):
        self.path = path
        self.content = StringIO()
        self.indent = 0
        self.indent_spaces = indent_spaces

    @property
    def _indent_str(self) -> str:
        return ' ' * self.indent * self.indent_spaces

    def write(self, value: str):
        self.content.write(self._indent_str + value)

    def writeln(self, value: str = ""):
        self.write(value)
        self.content.write("\n")

    @contextmanager
    def indented(self):
        self.indent += 1
        yield
        self.indent -= 1

    @contextmanager
    def if_(self, condition: str):
        self.writeln(f"if ({condition}) {{")
        with self.indented():
            yield
        self.writeln(f"}}")

    @contextmanager
    def elif_(self, condition: str):
        self.writeln(f"else if ({condition}) {{")
        with self.indented():
            yield
        self.writeln(f"}}")

    @contextmanager
    def else_(self):
        self.writeln(f"else {{")
        with self.indented():
            yield
        self.writeln(f"}}")

    @contextmanager
    def while_(self, condition: str):
        self.writeln(f"while ({condition}) {{")
        with self.indented():
            yield
        self.writeln(f"}}")

    @contextmanager
    def switch(self, expr: str):
        self.writeln(f"switch ({expr}) {{")
        with self.indented():
            yield
        self.writeln(f"}}")

    @contextmanager
    def case_(self, expr: str):
        self.writeln(f"case {expr} : {{")
        with self.indented():
            yield
        self.writeln(f"}}")

    @contextmanager
    def default_(self):
        self.writeln(f"default : {{")
        with self.indented():
            yield
        self.writeln(f"}}")

    @contextmanager
    def for_(self, expr: str):
        self.writeln(f"for ({expr}) {{")
        with self.indented():
            yield
        self.writeln(f"}}")

    @contextmanager
    def mut_fn(self, rtype: str, name: str, params: list[str]):
        self.write(f"mutable ")
        with self.fn(rtype, name, params):
            yield

    @contextmanager
    def fn(self, rtype: str, name: str, params: list[str]):
        self.write(f"{rtype} {name}(")
        if len(params) == 0:
            self.writeln(")")
        else:
            one_liner = ", ".join(params)
            if len(one_liner) > 120-3:
                self.writeln()
                with self.indented():
                    for param in params:
                        self.writeln(f"{param},")
            else:
                self.write(one_liner)
            self.writeln(") {")

        self.indent += 1
        yield
        self.indent -= 1
        self.writeln(f"}}")

    def __call__(self, value: str = ""):
        self.writeln(value)

    def get_value(self) -> str:
        return self.content.getvalue()

    def flush(self):
        assert Path(self.path).exists(), f"path '{self.path}' does not exist"
        with open(self.path, "w") as file:
            file.write(self.content.getvalue())

def main():
    xs = XsWriter("")

    xs("extern const int a = 10;")
    xs()
    with xs.fn("void", "main", []):
        xs("int a = 10;")
        with xs.if_("a > 0"):
            xs("int b = 10;")

    print(xs.get_value())

if __name__ == "__main__":
    main()
