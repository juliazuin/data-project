def transform(df, action):
    df = df.rename(columns={"lançamento": "lancamento"})

    if action == "lower":
        df["lancamento"] = df["lancamento"].str.lower()

    elif action == "upper":
        df["lancamento"] = df["lancamento"].str.upper()

    return df
