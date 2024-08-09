# Platform Builder Setup Guide

Welcome to my APP called the MoviePULSE recommender system Platform Builder setup guide! This guide will walk you through the steps to download, prepare your workspace, and run the program.

## Prerequisites

- Ensure you have the latest Python installed on your system (i.e 3.12 and above)

## Steps to Set Up and Run the Program

### 1. Unzip the File

Unzip the downloaded file to a directory of your choice.

### 2. Navigate to the Source Directory

Open your terminal or shell and navigate to the `platform_builder/src` directory.

```sh
cd path/to/platform_builder/src
```

### 3. Create a Virtual Environment

It is advisable to create a virtual environment to manage dependencies. Youe can use PIPENV or venv, Do as you please.

```sh
pipenv install
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

or

you can use you Visual studio code or pycharm to create the virtual environment of your choice.
```

### 4. Install Dependencies

Install all dependencies listed in the `requirements.txt` file.

```sh
pipenv install -r requirements.txt

or

you can use the usual pip if you have difficulties with pipenv
pip install -r requirements.txt
```

### 5. Test the Program to make sure the importation is accurate.

Run the program to ensure all checks pass. You should see the following output:
In your terminal run the following:

```sh
python tool_kits/processor.py
```

Expected output:

```
Environment Variable Validation Results:

NETFLIX_RAW_DATA: Valid
TDMB_RAW_DATA: Valid

Paths existence test results:

Path for NETFLIX_DATA_SOURCE_LOCAL: - Exists: True
Path for TDMB_DATA_SOURCE_LOCAL: - Exists: True
Path for NETFLIX_VECTOR_STORE_PATH: - Exists: True
Path for TDMB_VECTOR_STORE_PATH: - Exists: True

Loading the vector store: netflix_vector_db...
Loading the vector store: tdmb_vector_db...
<class 'langchain_community.vectorstores.chroma.Chroma'>
<class 'langchain_community.vectorstores.chroma.Chroma'>

Prompt template created successfully.

input_variables=['context', 'input'] messages=[SystemMessagePromptTemplate(prompt=PromptTemplate(input_variables=['context'], template="Your job is to provide personalized movie recommendations based on the user's preferences and viewing history.\n    Use the following context to recommend movies. Be as detailed as possible, but don't make up any information that's not from the context. If you can't make a recommendation, explain why.\n    {context}\n\n    Please recommend a movie for this user and explain your choice:\n    ")), HumanMessagePromptTemplate(prompt=PromptTemplate(input_variables=['input'], template='{input}'))]
```

### 6. Activate the API Endpoints

To start the API endpoints, run the following command:

```sh
uvicorn main:app --reload
```

If the API endpoint starts successfully, you should see something similar to this:

```
INFO:     Started server process [3889]* please note the number [3889] will be different for you.
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 7. Activate the Frontend

Open another command line or terminal session and navigate to the /platform_builder/src/recommend_api` directory.

```sh
cd path/to/platform_builder/src/recommend_api
```

Install the requirement files again if your python environment has changed or better still activate the virtual env used earlier for this new command line:

```sh
pip install -r requirements.txt
```

Run the frontend application:

```sh
python movie_cli_v4.py
```

This will open up the app for you to get ready recommendations, 
PLEASE FOLLOW THE ONE SCREEN INSTRUCTIONS TO INTERACT WITH THE PROGRAM

### 8. Closing the Program

To close the program, use the `exit` command on the `movie_cli_v4` interface.

To close the API endpoint, use `Ctrl + C` in the terminal where the API is running.

## Running the unit testing:

please navigate to the /platform_builder/src/test

- install pytest
- then run pytest unit_test.py

## Troubleshooting

If you encounter any issues, please ensure:

- All dependencies are installed correctly.
- Environment variables are set properly.
- Paths specified in the environment variables exist.

## Contact

For further assistance, please contact [bleck.tita@clarity.ai].

Thank you for using MoviePULSE!
