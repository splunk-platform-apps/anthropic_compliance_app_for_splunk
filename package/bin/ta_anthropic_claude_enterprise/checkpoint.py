"""KV Store checkpoint management for modular inputs."""

from __future__ import annotations

from typing import Any, Dict, Optional

from solnlib.modular_input import checkpointer

from ta_anthropic_claude_enterprise import ADDON_NAME, CHECKPOINT_COLLECTION


class CheckpointStore:
    """Persist input checkpoints in Splunk KV Store (SHC-safe)."""

    def __init__(self, session_key: str, collection_name: str = CHECKPOINT_COLLECTION):
        self._checkpointer = checkpointer.KVStoreCheckpointer(
            collection_name,
            session_key,
            ADDON_NAME,
        )

    def get(self, input_key: str) -> Dict[str, Any]:
        state = self._checkpointer.get(input_key)
        if not state:
            return {}
        if isinstance(state, dict):
            return state
        return {}

    def set(self, input_key: str, state: Dict[str, Any]) -> None:
        self._checkpointer.update(input_key, state)

    def get_value(self, input_key: str, field: str, default: Optional[Any] = None) -> Any:
        return self.get(input_key).get(field, default)

    def update(self, input_key: str, **fields: Any) -> Dict[str, Any]:
        state = self.get(input_key)
        state.update(fields)
        self.set(input_key, state)
        return state
