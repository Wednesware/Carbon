from __future__ import annotations
import os, platform, shutil, subprocess, threading, time
from nitrogen import require
Color = require("mg.color").Color
if platform.system() == "Windows":
    import winsound


class NoALSAUtilsError(RuntimeError):
    """Raised when a Linux system tries to play audio without ALSA support."""

_sound_processes: dict[str, subprocess.Popen] = {}
wait = time.sleep

def _normalize_path(path: str | os.PathLike[str]) -> str:
    resolved = os.fspath(path)
    if not os.path.exists(resolved):
        raise FileNotFoundError(f"The specified file does not exist: {resolved}")
    return resolved

def _ensure_linux_alsa() -> None:
    if platform.system() == "Linux" and not shutil.which("aplay"):
        raise NoALSAUtilsError(
            "Linux playback requires 'aplay' from alsa-utils. Install it with "
            "'sudo apt install alsa-utils' (or your distro equivalent)."
        )

def play(path: str | os.PathLike[str], wav: bool = False, prevent_overlap: bool = False, prevent_global_overlap: bool = False) -> None:
    normalized = _normalize_path(path)
    if not normalized.lower().endswith(".wav") and not wav:
        raise ValueError(
            f"Only WAV (.wav) files are supported. "
            f"If you are sure '{normalized}' is a WAV file, pass wav=True."
        )
    if prevent_overlap:
        stop(path)
    if prevent_global_overlap:
        stop_all()
    match platform.system():
        case "Windows":
            winsound.PlaySound(normalized, winsound.SND_FILENAME)
        case "Darwin":
            _sound_processes[normalized] = subprocess.Popen(
                ["afplay", normalized],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        case "Linux":
            _ensure_linux_alsa()
            _sound_processes[normalized] = subprocess.Popen(
                ["aplay", normalized],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        case _:
            raise NotImplementedError("Sound playback is not supported on this platform.")

def play_thread(path: str | os.PathLike[str], wav: bool = False, prevent_overlap: bool = False, prevent_global_overlap: bool = False, buffer: float = 0.001) -> None:
    threading.Thread(target=play, args=(path,), kwargs={"wav": wav, "prevent_overlap": prevent_overlap, "prevent_global_overlap": prevent_global_overlap}, daemon=True).start()
    wait(buffer)
    
def loop(
    path: str | os.PathLike[str],
    wav: bool = False,
    prevent_overlap: bool = False,
    prevent_global_overlap: bool = False,
    times: int = -1,
    delay: float = 0,
    thread: bool = False,
) -> None:
    if times == -1:
        while True:
            if thread:
                play_thread(path, wav=wav, prevent_overlap=prevent_overlap, prevent_global_overlap=prevent_global_overlap)
            else:
                play(path, wav=wav)
            if delay > 0:
                wait(delay)
        return

    for _ in range(times):
        if thread:
            play_thread(path, wav=wav, prevent_overlap=prevent_overlap, prevent_global_overlap=prevent_global_overlap)
        else:
            play(path, wav=wav)
        if delay > 0:
            wait(delay)

def loop_thread(
    path: str | os.PathLike[str],
    wav: bool = False,
    times: int = 1,
    prevent_overlap: bool = False,
    prevent_global_overlap: bool = False,
    delay: float = 0,
    thread: bool = False
) -> None:
    if times == -1:
        raise ValueError("Infinite looping is not supported in loop_thread. Use loop() instead.")
    threading.Thread(
        target=loop,
        args=(path,),
        kwargs={"wav": wav, "prevent_overlap": prevent_overlap, "prevent_global_overlap": prevent_global_overlap, "times": times, "delay": delay, "thread": thread},
        daemon=True,
    ).start()

def stop(path: str | os.PathLike[str]) -> None:
    normalized = os.fspath(path)
    if platform.system() == "Windows":
        winsound.PlaySound(None, 0)
        return

    process = _sound_processes.pop(normalized, None)
    if process is None:
        return

    try:
        process.terminate()
    except Exception:
        pass

    try:
        process.kill()
    except Exception:
        pass

def stop_all() -> None:
    for path in list(_sound_processes):
        stop(path)
