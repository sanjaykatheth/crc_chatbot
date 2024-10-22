import time
import streamlit as st
import pandas as pd
from utils.db_utils import connect_to_mssql
from utils.setup import setup_connexion, setup_session_state
from utils.images.display_logo import display_logo
import math
from dotenv import load_dotenv
load_dotenv()
# Set the page config as the first command
st.set_page_config(page_title="AI Chat", layout="wide")

from utils.UserChat import UserChat, UserChatList
from utils.vanna_calls import (
    generate_sql_cached,
    generate_plotly_code_cached,
    generate_plot_cached,
)
from collections import OrderedDict

from utils.login import login  
from utils.error.error_logging import store_error_log
from utils.history.chat_history import get_global_suggested_questions
from utils.history.chat_history import (
    get_existing_chat_data,
    store_chat_history_mssql,
    retrieve_chat_history_mssql,
    get_default_questions,
    get_user_questions_count,
    get_suggested_questions,
    get_default_questions_by_email,
    get_default_questions_by_department
)
from streamlit_modal import Modal
from utils.change_password import change_password
from utils.utility import logout, navigate,check_login_state

def store_chat_locally(chat_session_object):
    """Store a chat session object in the session state."""
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = UserChatList()
    
    st.session_state.chat_history.AddHistory(chat_session_object)
    
    print(st.session_state.chat_history)

def retrieve_local_chat():
    """Retrieve chat history from the session state."""
    return st.session_state.get('chat_history', UserChatList()).chat_history

def clear_local_chat():
    """Clear all chat history from the session state."""
    if 'chat_history' in st.session_state:
        st.session_state.pop('chat_history')  # Remove the chat history from session state


# Initialize session state and other setup functions
def setup_session_state():
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = UserChatList()
    if "search_query" not in st.session_state:
        st.session_state.search_query = ""
        st.session_state.suggested_questions = []
    if "vanna_ai_search_data" not in st.session_state:
        st.session_state.vanna_ai_search_data = ""
    if 'options' not in st.session_state:
        st.session_state.options = ""
    if "input_query" not in st.session_state:
        st.session_state.input_query = ""

def set_question(question):
    st.session_state["my_question"] = question

def retrieve_chat_history_mssql():
    connection = connect_to_mssql()
    query = "SELECT user_question, sql_query, sql_result, plot_code FROM chat_history_collection WHERE created_at >= DATEADD(hour, -24, GETDATE())"
    chat_history_df = pd.read_sql(query, connection)
    
    # Convert the SQL result back into a DataFrame
    chat_history_df['sql_result'] = chat_history_df['sql_result'].apply(lambda x: pd.read_json(x) if x is not None else None)
    
    connection.close()
    return chat_history_df

def get_sql_result_from_query(sql_query):
    connection = connect_to_mssql()
    result_df = pd.read_sql(sql_query, connection)

    connection.close()
    return result_df
    

