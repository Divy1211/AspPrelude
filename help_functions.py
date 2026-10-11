import json
import sys
from importlib.metadata import version
from itertools import product
from random import randrange
from typing import Iterator

import regex

from portalocker import Lock, LockFlags

from prelude.parser_imports import *
from prelude.common_vars import GameInfo
from prelude.help_xs import XsFn

_condition_grammar = {
    "1": "OBJECT1 not AREA",
    "2": "OBJECT1 not near OBJECT2",
    "3": "has at least",
    "4": "has at most AREA",
    "5": "has at least AREA",
    "6": "OBJECT1 has not been destroyed",
    "7": "has not captured OBJECT1",
    "8": "has at least",
    "9": "has not researched",
    "10": "VALUE seconds have not passed",
    "11": "OBJECT1 is not selected",
    "12": "ai signal VALUE is not detected",
    "13": "has not been defeated",
    "14": "OBJECT1 is not targeting OBJECT2",
    "15": "OBJECT1 is visible",
    "16": "OBJECT1 is not visible",
    "17": "is not researching",
    "18": "OBJECT1 has at least VALUE objects garrisoned",
    "19": "difficulty level is not",
    "20": "with a probability of VALUE%",
    "21": "TECH_STATE",
    "22": "is not",
    "23": "OBJECT1 has exactly VALUE HP",
    "24": "is not DIPLO_STATE with",
    "25": "XS function returns true",
    "26": "cannot see OBJECT1",
    "27": "has not selected OBJECT1",
    "28": "OBJECT1 is not ACTION",
    "29": "or",
    "30": "ai signal VALUE is not detected"
}

_object_state_grammar = {
    "0": "that is a foundationPLURAL",
    "1": "that is almost alive",
    "2": "that is alive",
    "3": "that is a resourcePLURAL",
    "4": "that is dying",
    "5": "that is dead",
    "6": "that is undead",
    "7": "that is removed"
}

_tech_state_grammar = {
    "0": "is not ready to research",
    "1": "is not ready to research",
    "2": "is not researching",
    "3": "has not researched",
    "4": "has not queued",
    "-1": "is not able to research"
}

_diplo_state_grammar = {
    "0": "allied with",
    "1": "enemies with",
    "3": "neutral with",
}

_comparison_grammar = {
    "0": "equal to",
    "1": "less than",
    "2": "greater than",
    "3": "less than or equal to",
    "4": "greater than or equal to"
}

_action_grammar = {
    "0": "doing anything",
    "1": "attacking OBJECT2",
    "3": "building OBJECT2",
    "5": "converting OBJECT2",
    "2": "defending OBJECT2",
    "18": "entering OBJECT2",
    "17": "evading OBJECT2",
    "6": "exploring",
    "13": "following OBJECT2",
    "10": "gathering from OBJECT2",
    "4": "healing OBJECT2",
    "14": "hunting OBJECT2",
    "24": "idle",
    "11": "moving",
    "12": "patrolling",
    "23": "going to pick up OBJECT2",
    "19": "repairing OBJECT2",
    "21": "researching",
    "9": "retreating from OBJECT2",
    "8": "running away from OBJECT2",
    "7": "stopping",
    "16": "trading with OBJECT2",
    "20": "training",
    "15": "transporting OBJECT2",
    "22": "unloading OBJECT2"
}


def make_unreachable(trigger: Trigger):
    trigger.new_condition.player_defeated(
        source_player = PlayerId.GAIA,
    )

def lerp(area: Area, tx: float = 0.5, ty: float = 0.5, as_int: bool = False) -> Tile:
    tile = Tile(area.corner2.x * tx + area.corner1.x * (1-tx), area.corner2.y * ty + area.corner1.y * (1-ty))
    if as_int:
        return Tile(int(tile.x), int(tile.y))
    return tile

def log[T](value: T) -> T:
    print(value)
    return value

def players_i(scx: AoE2DEScenario, *, gaia: bool = False) -> range:
    num_players = scx.player_manager.active_players
    return range(0 if gaia else 1, num_players + 1)

def players(scx: AoE2DEScenario, *, gaia: bool = False) -> Iterator[Player]:
    num_players = scx.player_manager.active_players
    return map(lambda player: scx.player_manager.players[player], range(0 if gaia else 1, num_players + 1))

