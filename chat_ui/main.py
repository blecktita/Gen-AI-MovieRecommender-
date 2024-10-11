import json
import os
from typing import Iterator

import httpx
import streamlit as st
from httpx_sse import connect_sse

API_URL = os.getenv("API_URL", "http://localhost:8000")
API_CLIENT = httpx.Client(base_url=API_URL)


def initialize_chat_history():
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def chat():
    # React to user input
    if user_prompt := st.chat_input("What is up?"):
        # Display user message in chat message container
        st.chat_message("user").markdown(user_prompt)
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": user_prompt})

        with st.chat_message("assistant"):
            with st.empty():
                with st.spinner("Generating Response"):
                    for response in get_response(user_prompt):
                        st.markdown(response, unsafe_allow_html=True)
            # Print again outside the empty container
            st.markdown(response, unsafe_allow_html=True)
            final_response = response

        # Add assistant response to chat history
        st.session_state.messages.append(
            {"role": "assistant", "content": final_response}
        )


def get_response(user_prompt: str) -> Iterator[str]:
    response_message = ""
    with connect_sse(
        client=API_CLIENT,
        url="stream_events",
        method="POST",
        json={"input": {"question": user_prompt}},
        timeout=httpx.Timeout(None, connect=3.0),
    ) as event_source:
        try:
            event_source.response.raise_for_status()
            for event in event_source.iter_sse():
                if event.event == "data":
                    data = json.loads(event.data)
                    match data:
                        case {"event": "on_chat_model_stream"}:
                            response_message += data["data"]["chunk"]["content"]
                            yield response_message
                        # case {"event": "on_chain_end"}:
                        #     output_messages: list[str] = data["data"]["output"][
                        #         "messages"
                        #     ]
                        #     for message in output_messages:
                        #         if message["type"] == "ai":
                        #             response_message = message["content"]
                        #             yield response_message
                elif event.event == "end":
                    break
                elif event.event == "error":
                    response_message = "Error during chat invocation"
        except httpx.HTTPStatusError:
            response_message = "Error during chat invocation"

    return response_message


if __name__ == "__main__":
    st.title("Movie Recommender Chat")
    initialize_chat_history()
    chat()
