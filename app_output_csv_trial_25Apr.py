import os
import pickle
import streamlit as st
import tempfile
import pandas as pd
import asyncio
from io import StringIO
import csv
#from dotenv import load_dotenv

# Import modules needed for building the chatbot application
from streamlit_chat import message
# from langchain.embeddings.openai import OpenAIEmbeddings
# from langchain.chat_models import ChatOpenAI
# from langchain.chains import ConversationalRetrievalChain
# from langchain.document_loaders.csv_loader import CSVLoader
# from langchain.vectorstores import FAISS

import openai

# Set the Streamlit page configuration, including the layout and page title/icon
st.set_page_config(layout="wide", page_icon="💬", page_title="Synthetic Scenario Generator")

# Display the header for the application using HTML markdown
st.markdown(
    "<h1 style='text-align: center;'>Synthetic Generator 💬</h1>",
    unsafe_allow_html=True)

# Load API key from .env file
#load_dotenv()
#user_api_key = os.getenv("OPENAI_API_KEY")
user_api_key = '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'
openai.api_key = user_api_key

# Allow the user to upload a CSV file
uploaded_file = st.sidebar.file_uploader("upload", type="csv", label_visibility="hidden")

# Allow the user to provide the number of records to be generated
user_no_of_records_needed = st.sidebar.text_input(label="#### Provide the number of records to be generated 👇",
                                            placeholder="For example: 10 records",
                                            type="default")

async def main():
    
    # Check if the user has entered an OpenAI API key
    if user_api_key == "":
        
        # Display a message asking the user to enter their API key
        st.markdown(
            "<div style='text-align: center;'><h4>Enter your OpenAI API key to start chatting 😉</h4></div>",
            unsafe_allow_html=True)
        
    else:
        # Set the OpenAI API key as an environment variable
        os.environ["OPENAI_API_KEY"] = user_api_key
        
        # If the user has uploaded a file, display it in an expander
        if uploaded_file is not None:
            def show_user_file(uploaded_file):
                file_container = st.expander("Your CSV file :")
                shows = pd.read_csv(uploaded_file)
                uploaded_file.seek(0)
                file_container.write(shows)
                
            show_user_file(uploaded_file)
            
        # If the user has not uploaded a file, display a message asking them to do so
        else :
            st.sidebar.info(
            "👆 Upload your CSV file to get started, "
            "sample for try : [fishfry-locations.csv](https://drive.google.com/file/d/18i7tN2CqrmoouaSqm3hDfAk17hmWx94e/view?usp=sharing)" 
            )
    
    if uploaded_file is not None and user_no_of_records_needed != "":
        # Convert uploaded file into a pandas dataframe
        input_csv = pd.read_csv(uploaded_file)

        # Extract column names and data types from the sample table
        columns = input_csv.columns.tolist()
        data_types = input_csv.dtypes.tolist()

        # Convert the input csv table into string format for input prompt
        data = input_csv.to_string(index=False)
        
        # Prepare your input prompt
        input_prompt = f"""
        Generate synthetic data for a table with the following columns: {columns}. The data types are: {data_types}.
        Use the following data as a sample table:

        {data}
        """
        # Define the API call parameters
        prompt = f"{input_prompt}\n\nGenerate synthetic data of {user_no_of_records_needed} new records in comma separarted csv format along with columns names from the above table using the above table as reference. Do not display the records from the sample table in the synthetic data results."


        print("Printing input prompt", prompt)

        print("Check 3")
        #Generate response using OpenAI API
        # response = openai.Completion.create(
        #         model="text-davinci-003",
        #         prompt=prompt
        #         )
        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=prompt,
            max_tokens = 3000,
            n = 1
        )
        
        api_string = response['choices'][0]['text']
        synthetic_df = pd.read_csv(StringIO(api_string), sep=",")

        print("Check 4")
        # print(synthetic_df)
        #Show the response in the web page
        
        # st.write('Length of input csv uploaded', len(input_csv))
        # st.write('Input prompt \n', input_prompt)
        st.write('API response \n',api_string)
        st.write('Output response from ChatGPT',synthetic_df)
        print("Printing final output table column names \n", synthetic_df.columns)

        # Download your results as a CSV file
        csv = synthetic_df.to_csv().encode('utf-8')
        st.download_button(
            label="Download data as CSV",
            data=csv,
            file_name='download_test_file.csv',
            mime='text/csv',
        )

    else:
        st.write("Upload a sample CSV and provide the number of records to be generated as input")

    print("Check 5")
    # Create an expander for the "About" section
    about = st.sidebar.expander("About 🤖")
    
    # Write information about the chatbot in the "About" section
    about.write("#### ChatBot-CSV is an AI chatbot featuring conversational memory, designed to enable users to discuss their CSV data in a more intuitive manner. 📄")
    about.write("#### He employs large language models to provide users with seamless, context-aware natural language interactions for a better understanding of their CSV data. 🌐")
    about.write("#### Powered by [Langchain](https://github.com/hwchase17/langchain), [OpenAI](https://platform.openai.com/docs/models/gpt-3-5) and [Streamlit](https://github.com/streamlit/streamlit) ⚡")
    about.write("#### Source code : [yvann-hub/ChatBot-CSV](https://github.com/yvann-hub/ChatBot-CSV)")

#Run the main function using asyncio
if __name__ == "__main__":
    asyncio.run(main())