def tiles(scx: AoE2DEScenario, *, step: int = 1) -> product:
    width = scx.map_manager.map_width
    height = scx.map_manager.map_height
    return product(range(0, width, step), range(0, height, step))

def player_count(scx: AoE2DEScenario) -> int:
    return scx.player_manager.active_players

def disable_carto(scx: AoE2DEScenario):
    for player in scx.player_manager.players:
        player.disabled_techs = [TechInfo.CARTOGRAPHY.ID]

def random_units_spawn(scx: AoE2DEScenario, *, area_size: int = 1, player: PlayerId = PlayerId.GAIA):
    tm = scx.trigger_manager

    deactivate = tm.add_trigger("Deactivate Spawn MMR", enabled = False)
    activate = tm.add_trigger("Activate Spawn MMR", enabled = False)
    spawn_chance_var = tm.add_variable("Spawn Chance")

    activate.new_effect.activate_trigger(
        trigger_id = deactivate.trigger_id,
    )
    deactivate.new_effect.change_variable(
        quantity=-2,
        operation=Operation.SET,
        variable=spawn_chance_var.variable_id,
    )

    def gen_spawn_trs():
        tm.add_trigger("==== Spawners ====", enabled = False)
        for x, y in tiles(scx, step = area_size):
            spawn = tm.add_trigger(f"Spawn MMR ({x}, {y})", enabled = False)
            spawn.new_condition.script_call(
                xs_function=str(XsFn(
                    f"xsGetRandomNumberMax(100) < xsTriggerVariable({spawn_chance_var.variable_id})"
                ).bool()),
            )
            spawn.new_effect.create_object(
                object_list_unit_id=OtherInfo.BARRELS.ID,
                source_player=player,
                location_x=x,
                location_y=y,
                facet = randrange(16)
            )
            activate.new_effect.activate_trigger(
                trigger_id=spawn.trigger_id,
            )
            deactivate.new_effect.deactivate_trigger(
                trigger_id=spawn.trigger_id,
            )
        deactivate.new_effect.deactivate_trigger(
            trigger_id = deactivate.trigger_id,
        )

    return activate, spawn_chance_var, gen_spawn_trs

def add_credits_header(name: str, map_version: str, scx: AoE2DEScenario) -> str:
    tm = scx.trigger_manager
    triggers = tm.triggers
    tm.triggers = []
    build_counts_path = r"C:\Users\Divy\PycharmProjects\ParserMaps\build_counts.json"
    with open(build_counts_path) as file:
        build_counts = json.load(file)

    build_counts.setdefault(name, 0)
    build_counts[name] += 1

    tm.add_trigger("")
    tm.add_trigger("")
    tm.add_trigger("")
    tm.add_trigger(f"       Map By Alian713 (v{map_version}.{build_counts[name]})")
    tm.add_trigger(f" Made Using AoE2ScenarioParser v{version('AoE2ScenarioParser')}")
    tm.add_trigger(" AoE2ScenarioParser by MrKirby:")
    tm.add_trigger("https://github.com/KSneijders/AoE2ScenarioParser")
    tm.add_trigger("")
    tm.add_trigger("")
    tm.add_trigger("")

    with Lock(build_counts_path, "r+", flags = LockFlags.EXCLUSIVE) as file:
        json.dump(build_counts, file, indent = 4)

    # fix the (de)activate effect trigger refs
    for trigger in triggers:
        trigger.trigger_id += len(tm.triggers)
        for effect in trigger.effects:
            if effect.effect_type in [EffectId.ACTIVATE_TRIGGER, EffectId.DEACTIVATE_TRIGGER]:
                effect.trigger_id += len(tm.triggers)

    tm.triggers.extend(triggers)

    return f"{map_version}.{build_counts[name]}"

