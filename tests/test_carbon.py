import importlib
import shutil
import sys
import unittest


class CarbonPublicAPI(unittest.TestCase):
    def test_import_does_not_fail_without_aplay(self):
        original_which = shutil.which

        def fake_which(name, *args, **kwargs):
            if name == "aplay":
                return None
            return original_which(name, *args, **kwargs)

        try:
            shutil.which = fake_which
            sys.modules.pop("carbon", None)
            carbon = importlib.import_module("carbon")
            self.assertTrue(callable(getattr(carbon, "play", None)))
            self.assertTrue(callable(getattr(carbon, "stop", None)))
        finally:
            shutil.which = original_which
            sys.modules.pop("carbon", None)

    def test_aliases_remain_compatible(self):
        carbon = importlib.import_module("carbon")
        self.assertTrue(callable(carbon.play_sound))
        self.assertTrue(callable(carbon.play))
        self.assertTrue(callable(carbon.loop))
        self.assertTrue(callable(carbon.loop_sound))

    def test_stop_does_not_wait_for_audio_to_finish(self):
        carbon = importlib.import_module("carbon")

        class FakeProcess:
            def __init__(self):
                self.terminated = False
                self.killed = False

            def terminate(self):
                self.terminated = True

            def kill(self):
                self.killed = True

            def wait(self, *args, **kwargs):
                raise AssertionError("stop() should not block waiting for the process to finish")

        fake_process = FakeProcess()
        carbon._sound_processes["demo.wav"] = fake_process

        carbon.stop("demo.wav")

        self.assertNotIn("demo.wav", carbon._sound_processes)
        self.assertTrue(fake_process.terminated or fake_process.killed)


if __name__ == "__main__":
    unittest.main()
