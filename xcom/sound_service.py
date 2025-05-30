import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.logging import log

try:  # Optional external dependency
    from playsound import playsound
except Exception:  # pragma: no cover - optional
    playsound = None


class SoundService:
    def __init__(self, sound_file="static/sounds/death_spiral.mp3"):
        # Always anchor to project root
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.sound_file = os.path.join(base_dir, sound_file)

    def play(self, file_path: str = None):
        """
        Plays an MP3 file using `playsound`. Defaults to death_spiral.mp3.
        """
        # Respect override or default to init path
        path = os.path.abspath(file_path) if file_path else self.sound_file

        try:
            if not os.path.isfile(path):
                raise FileNotFoundError(f"Sound file not found: {path}")

            log.info(f"🔊 Playing sound: {path}", source="SoundService")

            if sys.platform.startswith("win"):
                try:
                    os.startfile(path)  # non-blocking
                except Exception as e:
                    log.debug(f"os.startfile failed: {e}", source="SoundService")
                    if playsound:
                        playsound(path)
                    else:
                        raise
            else:
                if playsound:
                    playsound(path)
                else:
                    raise RuntimeError("playsound dependency missing")

            log.success("✅ System sound played", source="SoundService")

        except Exception as e:
            log.error(f"❌ Playback failed: {e}", source="SoundService")
            self._fallback_beep()

    def _fallback_beep(self):
        try:
            print("\a")  # ASCII bell
            log.info("Fallback beep emitted", source="SoundService")
        except Exception as e:
            log.error(f"Fallback beep failed: {e}", source="SoundService")