def regi_nomad_res(scx: AoE2DEScenario):
    tm = scx.trigger_manager
    res = tm.add_trigger("==== Regi Res ====", enabled = False)

    res.new_effect.script_call(
        message= "\n".join([
            f"rule regiRes",
            f"{{",
            f"    for(player = 1; <= xsGetNumPlayers()) {{",
            f"        int count = xsGetObjectCount(player, {UnitInfo.KING.ID});",
            f"        if(count > 0) {{",
            f"            xsSetPlayerAttribute(player, cAttributeFood, xsPlayerAttribute(player, cAttributeFood) + 300);",
            f"            xsSetPlayerAttribute(player, cAttributeWood, xsPlayerAttribute(player, cAttributeWood) + 300);",
            f"            xsSetPlayerAttribute(player, cAttributeGold, xsPlayerAttribute(player, cAttributeGold) - 100);",
            f"            xsSetPlayerAttribute(player, cAttributeStone, xsPlayerAttribute(player, cAttributeStone) - 50);",
            f"        }}",
            f"        count = xsGetObjectCount(player, {BuildingInfo.TOWN_CENTER.ID});",
            f"        if(count == 0) {{",
            f"            xsSetPlayerAttribute(player, cAttributeWood, xsPlayerAttribute(player, cAttributeWood) + 275);",
            f"            xsSetPlayerAttribute(player, cAttributeStone, xsPlayerAttribute(player, cAttributeStone) + 100);",
            f"        }}",
            f"    }}",
            f"    xsDisableSelf();",
            f"}}",
        ]),
    )

def fix_scouts(scx: AoE2DEScenario):
    tm = scx.trigger_manager
    tm.add_trigger("==== Scout Fix ====", enabled = False)

    NUM_PLAYERS = scx.player_manager.active_players
    for player in range(1, NUM_PLAYERS + 1):
        trigger = tm.add_trigger(f"Give Eagle p({int(player)})")
        for civ in GameInfo.MESO_CIVS:
            trigger.new_condition.research_technology(
                source_player=player,
                technology=civ.ID
            )
            if civ != GameInfo.MESO_CIVS[-1]:
                trigger.new_condition.or_()
        trigger.new_effect.replace_object(
            object_list_unit_id=UnitInfo.SCOUT_CAVALRY.ID,
            source_player=player,
            target_player=player,
            object_list_unit_id_2=UnitInfo.EAGLE_SCOUT.ID
        )
        trigger.new_effect.replace_object(
            object_list_unit_id = UnitInfo.CAMEL_SCOUT.ID,
            source_player = player,
            target_player = player,
            object_list_unit_id_2 = UnitInfo.EAGLE_SCOUT.ID
        )
        trigger.new_effect.replace_object(
            object_list_unit_id = UnitInfo.CHAMPI_SCOUT.ID,
            source_player = player,
            target_player = player,
            object_list_unit_id_2 = UnitInfo.EAGLE_SCOUT.ID
        )

    for player in range(1, NUM_PLAYERS + 1):
        trigger = tm.add_trigger(f"Give Scout (p{player})", execute_on_load = True)
        for civ in GameInfo.MESO_CIVS + GameInfo.LATAM_CIVS:
            trigger.new_condition.research_technology(
                source_player=player,
                technology=civ.ID,
                inverted = True
            )
        trigger.new_condition.research_technology(
            source_player = player,
            technology = TechInfo.GURJARAS.ID,
            inverted = True
        )
        trigger.new_effect.replace_object(
            object_list_unit_id=UnitInfo.EAGLE_SCOUT.ID,
            source_player=player,
            target_player=player,
            object_list_unit_id_2=UnitInfo.SCOUT_CAVALRY.ID
        )
        trigger.new_effect.replace_object(
            object_list_unit_id=UnitInfo.CAMEL_SCOUT.ID,
            source_player=player,
            target_player=player,
            object_list_unit_id_2=UnitInfo.SCOUT_CAVALRY.ID
        )
        trigger.new_effect.replace_object(
            object_list_unit_id = UnitInfo.CHAMPI_SCOUT.ID,
            source_player = player,
            target_player = player,
            object_list_unit_id_2 = UnitInfo.SCOUT_CAVALRY.ID
        )

    for player in range(1, NUM_PLAYERS + 1):
        trigger = tm.add_trigger(f"Give Camel Scout (p{player})", execute_on_load = True)
        trigger.new_condition.research_technology(
            source_player = player,
            technology = TechInfo.GURJARAS.ID,
        )
        trigger.new_effect.replace_object(
            object_list_unit_id=UnitInfo.SCOUT_CAVALRY.ID,
            source_player=player,
            target_player=player,
            object_list_unit_id_2=UnitInfo.CAMEL_SCOUT.ID
        )
        trigger.new_effect.replace_object(
            object_list_unit_id=UnitInfo.EAGLE_SCOUT.ID,
            source_player=player,
            target_player=player,
            object_list_unit_id_2=UnitInfo.CAMEL_SCOUT.ID
        )
        trigger.new_effect.replace_object(
            object_list_unit_id = UnitInfo.CHAMPI_SCOUT.ID,
            source_player = player,
            target_player = player,
            object_list_unit_id_2 = UnitInfo.CAMEL_SCOUT.ID
        )

    for player in range(1, NUM_PLAYERS + 1):
        trigger = tm.add_trigger(f"Give Champi Scout (p{player})", execute_on_load = True)
        for civ in GameInfo.LATAM_CIVS:
            trigger.new_condition.research_technology(
                source_player = player,
                technology = civ.ID
            )
            if civ != GameInfo.LATAM_CIVS[-1]:
                trigger.new_condition.or_()
        trigger.new_effect.replace_object(
            object_list_unit_id=UnitInfo.SCOUT_CAVALRY.ID,
            source_player=player,
            target_player=player,
            object_list_unit_id_2=UnitInfo.CHAMPI_SCOUT.ID
        )
        trigger.new_effect.replace_object(
            object_list_unit_id=UnitInfo.EAGLE_SCOUT.ID,
            source_player=player,
            target_player=player,
            object_list_unit_id_2=UnitInfo.CHAMPI_SCOUT.ID
        )
        trigger.new_effect.replace_object(
            object_list_unit_id = UnitInfo.CAMEL_SCOUT.ID,
            source_player = player,
            target_player = player,
            object_list_unit_id_2=UnitInfo.CHAMPI_SCOUT.ID
        )


