from extract_data import extract_data_invoices_from_csv, extract_categories
from process_data import process_data
from transform_data import transform

if __name__ == "__main__":
    df_invoices = extract_data_invoices_from_csv()

    transformed_df_invoices = transform(df=df_invoices, action="lower")

    process_data(df_invoices=transformed_df_invoices)
