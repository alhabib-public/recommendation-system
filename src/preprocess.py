import pandas as pd

def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Strip whitespace and ensure consistent column names."""
    df.columns = df.columns.str.strip()  # Remove leading/trailing spaces
    return df

def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    """Preprocess dataset."""
    df = clean_column_names(df)
    df = df.drop_duplicates().dropna()
    return df