def add_civ_bonuses(scx: AoE2DEScenario):
    tm = scx.trigger_manager
    NUM_PLAYERS = scx.player_manager.active_players
    for player in range(1, NUM_PLAYERS + 1):
        trigger = tm.add_trigger(f"Sicilian Bonus (p{player})")
        trigger.new_condition.research_technology(
            source_player=player,
            technology=TechInfo.SICILIANS.ID
        )
        trigger.new_effect.modify_resource(
            source_player=player,
            quantity=100,
            tribute_list=ResourceId.STONE_STORAGE,
            operation=Operation.ADD
        )
    for player in range(1, NUM_PLAYERS + 1):
        trigger = tm.add_trigger(f"Chinese Bonus (p{player})")
        trigger.new_condition.research_technology(
            source_player=player,
            technology=TechInfo.CHINESE.ID
        )
        trigger.new_effect.modify_resource(
            source_player=player,
            quantity=50,
            tribute_list=ResourceId.WOOD_STORAGE,
            operation=Operation.SUBTRACT
        )
        trigger.new_effect.modify_resource(
            source_player=player,
            quantity=200,
            tribute_list=ResourceId.FOOD_STORAGE,
            operation=Operation.SUBTRACT
        )

    for player in range(1, NUM_PLAYERS + 1):
        trigger = tm.add_trigger(f"Lithuanian Bonus (p{player})")
        trigger.new_condition.research_technology(
            source_player=player,
            technology=TechInfo.LITHUANIANS.ID
        )
        trigger.new_effect.modify_resource(
            source_player=player,
            quantity=150,
            tribute_list=ResourceId.FOOD_STORAGE,
            operation=Operation.ADD
        )

    for player in range(1, NUM_PLAYERS + 1):
        trigger = tm.add_trigger(f"Hun Bonus (p{player})")
        trigger.new_condition.research_technology(
            source_player=player,
            technology=TechInfo.HUNS.ID
        )
        trigger.new_effect.modify_resource(
            source_player=player,
            quantity=100,
            tribute_list=ResourceId.WOOD_STORAGE,
            operation=Operation.SUBTRACT
        )

    for player in range(1, NUM_PLAYERS + 1):
        trigger = tm.add_trigger(f"Mayan Bonus (p{player})")
        trigger.new_condition.research_technology(
            source_player=player,
            technology=TechInfo.MAYANS.ID
        )
        trigger.new_effect.modify_resource(
            source_player=player,
            quantity=50,
            tribute_list=ResourceId.FOOD_STORAGE,
            operation=Operation.SUBTRACT
        )

    for player in range(1, NUM_PLAYERS + 1):
        trigger = tm.add_trigger(f"Persian Bonus (p{player})")
        trigger.new_condition.research_technology(
            source_player=player,
            technology=TechInfo.PERSIANS.ID
        )
        trigger.new_effect.modify_resource(
            source_player=player,
            quantity=50,
            tribute_list=ResourceId.FOOD_STORAGE,
            operation=Operation.ADD
        )
        trigger.new_effect.modify_resource(
            source_player=player,
            quantity=50,
            tribute_list=ResourceId.FOOD_STORAGE,
            operation=Operation.ADD
        )