def chat_with_vanna(my_question):
    question_placeholder = st.empty()
    # question_placeholder.markdown(f"<h6 style='color: #555; margin: 0;'>You asked: {my_question}</h6>", unsafe_allow_html=True)
 
    if my_question:

        existing_chat_data = get_existing_chat_data(my_question)

        current_chat = UserChat()
        set_question(my_question)
        current_chat.user_id = st.session_state.get("user_id")
        current_chat.user_department = st.session_state.get("user_department")
        current_chat.user_email = st.session_state.get("user_email")
        current_chat.user_question=my_question

        
        if existing_chat_data is not None:
            print("== existing data")
            
            current_chat.sql = existing_chat_data['sql_query']
            current_chat.sql_result = get_sql_result_from_query(current_chat.sql)
            current_chat.plot_code = existing_chat_data['plot_code']
            # if st.session_state.get("show_sql", True):
            #     assistant_message_sql = st.chat_message("assistant", avatar="https://ask.vanna.ai/static/img/vanna_circle.png")
            #     assistant_message_sql.code(existing_chat_data['sql_query'], language="sql", line_numbers=True)

            # if existing_chat_data['sql_result'] is not None:
            #     df = existing_chat_data['sql_result']
            #     st.session_state["df"] = df
            #     if st.session_state.get("show_table", True):
            #         assistant_message_table = st.chat_message("assistant", avatar="https://ask.vanna.ai/static/img/vanna_circle.png")
            #         assistant_message_table.dataframe(df.head(10) if len(df) > 10 else df)

            # if existing_chat_data['plot_code'] and st.session_state.get("show_plot", True):
            #     fig = generate_plot_cached(code=existing_chat_data['plot_code'], df=df)
            #     if fig:
            #         assistant_message_chart = st.chat_message("assistant", avatar="https://ask.vanna.ai/static/img/vanna_circle.png")
            #         assistant_message_chart.plotly_chart(fig, key=f"plot_{my_question}_{st.session_state.get('user_id', '')}")
            #     else:
            #         assistant_message_error = st.chat_message("assistant", avatar="https://ask.vanna.ai/static/img/vanna_circle.png")
            #         assistant_message_error.error("I couldn't generate a chart")

            store_chat_locally(current_chat)
            
        else:
            print("== new  data")
            # current_chat = UserChat()
            # current_chat.user_question = my_question
            # set_question(my_question)
            # current_chat.user_id = st.session_state.get("user_id")
            # current_chat.user_department = st.session_state.get("user_department")
            # current_chat.user_email = st.session_state.get("user_email")

            # user_message = st.chat_message("user")
            # user_message.write(f"{my_question}")
            sql = generate_sql_cached(question=my_question)
            current_chat.sql = sql

            if sql:
                # if st.session_state.get("show_sql", True):
                #     assistant_message_sql = st.chat_message("assistant", avatar="https://ask.vanna.ai/static/img/vanna_circle.png")
                #     assistant_message_sql.code(sql, language="sql", line_numbers=True)

                try:
                    connection = connect_to_mssql()
                    df = pd.read_sql(sql, connection)
                    connection.close()

                    st.session_state["df"] = df
                    current_chat.sql_result = df

                    if df is not None:
                        # if st.session_state.get("show_table", True):
                        #     assistant_message_table = st.chat_message("assistant", avatar="https://ask.vanna.ai/static/img/vanna_circle.png")
                        #     assistant_message_table.dataframe(df.head(10) if len(df) > 10 else df)

                        code = generate_plotly_code_cached(question=my_question, sql=sql, df=df)
                        current_chat.plot_code = code

                        # if code and st.session_state.get("show_plot", True):
                        #     assistant_message_chart = st.chat_message("assistant", avatar="https://ask.vanna.ai/static/img/vanna_circle.png")
                        #     fig = generate_plot_cached(code=code, df=df)
                        #     if fig:
                        #         assistant_message_chart.plotly_chart(fig)
                        #     else:
                        #         assistant_message_chart.error("I couldn't generate a chart")

                    store_chat_history_mssql(current_chat)
                    store_chat_locally(current_chat)
                    st.session_state.suggested_questions = get_default_questions()  # Or however you populate them


                except Exception as e:
                    error_message = str(e)
                    assistant_message_error = st.chat_message("assistant", avatar="https://ask.vanna.ai/static/img/vanna_circle.png")
                    assistant_message_error.error(f"An error occurred while processing your request: {error_message}")
                    user_email = current_chat.user_email
                    user_department = current_chat.user_department
                    store_error_log(my_question, error_message, user_email, user_department)

    st.session_state["my_question"] = None

def get_suggested_questions(keyword):
    user_email = st.session_state.get("user_email")
    if not user_email:
        return []

    connection = connect_to_mssql()
    query = """
        SELECT DISTINCT user_question 
        FROM chat_history_collection
        WHERE user_question LIKE ?
        AND user_email = ?
    """
    
    keyword = f"%{keyword}%"
    suggested_questions_df = pd.read_sql(query, connection, params=[keyword, user_email])
    connection.close()
    
    return suggested_questions_df['user_question'].tolist() if not suggested_questions_df.empty else []

