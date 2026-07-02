from groq import Groq

from app.config import GROQ_API_KEY, GROQ_MODEL


class QAEngine:
    def __init__(self):
        self.client = Groq(api_key=GROQ_API_KEY)

    def build_context(self, retrieved_chunks: list[dict]) -> str:
        """
        Convert retrieved chunks into a prompt context.
        """

        context = []

        for index, chunk in enumerate(retrieved_chunks, start=1):

            metadata = chunk["metadata"]

            context.append(
                f"""
========== Source {index} ==========
File: {metadata['relative_path']}
Lines: {metadata['start_line']} - {metadata['end_line']}
Symbol: {metadata['symbol_name']}
Type: {metadata['symbol_type']}

{chunk['content']}
"""
            )

        return "\n".join(context)

    def build_prompt(
        self,
        question: str,
        context: str,
    ) -> str:

        return f"""
You are an expert Software Engineer.

You answer questions ONLY using the supplied code.

Rules:

1. Never hallucinate.

2. If the answer isn't present, reply:

"I could not find this information in the indexed repository."

3. Always mention

- File
- Line Number

4. Keep answers concise.

5. Explain code clearly.

User Question:

{question}

=========================
Repository Context
=========================

{context}
"""

    def answer(
        self,
        question: str,
        retrieved_chunks: list[dict],
    ) -> str:

        context = self.build_context(retrieved_chunks)

        prompt = self.build_prompt(
            question=question,
            context=context,
        )

        response = self.client.chat.completions.create(
            model=GROQ_MODEL,
            temperature=0.1,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )

        return response.choices[0].message.content


qa_engine = QAEngine()