def handle_chinese(NUM_PLAYERS, tm):
    for player in range(1, NUM_PLAYERS + 1):
        trigger = tm.add_trigger(f"if training villagers (p{player})")
        trigger.new_condition.timer(
            timer=2,
            inverted=True
        )
        trigger.new_condition.research_technology(
            source_player=player,
            technology=TechInfo.CHINESE.ID
        )
        trigger.new_condition.accumulate_attribute(
            attribute=ResourceId.TRAINING_COUNT,
            quantity=1,
            source_player=player
        )
        trigger.new_effect.change_ownership(
            object_list_unit_id=BuildingInfo.TOWN_CENTER.ID,
            source_player=player,
            target_player=PlayerId.GAIA,
        )
        trigger.new_effect.change_ownership(
            object_list_unit_id=BuildingInfo.TOWN_CENTER.ID,
            target_player=player,
            source_player=PlayerId.GAIA,
        )

    for player in range(1, NUM_PLAYERS + 1):
        trigger = tm.add_trigger(f"if queued villagers (p{player})")
        trigger.new_condition.timer(
            timer=2,
            inverted=True
        )
        trigger.new_condition.research_technology(
            source_player=player,
            technology=TechInfo.CHINESE.ID
        )
        trigger.new_condition.researching_tech(
            source_player=player,
            technology=TechInfo.LOOM.ID
        )
        trigger.new_condition.accumulate_attribute(
            attribute=ResourceId.QUEUED_UNITS,
            quantity=1,
            source_player=player
        )
        trigger.new_effect.activate_trigger(
            trigger_id=trigger.trigger_id + NUM_PLAYERS
        )

    for player in range(1, NUM_PLAYERS + 1):
        trigger = tm.add_trigger(f"Dequeue TC (p{player})")
        trigger.enabled = False
        trigger.new_condition.research_technology(
            source_player=player,
            technology=TechInfo.LOOM.ID
        )
        trigger.new_condition.accumulate_attribute(
            attribute=ResourceId.TRAINING_COUNT,
            quantity=1,
            source_player=player
        )
        trigger.new_effect.change_ownership(
            object_list_unit_id=BuildingInfo.TOWN_CENTER.ID,
            source_player=player,
            target_player=PlayerId.GAIA,
        )
        trigger.new_effect.change_ownership(
            object_list_unit_id=BuildingInfo.TOWN_CENTER.ID,
            target_player=player,
            source_player=PlayerId.GAIA,
        )


def dialogue_sequence(dialogues, tm):
    trigger = tm.add_trigger("-- Dialogue Sequence --")
    number = 1
    total_time = 0
    for dialogue in dialogues:
        trigger = tm.add_trigger(f"Dialogue {number}: {dialogue['speaker']}")
        trigger.new_condition.timer(
            timer=total_time
        )
        trigger.new_effect.display_instructions(
            object_list_unit_id=dialogue["unit"],
            source_player=dialogue["player"],
            display_time=dialogue["time"],
            instruction_panel_position=PanelLocation.CENTER,
            message=f"<{GameInfo.COLOUR[dialogue['player'] - 1]}>{dialogue['speaker']}: " + dialogue["message"]
        )
        total_time += dialogue["time"]
        number += 1


def implement_guardstate(unit, NUM_PLAYERS, tm):
    for player in range(1, NUM_PLAYERS + 1):
        trigger = tm.add_trigger(f"Guard {unit.name.lower()} (p{player})")
        trigger.new_condition.own_fewer_objects(
            quantity=0,
            object_list=unit.ID,
            source_player=player
        )
        trigger.new_effect.declare_victory(
            source_player=player,
            enabled=False
        )
    for player in range(1, NUM_PLAYERS):
        trigger = tm.add_trigger(f"Victory (p{player}) no {unit.name.lower()}")
        for trg_player in range(1, NUM_PLAYERS + 1):
            if trg_player != player:
                trigger.new_condition.own_fewer_objects(
                    quantity=0,
                    object_list=UnitInfo.KING.ID,
                    source_player=trg_player,
                )
                trigger.new_effect.declare_victory(
                    source_player=player,
                    enabled=True
                )


def implement_regicide(NUM_PLAYERS, tm):
    implement_guardstate(UnitInfo.KING, NUM_PLAYERS, tm)


def implement_koth(NUM_PLAYERS, tm):
    MONUMENT_OWNER_VAR = tm.add_variable("monument owner").variable_id
    COUNTDOWN_VAR = tm.add_variable("countdown").variable_id

    for player in range(1, NUM_PLAYERS + 1):
        trigger = tm.add_trigger(f"Set Trickle Res (p{player})")
        trigger.new_effect.modify_resource(
            quantity=1,
            tribute_list=ResourceId.MONUMENT_FOOD_PRODUCTIVITY,
            source_player=player,
            operation=Operation.SET
        )
        trigger.new_effect.modify_resource(
            quantity=1,
            tribute_list=ResourceId.MONUMENT_WOOD_PRODUCTIVITY,
            source_player=player,
            operation=Operation.SET
        )
        trigger.new_effect.modify_resource(
            quantity=1,
            tribute_list=ResourceId.MONUMENT_GOLD_PRODUCTIVITY,
            source_player=player,
            operation=Operation.SET
        )
        trigger.new_effect.modify_resource(
            quantity=1,
            tribute_list=ResourceId.MONUMENT_STONE_PRODUCTIVITY,
            source_player=player,
            operation=Operation.SET
        )

    trigger = tm.add_trigger("Set Vars")
    trigger.new_effect.change_variable(
        quantity=9,
        operation=Operation.SET,
        variable=MONUMENT_OWNER_VAR
    )
    trigger.new_effect.change_variable(
        quantity=551,
        operation=Operation.SET,
        variable=COUNTDOWN_VAR
    )

    trigger = tm.add_trigger("Under 100 Years Reset")
    trigger.enabled = False
    trigger.new_condition.variable_value(
        quantity=100,
        variable=COUNTDOWN_VAR,
        comparison=Comparison.LESS_OR_EQUAL
    )
    trigger.new_effect.change_variable(
        quantity=100,
        operation=Operation.SET,
        variable=COUNTDOWN_VAR
    )

    activate_trigger_id = trigger.trigger_id

    for player in range(1, NUM_PLAYERS + 1):
        trigger = tm.add_trigger(f"Set Owner to (p{player})")
        trigger.new_condition.own_objects(
            quantity=1,
            object_list=BuildingInfo.MONUMENT.ID,
            source_player=player
        )
        trigger.new_effect.change_variable(
            quantity=player,
            operation=Operation.SET,
            variable=MONUMENT_OWNER_VAR
        )
        trigger.new_effect.activate_trigger(
            trigger_id=activate_trigger_id
        )
        for trigger_ids in range(trigger.trigger_id - player + 1, trigger.trigger_id + NUM_PLAYERS - player + 1):
            if trigger_ids != trigger.trigger_id:
                trigger.new_effect.activate_trigger(
                    trigger_id=trigger_ids
                )
    trigger = tm.add_trigger("Update Countdown")
    trigger.looping = True
    trigger.new_condition.own_fewer_objects(
        quantity=0,
        object_list=BuildingInfo.MONUMENT.ID,
        source_player=PlayerId.GAIA
    )
    trigger.new_condition.timer(
        timer=5
    )
    trigger.new_effect.change_variable(
        quantity=1,
        operation=Operation.SUBTRACT,
        variable=COUNTDOWN_VAR
    )

    trigger = tm.add_trigger("Display Countdown")
    trigger.description = trigger.short_description = f"<Variable {COUNTDOWN_VAR}> Years Remaining\nMonument Owned By" + \
                                                      f" P<Variable {MONUMENT_OWNER_VAR}>"
    trigger.display_as_objective = trigger.display_on_screen = True
    trigger.new_condition.player_defeated(
        source_player=PlayerId.GAIA
    )

    for player in range(1, NUM_PLAYERS + 1):
        trigger = tm.add_trigger(f"Win (p{player})")
        trigger.new_condition.variable_value(
            quantity=0,
            variable=COUNTDOWN_VAR,
            comparison=Comparison.EQUAL
        )
        trigger.new_condition.own_objects(
            quantity=1,
            object_list=BuildingInfo.MONUMENT.ID,
            source_player=player
        )
        trigger.new_effect.declare_victory(
            source_player=player,
            enabled=True
        )

