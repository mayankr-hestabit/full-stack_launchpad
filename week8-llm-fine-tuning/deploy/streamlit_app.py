import uuid

import httpx
import streamlit as st


# ---------------------------------------------------------
# CONFIG
# ---------------------------------------------------------

API_URL = "http://127.0.0.1:8000"


st.set_page_config(
    page_title="Local LLM Assistant",
    page_icon="🤖",
    layout="centered",
)


# ---------------------------------------------------------
# SESSION STATE
# ---------------------------------------------------------

if "chat_session_id" not in st.session_state:

    st.session_state.chat_session_id = str(
        uuid.uuid4()
    )


if "messages" not in st.session_state:

    st.session_state.messages = []


# ---------------------------------------------------------
# TITLE
# ---------------------------------------------------------

st.title("🤖 Local Fine-Tuned LLM")

st.caption(
    "Qwen2.5-1.5B Fine-Tuned + GGUF Q4_0 + llama.cpp"
)


# ---------------------------------------------------------
# SIDEBAR SETTINGS
# ---------------------------------------------------------

st.sidebar.header("Generation Settings")


temperature = st.sidebar.slider(
    "Temperature",
    min_value=0.0,
    max_value=2.0,
    value=0.7,
    step=0.1,
)


top_p = st.sidebar.slider(
    "Top-p",
    min_value=0.1,
    max_value=1.0,
    value=0.9,
    step=0.05,
)


top_k = st.sidebar.slider(
    "Top-k",
    min_value=1,
    max_value=100,
    value=40,
)


max_tokens = st.sidebar.slider(
    "Max Tokens",
    min_value=32,
    max_value=1024,
    value=256,
    step=32,
)


system_prompt = st.sidebar.text_area(
    "System Prompt",
    value=(
        "You are a helpful coding and "
        "software engineering assistant."
    ),
)


# ---------------------------------------------------------
# TABS
# ---------------------------------------------------------

generate_tab, chat_tab = st.tabs(
    [
        "Generate",
        "Chat",
    ]
)


# =========================================================
# GENERATE TAB
# =========================================================

with generate_tab:

    st.subheader("Single Prompt Generation")

    prompt = st.text_area(
        "Enter your prompt",
        placeholder="Example: Explain Docker in simple terms.",
        height=150,
    )

    stream_output = st.checkbox(
        "Stream response",
        value=True,
        key="generate_stream",
    )

    if st.button(
        "Generate Response",
        type="primary",
    ):

        if not prompt.strip():

            st.warning("Please enter a prompt.")

        else:

            payload = {
                "prompt": prompt,
                "system_prompt": system_prompt,
                "temperature": temperature,
                "top_p": top_p,
                "top_k": top_k,
                "max_tokens": max_tokens,
                "stream": stream_output,
            }

            try:

                if stream_output:

                    output_box = st.empty()

                    complete_response = ""

                    with httpx.stream(
                        "POST",
                        f"{API_URL}/generate",
                        json=payload,
                        timeout=None,
                    ) as response:

                        response.raise_for_status()

                        for text in response.iter_text():

                            complete_response += text

                            output_box.markdown(
                                complete_response + "▌"
                            )

                    output_box.markdown(
                        complete_response
                    )

                else:

                    response = httpx.post(
                        f"{API_URL}/generate",
                        json=payload,
                        timeout=300,
                    )

                    response.raise_for_status()

                    result = response.json()

                    st.markdown(
                        result["response"]
                    )

                    st.caption(
                        f"Request ID: "
                        f"{result['request_id']}"
                    )

            except Exception as error:

                st.error(
                    f"API Error: {error}"
                )


# =========================================================
# CHAT TAB
# =========================================================

with chat_tab:

    left, right = st.columns(
        [4, 1]
    )

    with left:

        st.subheader("Chat Mode")

    with right:

        if st.button("New Chat"):

            st.session_state.chat_session_id = str(
                uuid.uuid4()
            )

            st.session_state.messages = []

            st.rerun()


    # -----------------------------------------------------
    # DISPLAY CHAT HISTORY
    # -----------------------------------------------------

    for message in st.session_state.messages:

        with st.chat_message(
            message["role"]
        ):

            st.markdown(
                message["content"]
            )


    # -----------------------------------------------------
    # USER INPUT
    # -----------------------------------------------------

    user_input = st.chat_input(
        "Ask something..."
    )


    if user_input:

        st.session_state.messages.append(
            {
                "role": "user",
                "content": user_input,
            }
        )

        with st.chat_message("user"):

            st.markdown(user_input)


        payload = {

            "message": user_input,

            "session_id":
                st.session_state.chat_session_id,

            "system_prompt":
                system_prompt,

            "temperature":
                temperature,

            "top_p":
                top_p,

            "top_k":
                top_k,

            "max_tokens":
                max_tokens,

            "stream":
                True,
        }


        with st.chat_message("assistant"):

            response_box = st.empty()

            complete_response = ""

            try:

                with httpx.stream(
                    "POST",
                    f"{API_URL}/chat",
                    json=payload,
                    timeout=None,
                ) as response:

                    response.raise_for_status()

                    for text in response.iter_text():

                        complete_response += text

                        response_box.markdown(
                            complete_response + "▌"
                        )

                response_box.markdown(
                    complete_response
                )

            except Exception as error:

                complete_response = (
                    f"API Error: {error}"
                )

                response_box.error(
                    complete_response
                )


        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": complete_response,
            }
        )