def CreatingLocalHistoryChat():
    chat_history_df = retrieve_local_chat()
    # print("===== chat_history_df", chat_history_df)

    for idx, chat in enumerate(chat_history_df):
        if chat.user_question:
            user_message = st.chat_message("user")
            user_message.write(chat.user_question)

        if chat.sql and st.session_state.get("show_sql", True):
            assistant_message_sql = st.chat_message("assistant", avatar="https://ask.vanna.ai/static/img/vanna_circle.png")
            assistant_message_sql.code(chat.sql, language="sql", line_numbers=True)

        if chat.sql_result is not None:
            df = chat.sql_result
            if st.session_state.get("show_table", True):
                assistant_message_table = st.chat_message("assistant", avatar="https://ask.vanna.ai/static/img/vanna_circle.png")
                assistant_message_table.dataframe(df.head(10) if len(df) > 10 else df)

        if chat.plot_code and st.session_state.get("show_plot", True):
            fig = generate_plot_cached(code=chat.plot_code, df=df)
            if fig:
                assistant_message_chart = st.chat_message("assistant", avatar="https://ask.vanna.ai/static/img/vanna_circle.png")
                # Use a unique key by combining index and user question
                assistant_message_chart.plotly_chart(fig, key=f"chat_plot_{idx}_{chat.user_question}")
            else:
                assistant_message_error = st.chat_message("assistant", avatar="https://ask.vanna.ai/static/img/vanna_circle.png")
                assistant_message_error.error("I couldn't generate a chart")

def CreatingChatHistoryMSSQL():
    chat_history_df = retrieve_chat_history_mssql()
    # for _, row in chat_history_df.iterrows():
    #     user_question = row['user_question'] if row['user_question'] is not None else "No question available"
    #     st.sidebar.write("- " + user_question)

    # if chat_history_df.empty:
    #     return

    for _, chat in chat_history_df.iterrows():
        if chat['user_question']:
            user_message = st.chat_message("user")
            user_message.write(chat['user_question'])

        if chat['sql_query'] and st.session_state.get("show_sql", True):
            assistant_message_sql = st.chat_message("assistant", avatar="https://ask.vanna.ai/static/img/vanna_circle.png")
            assistant_message_sql.code(chat['sql_query'], language="sql", line_numbers=True)

        if chat['sql_result'] is not None:
            df = chat['sql_result']
            if st.session_state.get("show_table", True):
                assistant_message_table = st.chat_message("assistant", avatar="https://ask.vanna.ai/static/img/vanna_circle.png")
                assistant_message_table.dataframe(df.head(10) if len(df) > 10 else df)

        if chat['plot_code'] and st.session_state.get("show_plot", True):
            fig = generate_plot_cached(code=chat['plot_code'], df=df)
            if fig:
                assistant_message_chart = st.chat_message("assistant", avatar="https://ask.vanna.ai/static/img/vanna_circle.png")
                assistant_message_chart.plotly_chart(fig, key=f"chat_plot_{chat['user_question']}_{_}")
            else:
                assistant_message_error = st.chat_message("assistant", avatar="https://ask.vanna.ai/static/img/vanna_circle.png")
                assistant_message_error.error("I couldn't generate a chart")
                    
def display_output_settings():
    st.sidebar.markdown("<h3 style='font-size: 20px;'>🔧 Output Settings</h3>", unsafe_allow_html=True)
    
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        st.sidebar.toggle("Show SQL", value=True, key="show_sql")
    with col2:
        st.sidebar.toggle("Show Table", value=True, key="show_table")
    
    st.sidebar.toggle("Show Chart", value=True, key="show_plot")

def update_search_query():
    st.session_state.search_query = st.session_state.input_query
    if st.session_state.search_query:
        st.session_state.suggested_questions = get_suggested_questions(st.session_state.search_query)
    else:
        st.session_state.suggested_questions = get_default_questions()
    

def paginate_questions(questions, page, per_page=5):
    start = (page - 1) * per_page
    end = start + per_page
    return questions[start:end]