def add_section_keys(scenario: AoE2DEScenario):
    tm = scenario.trigger_manager
    section = 65
    for trigger in tm.triggers:
        if not trigger.name.startswith("=="):
            trigger.name = " "+trigger.name
        else:
            trigger.name = chr(section)+trigger.name
            section += 1
            if section == 91:
                section = 65

def make_verbose(tm: TriggerManager):
    for trigger in tm.triggers[10:]:
        if not trigger.name.startswith("=="):
            trigger.new_effect.send_chat(
                source_player=1,
                message=f"{trigger.name} ran successfully",
            )

def overwrite_trigger(target_trigger: Trigger, source_trigger: Trigger) -> None:
    """
    :param target_trigger: The trigger that will get overwritten
    :param source_trigger: The trigger whoes attributes will be used to overwrite
    :return: None
    """
    target_trigger.__dict__.update(source_trigger.__dict__)

def minify(code: str) -> str:
    strings = []
    for i, string in enumerate(regex.finditer(r'"(?:(?!")(?:\\.|[^\\]))*"', code)):
        strings.append(string[0])
        code = code.replace(string[0], f"REPLACESTRING{i}", 1)

    # remove comments
    code = regex.sub(r"//.*", "", code)
    code = regex.sub(r"\/\*.*\*\/", "", code, flags = regex.DOTALL)

    # remove new lines, reduce spaces, tabs and
    code = regex.subf(r"(?:\n|\r|\t)", " ", code)
    code = regex.subf(r"\s+", " ", code)

    # remove redundant spaces
    code = regex.subf(r"\s+(\W+)\s+", "{1}", code)
    code = regex.subf(r"(\W+)\s+", "{1}", code)
    code = regex.subf(r"\s+(\W+)", "{1}", code)

    for i, string in enumerate(strings):
        code = code.replace(f"REPLACESTRING{i}", string, 1)

    return code

def minify_all(tm: TriggerManager):
    for trigger in tm.triggers: #type: Trigger
        for condition in trigger.conditions: #type: Condition
            if condition.condition_type == ConditionId.SCRIPT_CALL:
                condition.xs_function = minify(condition.xs_function)
        for effect in trigger.effects: #type: Effect
            if effect.effect_type == EffectId.SCRIPT_CALL:
                effect.message = minify(effect.message)

