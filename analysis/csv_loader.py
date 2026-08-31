import pandas as pd


def load_csv(file_path: str) -> pd.DataFrame:
    """
    Load CSV using multiple common encodings.
    """

    try:
        return pd.read_csv(
            file_path,
            encoding="utf-8-sig"
        )

    except UnicodeDecodeError:

        try:
            return pd.read_csv(
                file_path,
                encoding="cp1252"
            )

        except UnicodeDecodeError:

            return pd.read_csv(
                file_path,
                encoding="latin1"
            )