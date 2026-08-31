from analysis.csv_loader import load_csv


def detect_iqr_anomalies(
    file_path: str,
    metric_column: str,
) -> dict:
    """
    Detect outliers using the IQR method.
    """

    try:
        df = load_csv(file_path)

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

        series = df[metric_column].dropna()

        if series.empty:
            return {
                "success": False,
                "error": (
                    f"No valid values found "
                    f"in '{metric_column}'."
                ),
            }

        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)

        iqr = q3 - q1

        lower_bound = q1 - (1.5 * iqr)
        upper_bound = q3 + (1.5 * iqr)

        anomaly_mask = (
            (df[metric_column] < lower_bound)
            | (df[metric_column] > upper_bound)
        )

        anomalies = df[anomaly_mask]

        return {
            "success": True,
            "metric": metric_column,
            "q1": float(q1),
            "q3": float(q3),
            "iqr": float(iqr),
            "lower_bound": float(
                lower_bound
            ),
            "upper_bound": float(
                upper_bound
            ),
            "anomaly_count": int(
                len(anomalies)
            ),
            "anomalies": anomalies.to_dict(
                orient="records"
            ),
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


def discount_profit_analysis(
    file_path: str,
    discount_column: str,
    profit_column: str,
) -> dict:
    """
    Analyze the relationship between
    discount and profit.
    """

    try:
        df = load_csv(file_path)

        if discount_column not in df.columns:
            return {
                "success": False,
                "error": (
                    f"Column '{discount_column}' "
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

        if not (
            df[discount_column].dtype.kind
            in "biufc"
        ):
            return {
                "success": False,
                "error": (
                    f"'{discount_column}' "
                    "must be numeric."
                ),
            }

        if not (
            df[profit_column].dtype.kind
            in "biufc"
        ):
            return {
                "success": False,
                "error": (
                    f"'{profit_column}' "
                    "must be numeric."
                ),
            }

        correlation = df[
            discount_column
        ].corr(
            df[profit_column]
        )

        return {
            "success": True,
            "discount_column": discount_column,
            "profit_column": profit_column,
            "correlation": (
                float(correlation)
                if correlation == correlation
                else None
            ),
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }