import os
import platform

# External library
from rich.console import Console


# Internal utilities
from VibraVid.utils import config_manager
from VibraVid.source.utils.tracker import context_tracker


# Variable
console = Console()
CLEAN = config_manager.config.get_bool('DEFAULT', 'show_message')
SHOW = config_manager.config.get_bool('DEFAULT', 'show_message')


def start_message(clean: bool=True):
    """Display a stylized start message in the console."""
    if not context_tracker.should_print:
        return

    msg = r'''
[#c084fc]██  ██ ▄▄ ▄▄▄▄  ▄▄▄▄   ▄▄▄  [#86efac]██  ██ ▄▄ ▄▄▄▄
[#7c3aed]██▄▄██ ██ ██▄██ ██▄█▄ ██▀██ [#22c55e]██▄▄██ ██ ██▀██
[#5b21b6] ▀██▀  ██ ██▄█▀ ██ ██ ██▀██ [#15803d] ▀██▀  ██ ████▀
    '''

    if CLEAN and clean: 
        os.system("cls" if platform.system() == 'Windows' else "clear")
        # console.clear() DA NON USARE CHE DIO CANE CREA PROBLEMI
    
    if SHOW:
        console.print(msg)