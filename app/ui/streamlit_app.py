import streamlit as st

from app.pipeline import pipeline


st.set_page_config(
    page_title="Codebase QA Bot",
    page_icon="🤖",
    layout="wide",
)


st.title("🤖 Codebase QA Bot")
st.write(
    "Ask natural language questions over a GitHub repository and get answers with file + line citations."
)


with st.sidebar:
    st.header("📦 Repository Indexing")

    repo_url = st.text_input(
        "GitHub Repository URL",
        placeholder="https://github.com/psf/requests",
    )

    index_button = st.button("📥 Index Repository")

    if index_button:
        if not repo_url.strip():
            st.warning(
                """
⚠️ **Repository URL is required**

Please enter a valid GitHub repository URL.

Example:

`https://github.com/psf/requests`
"""
            )
            st.stop()

        with st.spinner("🔄 Cloning repository, parsing code, creating embeddings, and indexing..."):
            try:
                result = pipeline.index_repo(repo_url.strip())

                st.success("✅ Repository indexed successfully!")

                col1, col2 = st.columns(2)

                with col1:
                    st.metric(
                        "Files Indexed",
                        result.get("files_indexed", 0),
                    )

                with col2:
                    st.metric(
                        "Chunks Indexed",
                        result.get("chunks_indexed", 0),
                    )

                if result.get("message"):
                    st.info(result["message"])

            except ValueError as e:
                st.warning(f"⚠️ {str(e)}")

            except Exception as e:
                error_message = str(e)

                if "Repository URL is empty" in error_message:
                    st.warning(
                        "⚠️ Please enter a valid GitHub repository URL before indexing."
                    )

                elif "InvalidGitRepositoryError" in error_message:
                    st.error(
                        "❌ Invalid GitHub repository. Please check the repository URL."
                    )

                elif "Authentication failed" in error_message:
                    st.error(
                        "❌ GitHub authentication failed. Please use a public repository or configure GitHub token support."
                    )

                elif "Quota exceeded" in error_message:
                    st.error(
                        "❌ Chroma quota exceeded. Try a smaller repository or reduce chunk size."
                    )

                else:
                    st.error(
                        "❌ Something went wrong while indexing the repository."
                    )

                    with st.expander("Show technical details"):
                        st.code(error_message)


st.divider()

st.subheader("💬 Ask a Question")

question = st.text_input(
    "Question",
    placeholder="Where are HTTP adapters handled?",
)

ask_button = st.button("Ask")

if ask_button:
    if not question.strip():
        st.warning("⚠️ Please enter a question before asking.")
        st.stop()

    with st.spinner("🔍 Searching codebase and generating answer..."):
        try:
            result = pipeline.ask(question.strip())

            st.success("✅ Answer generated successfully.")

            st.subheader("Answer")
            st.markdown(result.get("answer", "No answer generated."))

            sources = result.get("sources", [])

            if sources:
                st.subheader("Sources")

                for source in sources:
                    metadata = source.get("metadata", {})

                    file_name = metadata.get("relative_path", "Unknown file")
                    start_line = metadata.get("start_line", "?")
                    end_line = metadata.get("end_line", "?")
                    symbol_name = metadata.get("symbol_name", "")
                    symbol_type = metadata.get("symbol_type", "")
                    score = round(source.get("score", 0), 4)

                    title = f"{file_name}:{start_line}-{end_line}"

                    if symbol_name:
                        title += f" | {symbol_type}: {symbol_name}"

                    with st.expander(title):
                        st.write(f"**Score:** {score}")
                        st.code(source.get("content", ""), language=metadata.get("language", ""))

            else:
                st.info("No source chunks found.")

        except ValueError as e:
            st.warning(f"⚠️ {str(e)}")

        except Exception as e:
            error_message = str(e)

            if "Please reduce the length" in error_message:
                st.error(
                    "❌ The retrieved code context is too large for the LLM. Reduce TOP_K or chunk size."
                )

            elif "GROQ_API_KEY" in error_message:
                st.error(
                    "❌ Groq API key is missing. Please add GROQ_API_KEY in your .env file."
                )

            else:
                st.error(
                    "❌ Something went wrong while generating the answer."
                )

                with st.expander("Show technical details"):
                    st.code(error_message)