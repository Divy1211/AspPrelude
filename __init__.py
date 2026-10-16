from .parser_imports import *
from .help_functions import (
    log,
    players_i,
    players,
    tiles,
    player_count,
    disable_carto,
    random_units_spawn,
    add_credits_header,
    fix_scouts,
    regi_nomad_res,
    add_civ_bonuses,
    handle_chinese,
    dialogue_sequence,
    implement_guardstate,
    implement_regicide,
    implement_koth,
    add_section_keys,
    make_verbose,
    make_unreachable,
    overwrite_trigger,
    minify,
    minify_all,
    condition_to_text,
    lerp,
    get_arg,
    to_pascal,
)
from .common_vars import Paths, GameInfo
from .help_xs import XsFn, xs_vec, str_arg, bool_arg, xs_display_instructions, is_in_editor

from .struct_gen import xs_struct

from xs_writer import XsWriter

from AoE2ScenarioParser import settings

settings.ENABLE_XS_CHECK_INTEGRATION = False
