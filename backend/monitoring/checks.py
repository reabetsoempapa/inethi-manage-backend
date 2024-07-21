from dataclasses import dataclass, asdict
import enum
from typing import TYPE_CHECKING, Any
from django.conf import settings

if TYPE_CHECKING:
    from .models import Node
else:
    Node = Any


class CheckStatus(enum.Enum):
    """Status of a device check results."""

    CRITICAL = "Critical"
    WARNING = "Warning"
    DECENT = "Decent"
    OK = "Ok"

    def alert_level(self) -> int:
        """Convert status to an alert level."""
        if self == CheckStatus.OK:
            return 0
        if self == CheckStatus.DECENT:
            return 1
        if self == CheckStatus.WARNING:
            return 2
        return 3


@dataclass
class CheckResult:
    """The result for a particular device check."""

    title: str
    passed: bool | None
    feedback: str


class CheckResults(list[CheckResult]):
    """A list of device check results."""

    @classmethod
    def run_checks(cls, node: Node) -> "CheckResults":
        """Run checks for a node and return the results."""
        results = cls()
        for check in settings.DEVICE_CHECKS:
            check_func = check.get("func", bool)
            key = check["key"]
            if hasattr(node, key):
                value = getattr(node, key)
            else:
                get_func = getattr(node, f"get_{check['key']}")
                value = get_func()
            if value is not None:
                passed = check_func(value)
            else:
                passed = None
            results.append(
                CheckResult(
                    title=check["title"],
                    passed=passed,
                    feedback=check["feedback"][passed],
                )
            )
        return results

    @property
    def num_failed(self) -> int:
        """Get the number of failed checks."""
        return sum(1 for c in self if not c.passed)

    @property
    def num_passed(self) -> int:
        """Get the number of passed checks."""
        return sum(1 for c in self if c.passed)

    def oll_korrect(self) -> bool:
        """Check whether all checks passed."""
        return self.num_failed == 0

    def fewer_than_half_failed(self) -> bool:
        """Check whether fewer than half failed."""
        return self.num_failed <= len(self) / 2

    def more_than_half_failed_but_not_all(self) -> bool:
        """Check whether more than half of the checks failed (but not all)."""
        return self.num_failed > len(self) / 2 and self.num_passed != 0

    def all_failed(self) -> bool:
        """Check whether all of the checks failed."""
        return self.num_passed == 0

    def status(self) -> CheckStatus:
        """Node status, based on these check results."""
        if self.oll_korrect():
            return CheckStatus.OK
        if self.fewer_than_half_failed():
            return CheckStatus.DECENT
        if self.more_than_half_failed_but_not_all():
            return CheckStatus.WARNING
        # All failed
        return CheckStatus.CRITICAL

    def alert_summary(self) -> str:
        """Summary of failing checks, used to generate alerts."""
        return "\n".join(f"{c.title}: {c.feedback}" for c in self if not c.passed)

    def serialize(self) -> list[dict]:
        """Serialize results as a list of primitive dicts."""
        return [asdict(c) for c in self]
