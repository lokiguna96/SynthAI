# Import all the required packages
import os
import pickle
import streamlit as st
import tempfile
import pandas as pd
import asyncio
from io import StringIO
import csv
from datetime import datetime

from streamlit_chat import message
import openai

from PIL import Image
#from dotenv import load_dotenv
from pathlib import Path

# datetime object containing current date and time
now = datetime.now()
execution_time = now.strftime("%Y%m%d_%H%M")

# Path to environment variables ( to be changed to relative path)
#dotenv_path = Path('.env')

#load_dotenv(dotenv_path=dotenv_path)

user_api_key = st.secrets["OPENAI_API_KEY"]
openai.api_key = user_api_key

# Building a light weight Streamlit web application
# Set the Streamlit page configuration, including the layout and page title/icon
st.set_page_config(layout="wide", page_icon="🏬", page_title="Synthetic Scenario Generator")

# Display the header for the application using HTML markdown
st.markdown(
    "<h1 style='text-align: center;'>SynthetikAI 📈</h1>",
    unsafe_allow_html=True)

# Opening the image for Kearney logo
# Path to the image file in local system (to be changed to relative path)
image = Image.open('Kearney_logo.jpg')

# Displaying the image on streamlit app
st.sidebar.image(image, caption='Kearney - Cookie Bite Hackathon - Generative AI')

# Get all user inputs in the side bar and send batch input to Streamlit app once all the inputs are given
# Create a Form in the sidebar for consolidating all the inputs
with st.sidebar.form(key='my_input_form', clear_on_submit=True):
    # Allow the user to upload a CSV file
    uploaded_file = st.file_uploader(label="#### Upload a sample CSV file 📂", type="csv", label_visibility="visible")
    hide_label = """
    <style>
        .css-9ycgxx {
            display: none;
        }
    </style>
    """
    st.markdown(hide_label, unsafe_allow_html=True)

    # Allow the user to provide the number of records to be generated
    user_context = st.text_input(label="#### Provide context",
                                                placeholder="",
                                                type="default")

    # Allow the user to provide the date for which the synthetic data is to be generated
    user_date_input = st.date_input(label="#### Enter the date for which synthetic data has to be generated 📅")
    submit_button = st.form_submit_button(label='Submit')

async def main():
    if submit_button:
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
        Consider the following context before generating synthetic data: {user_context}
        Output should be in comma separarted csv format along with columns names from the above table using the above table as reference. 
        The API response text should start with the column names and it should not contain any leading text.
        """

        #Generate response using OpenAI API
        # response = openai.Completion.create(
        #         model="text-davinci-003",
        #         prompt=prompt
        #         )
        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=input_prompt,
            max_tokens = 2600,
            n = 1
        )
        
        api_string = response['choices'][0]['text']
        # st.write('Input prompt \n', prompt)

        # Comment the next line since the API response doesn't have to be shown in the web app
        st.write('API response \n',api_string)

        # Stripping the API response text to ensure no leading spaces are present before converting to a pandas dataframe
        stripped_api_string = api_string.strip()
    

        synthetic_df = pd.read_csv(StringIO(stripped_api_string), sep=",")

        # Remove the next 2 lines , they are just for checking the response in the Web app
        print("Printing final output table column names \n", synthetic_df.columns)
        print("Printing 1st line of value", synthetic_df.head(1))
        

        #Show the response in the web page
        st.write('Output: ',synthetic_df)
        

        # Download your results as a CSV file
        csv = synthetic_df.to_csv().encode('utf-8')
        st.download_button(
            label="Download data as CSV",
            data=csv,
            file_name='Synthetic_data_download_'+execution_time+'.csv',
            mime='text/csv',
        )

    else:
        st.write("Provide all the inputs and click 'Submit' to see the results")

#Run the main function using asyncio
if __name__ == "__main__":
    asyncio.run(main())

