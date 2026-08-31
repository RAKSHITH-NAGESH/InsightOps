from analysis.csv_loader import load_csv


def numeric_summary(file_path: str) -> dict:
    """
    Calculate summary statistics for numeric columns.
    """

    try:
        df = load_csv(file_path)

        numeric_df = df.select_dtypes(
            include="number"
        )

        if numeric_df.empty:
            return {
                "success": False,
                "error": "No numeric columns found.",
            }

        result = {}

        for column in numeric_df.columns:

            series = numeric_df[column].dropna()

            result[column] = {
                "count": int(series.count()),
                "sum": float(series.sum()),
                "mean": float(series.mean()),
                "median": float(series.median()),
                "min": float(series.min()),
                "max": float(series.max()),
                "std": (
                    float(series.std())
                    if len(series) > 1
                    else 0.0
                ),
            }

        return {
            "success": True,
            "summary": result,
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


def group_analysis(
    file_path: str,
    category_column: str,
    metric_column: str,
) -> dict:
    """
    Compare a numeric metric across categories.
    """

    try:
        df = load_csv(file_path)

        if category_column not in df.columns:
            return {
                "success": False,
                "error": (
                    f"Column '{category_column}' "
                    "not found."
                ),
            }

        if metric_column not in df.columns:
            return {
                "success": False,
                "error": (
                    f"Column '{metric_column}' "
                    "not found."
                ),
            }

        if not df[metric_column].dtype.kind in "biufc":
            return {
                "success": False,
                "error": (
                    f"'{metric_column}' "
                    "must be numeric."
                ),
            }

        grouped = (
            df.groupby(
                category_column,
                dropna=False
            )[metric_column]
            .agg(
                count="count",
                total="sum",
                average="mean",
                median="median",
                minimum="min",
                maximum="max",
            )
            .reset_index()
        )

        return {
            "success": True,
            "category": category_column,
            "metric": metric_column,
            "results": grouped.to_dict(
                orient="records"
            ),
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


def correlation_analysis(file_path: str) -> dict:
    """
    Calculate correlations between numeric variables.
    """

    try:
        df = load_csv(file_path)

        numeric_df = df.select_dtypes(
            include="number"
        )

        if numeric_df.shape[1] < 2:
            return {
                "success": False,
                "error": (
                    "At least two numeric "
                    "columns are required."
                ),
            }

        correlation = numeric_df.corr()

        return {
            "success": True,
            "correlation_matrix": (
                correlation
                .round(3)
                .to_dict()
            ),
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


def calculate_profit_margin(
    file_path: str,
    revenue_column: str,
    profit_column: str,
) -> dict:
    """
    Calculate profit margin statistics.
    """

    try:
        df = load_csv(file_path)

        if revenue_column not in df.columns:
            return {
                "success": False,
                "error": (
                    f"Column '{revenue_column}' "
                    "not found."
                ),
            }

        if profit_column not in df.columns:
            return {
                "success": False,
                "error": (
                    f"Column '{profit_column}' "
                    "not found."
                ),
            }

        revenue = df[revenue_column]
        profit = df[profit_column]

        margin = (
            profit / revenue.replace(0, float("nan"))
        ) * 100

        df["profit_margin"] = margin

        return {
            "success": True,
            "average_margin": float(
                margin.mean()
            ),
            "minimum_margin": float(
                margin.min()
            ),
            "maximum_margin": float(
                margin.max()
            ),
            "transaction_margins": df[
                [
                    revenue_column,
                    profit_column,
                    "profit_margin",
                ]
            ].to_dict(
                orient="records"
            ),
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }