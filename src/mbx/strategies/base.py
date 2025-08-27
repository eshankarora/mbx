from typing import Any, Protocol

import pandas as pd


class StrategyBase(Protocol):
    def target_weights(
        self, data: dict[str, pd.DataFrame], params: dict[str, Any]
    ) -> pd.DataFrame:
        ...
