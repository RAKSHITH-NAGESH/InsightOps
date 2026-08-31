from analysis.csv_loader import load_csv


def profile_dataset(file_path: str) -> dict:
    """
    Profile a CSV dataset.
    """

    try:
        df = load_csv(file_path)

        numeric_columns = df.select_dtypes(
            include="number"
        ).columns.tolist()

        categorical_columns = df.select_dtypes(
            include=["object", "category", "string"]
        ).columns.tolist()

        missing_values = (
            df.isnull()
            .sum()
            .to_dict()
        )

        return {
            "success": True,
            "rows": int(len(df)),
            "columns": int(len(df.columns)),
            "column_names": df.columns.tolist(),
            "numeric_columns": numeric_columns,
            "categorical_columns": categorical_columns,
            "data_types": (
                df.dtypes
                .astype(str)
                .to_dict()
            ),
            "missing_values": missing_values,
            "duplicate_rows": int(
                df.duplicated().sum()
            ),
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }