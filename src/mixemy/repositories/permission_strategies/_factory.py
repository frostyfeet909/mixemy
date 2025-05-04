from mixemy.repositories.permission_strategies._base import PermissionStrategy
from mixemy.repositories.permission_strategies._loose_strategy import (
    LoosePermissionStrategy,
)
from mixemy.repositories.permission_strategies._strict_strategy import (
    StrictPermissionStrategy,
)
from mixemy.types import BaseModelT, permission_strategies


class PermissionStrategyFactory:
    """Factory class for creating permission strategies."""

    @staticmethod
    def create_permission_strategy(
        strategy: permission_strategies,
        model: type[BaseModelT],
        user_id_attribute: str,
        user_joined_table: str | None,
    ) -> PermissionStrategy:
        """Create a permission strategy based on the given strategy name."""
        if strategy == "loose":
            return LoosePermissionStrategy(
                model=model,
                user_id_attribute=user_id_attribute,
                user_joined_table=user_joined_table,
            )

        return StrictPermissionStrategy(
            model=model,
            user_id_attribute=user_id_attribute,
            user_joined_table=user_joined_table,
        )
