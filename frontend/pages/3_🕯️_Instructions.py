import streamlit as st
from perry.authentication import session_login_wrapper


def display_instructions(request_manager):
    st.title("Welcome to Perry!")
    st.write(
        "Perry allows you to quickly and efficiently work with conversational AI and PDF files."
        "Use Perry to brainstorm, quickly summarize or rewrite texts or automate reporting."
    )
    st.info(
        "__🔥 Tip:__ We'll give you some prompts to get started, but it's useful start experimenting with them yourself."
        " Write down the most useful prompts somewhere and use them to get better custom results over time!"
    )
    st.subheader("Getting started")
    st.write("A quick summary of the steps before we start:")
    st.markdown(
        """
    1. _Upload some documents_
    2. _Create a conversation and choose an agent_
    3. _Start chatting with your agent!_
    """
    )
    st.subheader("1. Upload documents 🗂️")
    st.write(
        "First, we need  documents to work with. You can upload PDF files going to the `Documents` page."
        " Just follow the steps there and you'll be good to go! If you ever want to delete a document,"
        " you can do that from the `Documents` page as well."
    )
    st.info(
        "Filling in the __description__ for each document is important! It will be used by the agent to understand the contents and answer your questions."
    )

    st.subheader("2. Create a conversation 🤖")
    st.write(
        "Now that we have some documents to work with, we can create a conversation."
        " A conversation is a session with an agent that will help you work with your documents."
        " You can create a conversation by going to the `Conversations` page and clicking the __Create__ button."
        " You'll be asked to fill in some details about your conversation and choose settings for your agent!"
        " If you'd like to delete a conversation, you can do that from the `Conversations` page as well."
    )
    st.info(
        "There are multiple agents to choose from. Each agent handles documents differently. Experiment to see which one works best for you!"
    )

    st.subheader("3. Start chatting with your agent! 💬")
    st.write(
        "Now that you've created a conversation, you can start chatting with your agent on the `Chat` page!"
        " Just click on the conversation in the sidebar and you'll be able to start chatting."
        " You will see information about the session, including selected documents, in the sidebar and can switch conversations from there as well."
    )

    st.write(
        "That's it! You're ready to start working with your documents. If you have any questions, feel free to reach out to us at [🔥Forge Fire AI Engineering](forgefire.dev)."
    )

    st.subheader("4. Bonus: Prompt Library 📚")
    st.write(
        "If you're not sure what to ask your agent, use one of the following prompts to get started!"
    )
    st.write("__Summarize a document:__")
    st.write(
        "Use this style of prompting to summarize a document or go through documents quickly."
    )
    st.code(
        """
    Take a look at all the uploaded documents and summarize the main points of
    each document. Do so in bullet points, and give at least three bullet
    points per document.
    """,
        language="text",
    )

    st.write("__Reason:__")
    st.write("Let the agent explain why something is the case.")
    st.code(
        """
    Before answering a question, first summarize the question 
    in your own words. Then outline a way to solve the
    question. Explicitly suggest improvements to your solution.
    Only then answer the question.
    """,
        language="text",
    )

    st.write("__Q&A:__")
    st.write(
        "Use this style of prompting to ask questions and get answers in a specific format by proving an example."
    )
    st.code(
        """
    Q: This is the format of the question.
    A: This is the answering style I want to use.

    Q: This is another question.
    A: 
    """,
        language="text",
    )

    st.write("__Brainstorm:__")
    st.write("Use this style of prompting to brainstorm ideas.")
    st.code(
        """
    Brainstorm ideas for a new product. Write down at least 10 ideas.
    Use the theme "The Answer To Everything Is 42". Be creative and 
    link ideas from different domains together. Take a risk! 
    """,
        language="text",
    )


if __name__ == "__main__":
    session_login_wrapper(display_instructions)
