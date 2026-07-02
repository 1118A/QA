import streamlit as st

from app.pipeline import pipeline

st.set_page_config(
    page_title="Codebase QA Bot",
    layout="wide",
)

st.title("💻 Codebase QA Bot")

repo_url = st.text_input(
    "GitHub Repository URL"
)

if st.button("Index Repository"):

    with st.spinner("Indexing repository..."):

        result = pipeline.index_repo(repo_url)

    st.success("Repository Indexed Successfully!")

    st.write(result)

st.divider()

question = st.text_input(
    "Ask a question about the repository"
)

if st.button("Ask"):

    with st.spinner("Searching code..."):

        result = pipeline.ask(question)

    st.markdown("## Answer")

    st.write(result["answer"])

    st.markdown("---")

    st.markdown("## Retrieved Chunks")

    for source in result["sources"]:

        meta = source["metadata"]

        with st.expander(
            f"{meta['relative_path']} ({meta['start_line']} - {meta['end_line']})"
        ):

            st.code(
                source["content"],
                language=meta["language"],
            )