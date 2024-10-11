import os

import pandas as pd
import tiktoken
from dotenv import load_dotenv
from langchain.tools import tool
from langchain_chroma import Chroma
from langchain_community.document_loaders import DataFrameLoader
from langchain_openai import OpenAIEmbeddings

load_dotenv()

NETFLIX_TITLES_PATH = os.getenv("NETFLIX_TITLES_PATH", "data/titles.csv")
CHROMADB_URL = os.getenv("CHROMADB_URL", "./data/chromadb")


def setup_chroma(src_path: str, db_url: str) -> Chroma:
    df = pd.read_csv(src_path)
    loader = DataFrameLoader(df, page_content_column="description")
    docs = loader.load()
    embedding_function = OpenAIEmbeddings()
    # No need to split due to size
    db = Chroma.from_documents(
        documents=docs,
        embedding=embedding_function,
        persist_directory=db_url,
    )
    return db


def load_chroma(db_url: str) -> Chroma:
    embedding_function = OpenAIEmbeddings()
    return Chroma(persist_directory=db_url, embedding_function=embedding_function)


def print_datasource_info(data_path: str):
    df = pd.read_csv(data_path)
    print("Dataframe info:")
    print(df.info())
    print("Average description length:", df["description"].str.len().mean())
    print("Max description length:", df["description"].str.len().max())
    print("Min description length:", df["description"].str.len().min())
    max_description = df.loc[df["description"].str.len().idxmax(), "description"]
    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    print("Max description number of tokens:", len(encoding.encode(max_description)))


@tool
def get_netflix_titles_movie_documents(query: str) -> str:
    """Movies information based on a user query"""
    db = load_chroma(CHROMADB_URL)
    retriever = db.as_retriever()
    return retriever.invoke(query)


def main():
    # NOTE: this takes about 40 seconds to run
    print_datasource_info(data_path=NETFLIX_TITLES_PATH)
    setup_chroma(src_path=NETFLIX_TITLES_PATH, db_url=CHROMADB_URL)
    print("Chroma setup")
    print("Running and example query in the new data")
    retrieved_docs = get_netflix_titles_movie_documents.run("action movies")
    print(retrieved_docs)


if __name__ == "__main__":
    main()
