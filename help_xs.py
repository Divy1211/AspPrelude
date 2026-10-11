from AoE2ScenarioParser.datasets.players import PlayerId
from AoE2ScenarioParser.datasets.trigger_lists import PanelLocation
from AoE2ScenarioParser.objects.data_objects.trigger import Trigger


class XsFn:
    __id = 0

    def __init__(self, stmt_expr: str):
        self.stmt_expr = stmt_expr
        self.type = "void"
        self._name = "eff"

        self.id = XsFn.__id
        XsFn.__id += 1

    def void(self):
        self.type = "void"
        self._name = "eff"
        return self

    def bool(self):
        self.type = "bool"
        self._name = "cnd"
        return self

    def rule(self):
        self.type = "rule"
        return self

    def __str__(self) -> str:
        if self.type == "bool" and "return" not in self.stmt_expr:
            return f"""{self.type} {self._name}Fn{self.id}() {{\n    return ({self.stmt_expr.removesuffix(';')});\n}}"""
        if self.type == "rule":
            return f"""rule rule{self.id}\n    minInterval 1\n{{\n    {self.stmt_expr.removesuffix(';')};\n}}"""
        return f"""{self.type} {self._name}Fn{self.id}() {{\n    {self.stmt_expr.removesuffix(';')};\n}}"""

    def no_ret(self) -> str:
        return f"""{self.type} {self._name}Fn{self.id}() {{\n    {self.stmt_expr.removesuffix(';')};\n}}"""

    def no_scolon(self) -> str:
        return f"""{self.type} {self._name}Fn{self.id}() {{\n    {self.stmt_expr}\n}}"""

    @property
    def name(self) -> str:
        return f"{self._name}Fn{self.id}"

def xs_vec(x: float | str, y: float | str, z: float | str = -1) -> str:
    if isinstance(x, float) and isinstance(y, float) and isinstance(z, float):
        return f"vector({x}, {y}, {z})"
    return f"xsVectorSet({x}, {y}, {z})"

def str_arg(v: str) -> str:
    return f'"{v!r}"'.replace("'", "")

def bool_arg(v: bool) -> str:
    return 'true' if v else 'false'

def xs_display_instructions(
    trigger: Trigger,
    object_list_unit_id: int = -1,
    source_player: int = PlayerId.ONE,
    display_time: int = 10,
    instruction_panel_position: int = PanelLocation.TOP,
    message: str = "",
    sound_name: str = "",
    use_tag_color_for_icon: bool = False,
    play_notif_sound: bool = True,
    specific_player_id: int = -1,
):
    trigger.new_effect.script_call(
        message = str(XsFn(f"xsDisplayInstructions({str_arg(message)}, {display_time}, {source_player}, {object_list_unit_id}, {instruction_panel_position}, {bool_arg(use_tag_color_for_icon)}, {bool_arg(play_notif_sound)}, {str_arg(sound_name)}, {specific_player_id})")),
    )

def is_in_editor(trigger: Trigger):
    trigger.new_condition.script_call(
        xs_function = str(XsFn(f'xsGetMapName() == "default0"').bool()),
    )
