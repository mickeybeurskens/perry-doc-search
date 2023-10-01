import streamlit as st
from perry.authentication import session_login_wrapper


def display_about(request_manager):
    st.subheader("Brought to you by Forge Fire 🔥")
    st.title("About Perry")
    st.write(
        "Perry is a tool for exploring the question answering capabilities of Generative AI, specifically language models."
    )
    st.write(
        "This full stack AI application was built by Mickey Beurskens at 🔥 [Forge Fire AI Engineering](https://forgefire.dev). Forge Fire specializes in Generative AI, like language models and image generators, with a focus on AI safety."
    )
    st.header("Contact")
    st.write("If you'd like to speak with me about this project, or are interested in my research and development services, please reach out to me through email or LinkedIn.")
    st.write("🔥 __Email__: info@forgefire.dev for my research and development services.")
    st.write("🔗 __LinkedIn__: [Mickey Beurskens](https://www.linkedin.com/in/mickey-beurskens/).")
    st.write("🐙 __Github__: Check out [Github](github.com/mickeybeurskens) for other research and projects.")
    st.write("☕ __Mickey.Coffee:__ I also write about AI and other topics on my [personal blog](https://mickey.coffee).")


if __name__ == "__main__":
    session_login_wrapper(display_about)
