# --- Prompt Template Definition ---
# This is the primary RAG prompt template, as defined in our project plan.
# It instructs the LLM on its role, how to use the provided context, and what
# to do if the answer is not in the context.
RAG_PROMPT_TEMPLATE = """
You are a helpful and friendly AI assistant for the students of a college. Your name is 'CollegeBot'. Your goal is to provide accurate answers based ONLY on the context provided below.

**Instructions:**
1. Read the user's query and the provided context carefully.
2. Synthesize an answer directly from the information in the context. Do not use any prior knowledge.
3. If the context contains the answer, provide it in a clear and concise manner.
4. If the context does NOT contain enough information to answer the query, you MUST respond with the exact phrase: "I do not have enough information to answer that question." Do not try to guess the answer.
5. Be friendly and approachable in your tone.

**Context:**
---
{context}
---

**User Query:** {query}

**Answer:**
"""

def build_prompt(context: str, query: str) -> str:
    """
    Builds the final prompt string to be sent to the LLM using the RAG template.

    Args:
        context: The relevant text chunks retrieved from the vector store.
        query: The user's original question.

    Returns:
        A formatted string ready to be sent to the LLM.
    """
    # The .format() method replaces the {context} and {query} placeholders
    # in the template with the actual content.
    return RAG_PROMPT_TEMPLATE.format(context=context, query=query)

# --- Testing Block ---
if __name__ == "__main__":
    print("--- Testing Prompt Builder ---")
    
    # Create some sample context and a query to test the builder
    test_context = "The library is open from 9 AM to 9 PM on weekdays. The computer science department is in the Turing Building."
    test_query = "What are the library hours?"
    
    # Build the prompt using the function we want to test
    final_prompt = build_prompt(test_context, test_query)
    
    print("\n--- Generated Prompt ---")
    print(final_prompt)
    
    print("\n--- ✅ Prompt built successfully. ---")