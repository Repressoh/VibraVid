# 25.06.20
# ruff: noqa: E402

import os
import sys


# Fix import
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(src_path)


from VibraVid.utils import start_message
from VibraVid.core.downloader import MEGA_Downloader


start_message()
mega = MEGA_Downloader(
    choose_files=True
)

output_path = mega.download_url(
    url="",
    dest_path=r".\Video\Movie\Prova.mp4",
)