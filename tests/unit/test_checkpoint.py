"""Tests for checkpoint store."""

import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

BIN_DIR = Path(__file__).resolve().parents[2] / "package" / "bin"
LIB_DIR = Path(__file__).resolve().parents[2] / "output" / "TA-anthropic_claude_enterprise" / "lib"
if LIB_DIR.is_dir():
    sys.path.insert(0, str(LIB_DIR))
sys.path.insert(0, str(BIN_DIR))

if "solnlib" not in sys.modules:
    solnlib = MagicMock()
    solnlib.modular_input = MagicMock()
    solnlib.modular_input.checkpointer = MagicMock()
    sys.modules["solnlib"] = solnlib
    sys.modules["solnlib.modular_input"] = solnlib.modular_input
    sys.modules["solnlib.modular_input.checkpointer"] = solnlib.modular_input.checkpointer


class TestCheckpointStore(unittest.TestCase):
    @patch("solnlib.modular_input.checkpointer.KVStoreCheckpointer")
    def test_get_returns_empty_dict_when_missing(self, mock_cls):
        from ta_anthropic_claude_enterprise.checkpoint import CheckpointStore

        mock_cls.return_value.get.return_value = None
        store = CheckpointStore("session-key")
        self.assertEqual(store.get("input_a"), {})

    @patch("solnlib.modular_input.checkpointer.KVStoreCheckpointer")
    def test_set_delegates_to_checkpointer(self, mock_cls):
        from ta_anthropic_claude_enterprise.checkpoint import CheckpointStore

        store = CheckpointStore("session-key")
        store.set("input_a", {"cursor": "abc"})
        mock_cls.return_value.update.assert_called_once_with("input_a", {"cursor": "abc"})


if __name__ == "__main__":
    unittest.main()
