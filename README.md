[![Wednesware](https://github.com/Wednesware/Nitrogen/raw/main/wednesware.png)](https://wednesware.org)

# carbon

A lightweight cross-platform audio playback library for WAV files. It uses native platform audio APIs to play, loop, and stop sounds while helping prevent overlap and audio conflicts.

## Installation

> `n2 get carbon`

## Quick start

### Play a sound file

```python
from carbon import play

play("demo.wav")
```

### Start a looping sound without global overlap

```python
from carbon import loop

loop("alarm.wav", times=3, delay=0.5, prevent_global_overlap=True)
```

### Play in a background thread and stop it later

```python
from carbon import play_thread, stop, wait

play_thread("notification.wav")
wait(0.5)
stop("notification.wav")
```

## Dependencies

- Python 3.12+
- Nitrogen 26.63+ (`pip install wwn`)
- [ALSA Utils](https://github.com/alsa-project/alsa-utils) **(Only on Linux)** (`sudo apt install alsa-utils` or `sudo pacman -S alsa-utils`)

# Definitions

## `carbon`

From the package, you can import the playback helpers and platform-safe stop controls.

> from carbon import play, play_thread, loop, loop_thread, stop, stop_all, wait, NoALSAUtilsError

### `carbon.NoALSAUtilsError`

Raised on Linux when playback is requested without ALSA support installed. The library checks for `aplay` and raises this error before trying to play audio.

> error = NoALSAUtilsError("Linux playback requires 'aplay' from alsa-utils")

### `carbon.play(path, wav=False, prevent_overlap=False, prevent_global_overlap=False)`

Plays an audio file from `path`. The path must exist, and unless `wav=True` the file must have a `.wav` extension. Playback uses the native OS player: `winsound` on Windows, `afplay` on macOS, and `aplay` on Linux. Set `prevent_overlap=True` to stop any active instance of the same file before replaying it, and `prevent_global_overlap=True` to stop every active sound before playing.

> play("demo.wav")

### `carbon.play_thread(path, wav=False, prevent_overlap=False, prevent_global_overlap=False, buffer=0.001)`

Starts `play()` in a background thread and sleeps for `buffer` seconds after launching so the thread can begin without blocking the caller. This is useful for non-blocking audio playback with the same options as `play()`.

> play_thread("demo.wav", prevent_global_overlap=True)

### `carbon.loop(path, wav=False, prevent_overlap=False, prevent_global_overlap=False, times=-1, delay=0, thread=False)`

Repeatedly plays the same sound file. When `times` is `-1`, playback loops forever until the process ends. Each iteration waits `delay` seconds after playing when `delay > 0`. If `thread=True`, the library launches each iteration via `play_thread()` instead of blocking the main thread, playing the next iteration without waiting for the current one to finish.

> loop("demo.wav", times=3, delay=0.25)

### `carbon.loop_thread(path, wav=False, times=1, prevent_overlap=False, prevent_global_overlap=False, delay=0, thread=False)`

Runs `loop()` in a separate daemon thread. Unlike `loop()`, this function does not accept infinite looping; `times=-1` raises a `ValueError` and instructs callers to use `loop()` instead.

> loop_thread("demo.wav", times=2, delay=0.2)

### `carbon.stop(path)`

Stops playback for a specific file. On Windows it stops the underlying sound device; on Unix-like systems it terminates the stored subprocess for that file path if it is still active. If the file is not currently playing, the call is ignored.

> stop("demo.wav")

### `carbon.stop_all()`

Stops every active sound currently tracked by the library. This is useful when a global playback lock is needed and you want to silence all queued or active sounds immediately.

> stop_all()

### `carbon.wait(seconds)`

Alias for `time.sleep`, exposed by the package for convenience in background playback loops and scheduling helpers.

> wait(0.5)
