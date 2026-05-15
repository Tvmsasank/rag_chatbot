import os
import faiss
import numpy as np
import requests

from dotenv import load_dotenv
load_dotenv()

from sentence_transformers import (
    SentenceTransformer,
    util
)

from database import (
    get_student_full_details
)

# =====================================================
# MEMORY
# =====================================================

conversation_state = {}

# =====================================================
# PATHS
# =====================================================

base_dir = os.path.dirname(os.path.abspath(__file__))

index_path = os.path.normpath(
    os.path.join(base_dir, "..", "data", "index.faiss")
)

chunk_path = os.path.normpath(
    os.path.join(base_dir, "..", "data", "chunks.npy")
)

print("Loading index from:", index_path)
print("Loading chunks from:", chunk_path)

# =====================================================
# LOAD VECTOR DATABASE
# =====================================================

index = faiss.read_index(index_path)

chunks = np.load(
    chunk_path,
    allow_pickle=True
)

# =====================================================
# EMBEDDING MODEL
# =====================================================

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

# =====================================================
# RETRIEVE DOCUMENTS
# =====================================================

def retrieve(query, k=3):

    q_emb = model.encode(
        [query],
        normalize_embeddings=True
    )

    D, I = index.search(
        np.array(q_emb),
        k
    )

    results = []

    for score, idx in zip(D[0], I[0]):

        if score > 0.30:
            results.append(chunks[idx])

    return results

# =====================================================
# SMART ANSWER EXTRACTION
# =====================================================

def extract_best_answer(query, docs):

    query_emb = model.encode(
        query,
        convert_to_tensor=True
    )

    best_score = 0
    best_answer = None

    for doc in docs:

        parts = doc.split("Q:")

        for p in parts:

            if "A:" in p:

                q_text = p.split("A:")[0].strip()

                a_text = p.split("A:")[1].strip()

                q_emb = model.encode(
                    q_text,
                    convert_to_tensor=True
                )

                score = util.cos_sim(
                    query_emb,
                    q_emb
                ).item()

                if score > best_score:

                    best_score = score
                    best_answer = a_text

    if best_score > 0.45:
        return best_answer

    return None

# =====================================================
# BUILD PROMPT
# =====================================================

def build_prompt(query, docs):

    context = "\n\n".join(docs)

    return f"""
You are a university AI assistant.

Answer ONLY from the given context.

If answer is not found, say:
"I couldn't find relevant information."

Context:
{context}

Question:
{query}

Answer:
"""

# =====================================================
# OLLAMA CALL
# =====================================================

def call_llm(prompt):

    try:

        res = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False
            },
            timeout=120
        )

        data = res.json()

        return data.get(
            "response",
            "No response generated."
        )

    except Exception as e:

        return f"LLM Error: {str(e)}"

# =====================================================
# GREETINGS
# =====================================================

def is_greeting(query):

    greetings = [
        "hi",
        "hello",
        "hey",
        "good morning",
        "good evening",
        "good afternoon"
    ]

    return query.lower().strip() in greetings

# =====================================================
# MAIN CHAT FUNCTION
# =====================================================

