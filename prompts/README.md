# RAG Prompts Documentation

## 1. System Prompt (`system_prompt.md`)
**Role:** The "Brain" of the NCERT Doubt-Solver.
**Use:** Passed as `system_instruction` to the LLM.

**Why it works (Judge-Friendly Explanation):**
This system prompt is designed to constrain the LLM to act strictly as an interpreter of the provided NCERT context. It explicitly forbids external knowledge, enforces strict citation formats, and handles multilingual requirements. This minimizes hallucination risk and ensures answers are verifiable against the textbook.

## 2. User Prompt Template (`rag_query_template.txt`)
**Role:** The dynamic frame for every user question.
**Use:** Filled with retrieved chunks and the user's question at runtime.

**Structure:**
```text
[CONTEXT START]
{RETRIEVED_CHUNKS}
[CONTEXT END]

USER QUESTION: {USER_QUESTION}
```

## 3. Shortened "Efficiency" System Prompt
If token limits are tight, use this compressed version:

```text
You are an NCERT Doubt-Solver. Answer ONLY from the provided context.
If the answer is missing, say "This topic is not covered in the NCERT textbook for this class."

Inputs: User Question, Retrieved Context.

Rules:
1. No outside knowledge.
2. English question -> English answer. Hindi question -> Hindi answer.
3. Cite strictly as: • Class <X> – <Subject> – Chapter <Y> – Page <Z>

Output Format:
Answer: <Explanation>
Citations: <Bulleted List of Pages Used>
```
