from io import BytesIO
import os
import shutil
import subprocess
import time
from PIL import Image

from config.config import Config


class TerminalDisplay:
    def __init__(self):
        self.glow_available = shutil.which("glow") is not None
        self.kitten_available = shutil.which("kitten") is not None

    def show_text(self, text: str):
        md_path = (Config().tmp_dir / "c.md").as_posix()

        with open(md_path, "w") as f:
            f.write(text)

        if self.glow_available:
            subprocess.run(["glow", f"{md_path}"], check=True)
        else:
            print("\n[INFO] `glow` not found. Displaying raw text:\n")
            print(text)

    def show_image(self, image_data: bytes):
        os.makedirs(Config().image_dir, exist_ok=True)
        image = Image.open(BytesIO(image_data))
        img_path = (Config().image_dir / f"{time.time_ns()}.png").as_posix()
        image.save(img_path)

        if self.kitten_available:
            subprocess.run(["kitten", "icat", f"{img_path}"], check=True)
        else:
            print(f"[INFO] `kitten` not found. Saved image at: {img_path}")

    def __del__(self):
        pass
