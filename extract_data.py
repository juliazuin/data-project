import pandas as pd
import os

current_dir = os.path.dirname(os.path.abspath(__file__))


def extract_data_invoices_from_csv():
    # carregar todos csv de faturas
    dfs = []

    joined_path = os.path.join(current_dir, "invoice")
    for folders in os.listdir(joined_path):
        if folders != ".DS_Store":
            for file in os.listdir(joined_path + f"/{folders}"):
                df = pd.read_csv(joined_path + f"/{folders}" + f"/{file}")
                # appenda todos os CSVs dentro do mesmo dataframe
                dfs.append(df)

    df_invoices = pd.concat(dfs, ignore_index=True)
    # df.to_csv("transacoes_tratadas.csv", index=False)
    return df_invoices


def extract_categories():
    # carregar categorias
    df_category = pd.read_csv(current_dir + "/categories.csv")

    # normalizar texto
    df_category["word"] = df_category["word"].str.lower()

    return df_category
