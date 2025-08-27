from typing import Protocol, Any
import pandas as pd

class StrategyBase(Protocol):
    def target_weights(self, data: dict[str, pd.DataFrame], params: dict[str, Any]) -> pd.DataFrame: ...
