import pandas as pd
import os
from extract_data import extract_categories

current_dir = os.path.dirname(os.path.abspath(__file__))


def process_data(df_invoices):

    # cria uma coluna de categoria no df e aplica a funcao "categorizar"
    df_invoices["categoria"] = df_invoices["lancamento"].apply(categorizar)

    # Remover linhas onde categoria é "REMOVER"
    drop_outros_cat = df_invoices[
        df_invoices["categoria"].str.contains("REMOVER", na=False)
    ].index
    df_invoices = df_invoices.drop(drop_outros_cat)

    # remove valores negativos
    drop_neg_values = df_invoices[df_invoices["valor"] <= 0].index
    df_invoices = df_invoices.drop(drop_neg_values)

    # converter data
    df_invoices["data"] = pd.to_datetime(df_invoices["data"])

    # criar coluna de mês
    df_invoices["mes"] = df_invoices["data"].dt.to_period("M").astype(str)

    # salvar dataset final
    df_invoices.to_csv("transacoes_tratadas.csv", index=False)


def categorizar(lancamento):
    df_category = extract_categories()
    for _, row in df_category.iterrows():
        if row["word"] in lancamento:
            return row["category"]
        elif "pagamento efetuado" in lancamento or "pagamento com saldo" in lancamento:
            return "REMOVER"
    return "Outros"