def condition_to_text(condition: Condition, tm):
    _condition = condition.condition_type
    quantity = condition.quantity
    resource = condition.attribute
    ref1 = condition.unit_object
    ref2 = condition.next_object
    unit = condition.object_list
    src = condition.source_player
    tech = condition.technology
    timer = condition.timer
    x1 = condition.area_x1
    y1 = condition.area_y1
    x2 = condition.area_x2
    y2 = condition.area_y2
    group = condition.object_group
    _type = condition.object_type
    state = condition.object_state
    ai_signal = condition.ai_signal
    inverted = condition.inverted
    var = condition.variable
    comparison = condition.comparison
    trg = condition.target_player
    action = condition.unit_ai_action
    xs = condition.xs_function

    output = ""
    if _condition not in [20, 29]:
        output = "if VARIABLE "

    if src == 0:
        src = "Gaia"
    elif src != -1:
        src = f"p{src}"

    if trg == 0:
        trg = "Gaia"
    elif trg != -1:
        trg = f"p{src}"

    output += {"-1": ""}.get(f"{src}", f"{src} ")
    output += _condition_grammar[f"{_condition}"]
    output = output.replace("least", "most") if inverted else output.replace(" not", "").replace("not ", " ")

    if var != -1:
        try:
            output = output.replace("VARIABLE", f"{tm.get_variable(variable_id=var).name}")
        except ResourceId.rror:
            output = output.replace("VARIABLE", f"Variable {var}")

        output += f" {_comparison_grammar[f'{comparison}']} {quantity}"
        return output

    output = output.replace("VARIABLE ", "")

    if timer != -1:
        output = output.replace("VALUE", f"{timer}")
        return output

    if ai_signal != -1:
        output = output.replace("VALUE", f"{ai_signal}")
        return output

    if xs:
        return output

    if action != -1:
        output = output.replace("ACTION", _action_grammar.get(f"{action}", f"action: {action}"))

    if ref1 != -1:
        output = output.replace("OBJECT1", f"object: {ref1}")
        if ref2 != -1:
            output = output.replace("OBJECT2", f"object: {ref2}")
        else:
            output = output.replace("OBJECT2", f"another object")

    need_quantity = False
    if _condition != 21 and quantity != -1:
        need_quantity = True
        placeholders = ["VALUE", "DIPLO_STATE"]
        replacements = [{"-1": ""}, _diplo_state_grammar]
        for placeholder, replacement in zip(placeholders, replacements):
            if placeholder in output:
                output = output.replace(placeholder, replacement.get(f"{quantity}", f"{quantity}"))
                need_quantity = False
                if quantity == 1:
                    output.replace("objects", "object")
                break
        if need_quantity:
            output += f" {quantity}"

    if tech != -1:
        try:
            output += " " + TechInfo.from_id(tech).name.lower().replace("_", " ")
        except ValueError:
            output += " " + f"tech: {tech}"

        if _condition == 21:
            output = output.replace("TECH_STATE", _tech_state_grammar.get(f"{quantity}", f"{quantity}"))
            if not inverted:
                output = output.replace(" not", "") if quantity not in [-1, 0] else output
            else:
                output = output.replace(" not", "") if quantity in [-1, 0] else output

        if tech in GameInfo.CIVS:
            output = output.replace(" researched", "")
            output = output.replace(" able to research", "")
            if quantity != 4:
                output = output.replace("has", "is")

        return output

    if trg != -1:
        output += f" {trg}"
        return output

    if unit != -1:
        unit_name = ""
        for dataset in [UnitInfo, BuildingInfo, HeroInfo, OtherInfo]:
            try:
                unit_enum = dataset.from_id(unit)
                if unit_enum is None:
                    continue
                unit_name = unit_enum.name.lower().replace("_", " ")
            except ValueError:
                continue

        output += " " + (unit_name or f"{unit}")
        if need_quantity:
            output += "" if quantity == 1 else "s"

    elif group != -1 or _type != -1:
        if _type != -1:
            output += " unit of type: " if quantity == 1 else " units of type: "
            try:
                output += ObjectType(_type).name.lower().replace("_", " ")
            except ValueError:
                output += f"{_type}"
        if group != -1:
            if _type != -1:
                output += " and"
            output += " belonging to class: "
            try:
                output += ObjectClass(group).name.lower().replace("_", " ")
            except ValueError:
                output += f"{group}"

    output_parts = output.partition(" AREA")
    output = output_parts[0] + output_parts[2] + output_parts[1]

    if x1 != -1:
        state_if_present = ""
        if state != -1:
            state_if_present = _object_state_grammar[f"{state}"] + " "
            if quantity > 1:
                state_if_present = state_if_present.replace("is a", "are")
                state_if_present = state_if_present.replace("is", "are")
                state_if_present = state_if_present.replace("PLURAL", "s")
            else:
                state_if_present = state_if_present.replace("PLURAL", "")

        output = output.replace("AREA", f"{state_if_present}in the area from ({x1}, {y1}) to ({x2}, {y2})")
    else:
        output = output.replace("AREA", f"on the map")

    if resource != -1:
        try:
            output += " " + ResourceId.from_id(resource).name.lower().replace("_", " ")
        except ValueError:
            output += " " + f"{resource}"

    return output


def get_arg(i: int) -> str | None:
    if len(sys.argv) > i:
        return sys.argv[i]
    return None