def ask(query):

    global conversation_state

    query_lower = query.lower()

    # =================================================
    # GREETING
    # =================================================

    if is_greeting(query):

        return (
            "Hello 👋\n\n"
            "I’m your university AI assistant.\n"
            "How may I help you today?",
            []
        )

    # =================================================
    # STUDENT DETAIL REQUESTS
    # =================================================

    student_keywords = [
        "fees",
        "fee due",
        "payment",
        "attendance",
        "result",
        "marks",
        "assignment",
        "library",
        "scholarship",
        "transport",
        "bus",
        "phone",
        "email",
        "address",
        "parent",
        "course",
        "batch",
        "details",
        "student details"
    ]

    if any(word in query_lower for word in student_keywords):

        conversation_state.clear()

        conversation_state["intent"] = "student_details"

        conversation_state["original_query"] = query_lower

        return (
            "Sure 👍 Please provide your hall ticket number.",
            []
        )

    # =================================================
    # WAITING FOR HALLTICKET
    # =================================================

    if (
        conversation_state.get("intent") == "student_details"
        and "hallticket" not in conversation_state
    ):

        hallticket = query.strip()

        result = get_student_full_details(hallticket)

        if not result:

            conversation_state.clear()

            return (
                "No student record found with this hall ticket number.",
                []
            )

        original_query = conversation_state["original_query"]

        conversation_state.clear()

        # =================================================
        # FEES
        # =================================================

        if (
            "fees" in original_query or
            "payment" in original_query or
            "due" in original_query
        ):

            return (
                f"""
Student Name: {result[2]}

Hall Ticket: {result[1]}

Course: {result[5]}

Batch: {result[6]}

Fees Due: ₹{result[3]}
""",
                []
            )

        # =================================================
        # ATTENDANCE
        # =================================================

        if "attendance" in original_query:

            return (
                f"""
Student Name: {result[2]}

Attendance: {result[4]}%
""",
                []
            )

        # =================================================
        # RESULT
        # =================================================

        if (
            "result" in original_query or
            "marks" in original_query
        ):

            return (
                f"""
Student Name: {result[2]}

Exam Result: {result[13]}
""",
                []
            )

        # =================================================
        # ASSIGNMENTS
        # =================================================

        if "assignment" in original_query:

            return (
                f"""
Student Name: {result[2]}

Assignments Pending: {result[14]}
""",
                []
            )

        # =================================================
        # LIBRARY
        # =================================================

        if "library" in original_query:

            return (
                f"""
Student Name: {result[2]}

Library Books Issued: {result[15]}
""",
                []
            )

        # =================================================
        # SCHOLARSHIP
        # =================================================

        if "scholarship" in original_query:

            return (
                f"""
Student Name: {result[2]}

Scholarship Status: {result[17]}
""",
                []
            )

        # =================================================
        # TRANSPORT
        # =================================================

        if (
            "transport" in original_query or
            "bus" in original_query
        ):

            return (
                f"""
Student Name: {result[2]}

Transport Route: {result[16]}
""",
                []
            )

        # =================================================
        # CONTACT DETAILS
        # =================================================

        if (
            "phone" in original_query or
            "email" in original_query or
            "address" in original_query
        ):

            return (
                f"""
Student Name: {result[2]}

Phone: {result[8]}

Email: {result[7]}

Address: {result[9]}
""",
                []
            )

        # =================================================
        # PARENT DETAILS
        # =================================================

        if "parent" in original_query:

            return (
                f"""
Student Name: {result[2]}

Parent Name: {result[11]}

Parent Contact: {result[12]}
""",
                []
            )

        # =================================================
        # FULL DETAILS
        # =================================================

        return (
            f"""
Student ID: {result[0]}

Name: {result[2]}

Hall Ticket: {result[1]}

Course: {result[5]}

Batch: {result[6]}

Fees Due: ₹{result[3]}

Attendance: {result[4]}%

Email: {result[7]}

Phone: {result[8]}

Address: {result[9]}

DOB: {result[10]}

Parent Name: {result[11]}

Parent Contact: {result[12]}

Exam Result: {result[13]}

Assignments Pending: {result[14]}

Library Books Issued: {result[15]}

Transport Route: {result[16]}

Scholarship Status: {result[17]}
""",
            []
        )

    # =================================================
    # RAG SEARCH
    # =================================================

    docs = retrieve(query)

    if docs:

        answer = extract_best_answer(
            query,
            docs
        )

        if answer:

            return answer, docs

        prompt = build_prompt(
            query,
            docs
        )

        return call_llm(prompt), docs

    # =================================================
    # FINAL FALLBACK
    # =================================================

    return (
        "Sorry, I couldn't find relevant information for your question.",
        []
    )

# =====================================================
# CLI TEST
# =====================================================

if __name__ == "__main__":

    while True:

        q = input("Ask: ")

        ans, docs = ask(q)

        print("\nAnswer:\n", ans)

        print("\nContext:\n", docs)