def update_pagination_buttons():
    total_questions = len(st.session_state.filtered_questions)
    total_pages = (total_questions + 4) // 5
    cols = st.sidebar.columns(2)
    if cols[0].button("Previous", disabled=st.session_state.page == 1):
        st.session_state.page = max(1, st.session_state.page - 1)
        st.rerun()
    if cols[1].button("Next", disabled=st.session_state.page >= total_pages):
        st.session_state.page = min(total_pages, st.session_state.page + 1)
        st.rerun()
        
        

def setup_sidebar():
    st.sidebar.markdown("<h3 style='font-size: 20px;'> Your Suggested Questions</h3>", unsafe_allow_html=True)
    setup_session_state()

    user_email = st.session_state.get("user_email")
    user_department = st.session_state.get("user_department")

    question_count = get_user_questions_count(user_email)
    user_questions = get_default_questions_by_email(user_email)
    
    # Initialize suggested questions
    suggested_questions = OrderedDict.fromkeys(user_questions, None)

    # Retrieve department questions based on question count
    if question_count < 6:
        department_questions = get_default_questions_by_department(user_department,user_email)
    else:
        department_questions = user_questions

    # Add department questions to suggested questions if not already present
    for question in department_questions:
        suggested_questions.setdefault(question, None)

    st.session_state.suggested_questions = list(suggested_questions.keys())
    st.session_state.filtered_questions = list(suggested_questions.keys())
    
    # Handle search query
    search_query = st.sidebar.text_input(
        "Type your question here:",
        placeholder="Search for a question...",
        key="input_query_sidebar",  
        on_change=update_search_query
    )

    input_query = st.session_state.get("input_query_sidebar", "").lower()
    
    if input_query:
        filtered_questions = [q for q in st.session_state.suggested_questions if input_query in q.lower()]
        
        print("=== math.ceil(len(filtered_questions)/5)",math.ceil(len(filtered_questions)/5))
        if(st.session_state.page>math.ceil(len(filtered_questions)/5)):
            st.session_state.page = 1
    else:
        filtered_questions = st.session_state.suggested_questions
    
    st.session_state.filtered_questions=filtered_questions

    if "page" not in st.session_state:
        st.session_state.page = 1

    try:
        st.session_state.page = int(st.session_state.page)
    except ValueError:
        st.session_state.page = 1

    paginated_questions = paginate_questions(filtered_questions, int(st.session_state.page))
    st.markdown("""
    <style>
    [role=radiogroup] {
        gap: 1.3rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    if paginated_questions:
        question_options = [f"{index + 1}. {question}" for index, question in enumerate(paginated_questions)]
        selected_question = st.sidebar.radio("Select a question:", question_options, index=None)
        if selected_question:
             selected_question_text = selected_question.split(". ", 1)[1]
             st.session_state["my_question"] = selected_question_text
             chat_with_vanna(selected_question_text)  
        update_pagination_buttons()

def display_top_bar():
    """Display the top bar with the change password button."""
    modal = change_password()
    st.empty()
    col1, col2 = st.columns([7.5, 2.5])
    
    with col1:
        pass
    
    with col2:
        button_col1, button_col2 = st.columns(2)

        with button_col1:
            if st.button("Change Password", key="change_password"):
                modal.open()

        with button_col2:
            if st.button("Logout", key="logout"):
                logout()
                clear_local_chat()
                navigate("login")
                st.rerun()

def main():
    """Main application logic."""
    setup_connexion()
    setup_session_state()

    display_output_settings()
    # setup_sidebar()
    # CreatingChatHistoryMSSQL()
    
    # print("testing")
    input_ai_data = st.chat_input("Ask me a question about your data", key="vanna_ai_search_key")
    if input_ai_data:
        chat_with_vanna(input_ai_data)
    setup_sidebar()
    CreatingLocalHistoryChat()
    

if __name__ == '__main__':
    query_params = st.query_params
    # print("==== query_params",query_params)
    page = query_params.get("page", "login")
    logged_in, user_data = check_login_state()
    if logged_in and page == "home":
        st.session_state.update({
            "logged_in": True,
            "user_email": user_data.get("email"),
            "user_department": user_data.get("department")
        })
        display_top_bar()
        display_logo()
        main()
    else:
        navigate("login")
        login()
