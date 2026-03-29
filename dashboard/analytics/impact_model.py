class ImpactCalculator:
    """Business impact calculations for operational analytics dashboards."""

    @staticmethod
    def calculate_fte_saved(auto_matched_count: int, mins_per_match: float = 3.0) -> float:
        """Return hours saved from automated matching throughput."""
        total_minutes_saved = auto_matched_count * mins_per_match
        return total_minutes_saved / 60.0

    @staticmethod
    def calculate_dso_reduction(total_ar: float, credit_sales: float, previous_dso: float) -> float:
        """Return reduction in DSO relative to a previous baseline."""
        if credit_sales == 0:
            return 0.0

        current_dso = (total_ar / credit_sales) * 365
        return previous_dso - current_dso
