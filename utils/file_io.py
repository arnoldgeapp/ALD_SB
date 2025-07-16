import os
import pandas as pd

BOOKS_CSV = "ald_books.csv"


def load_books():
    if os.path.exists(BOOKS_CSV):
        df = pd.read_csv(BOOKS_CSV)
        df["Book"] = df["Book"].fillna("").astype(str)
        return df
    return pd.DataFrame(columns=["Book", "Code", "Description"])


def save_books(df):
    df.to_csv(BOOKS_CSV, index=False)
