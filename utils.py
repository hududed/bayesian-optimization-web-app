import streamlit as st
import supabase
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, inspect
import os
import uuid
import pandas as pd
import seaborn as sns
import altair as alt


load_dotenv()
# Load Supabase credentials from .env file
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')

# Initialize Supabase client
supabase_client = supabase.create_client(supabase_url, supabase_key)
PG_PASS = os.getenv('PG_PASS')
DATABASE_URL = f'postgresql://postgres:{PG_PASS}@db.zugnayzgayyoveqcmtcd.supabase.co:5432/postgres'
engine = create_engine(DATABASE_URL)


# Define routes
def create_account(email, password):
    # Create new account
    response = supabase_client.auth.sign_up({
        'email': email,
        'password': password
    })
    return response

def login(credentials):
    # Login to existing account
    response = supabase_client.auth.sign_in_with_password(credentials)
    return response

def upload_to_bucket(bucket_name, file_name, file_content):
    # Generate new UUID for file name
    new_file_name = str(uuid.uuid4()) + '-' + file_name
    st.write(f'Uploading file "{file_name}" to bucket "{bucket_name}" as "{new_file_name}"')
    # Upload file to bucket
    supabase_client.storage.from_(bucket_name).upload(new_file_name, file_content)
    st.write(f'"{new_file_name}" uploaded to bucket "{bucket_name}"')

def create_table(table_name):
    # Create new table
    with engine.connect() as conn:
        query = text(f'CREATE TABLE IF NOT EXISTS {table_name} (id UUID NOT NULL DEFAULT uuid_generate_v4(), PRIMARY KEY (id));')
        conn.execute(query)
        st.write(f'Table "{table_name}" created in database')

def insert_data(table_name, data):
    # Insert data into table
    with engine.connect() as conn:
        df = pd.read_csv(data)
        df.to_sql(table_name, conn, if_exists='replace', index=False)
        st.write(f'{data.name} inserted into table "{table_name}"')

def display_table(table_name):
    # Query the table
    with engine.connect() as conn:
        query = f'SELECT * FROM {table_name}'
        df = pd.read_sql(query, conn)

    # Highlight the maximum values in the last column
    df_styled = df.style.highlight_max(subset=[df.columns[-1]])

    # Create two columns
    col1, col2 = st.columns(2)

    # Display the DataFrame in the first column
    col1.dataframe(df_styled)

    # Plot output as a function of each parameter in the second column
    output = df.iloc[:, -1]
    for param in df.columns[:-1]:
        chart_data = pd.DataFrame({
            'x': df[param],
            'y': output
        })
        chart = alt.Chart(chart_data).mark_circle().encode(
            x=alt.X('x', title=param),
            y=alt.Y('y', title=output.name)
        )
        col2.altair_chart(chart)
    sns.set_theme(context='talk')
    pairplot_fig = sns.pairplot(df, hue="param3", diag_kind='kde')
    st.pyplot(pairplot_fig)