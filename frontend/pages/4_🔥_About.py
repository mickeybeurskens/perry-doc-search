import streamlit as st
from perry.authentication import session_login_wrapper


def display_about(request_manager):
    st.subheader("🔥Brought to you by")
    st.title("Forge Fire AI Engineering")
    st.write("Forge Fire specializes in Generative AI, like language models and image generators, with a focus on AI safety.")
    st.write("Visit us at 🔥 [forgefire.dev](https://forgefire.dev) to learn more!")
    

if __name__ == "__main__":
    session_login_wrapper(display_about)
