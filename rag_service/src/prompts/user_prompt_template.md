# NCERT Doubt-Solver - User Prompt Template

This template is inserted into the conversation after the System Prompt.

---

## 📝 PROMPT STRUCTURE

```text
[CONTEXT START]
{RETRIEVED_CHUNKS}
[CONTEXT END]

USER QUESTION: {USER_QUESTION}

Please answer the question based strictly on the context above.
```

## 🔍 VARIABLE DEFINITIONS

### `{RETRIEVED_CHUNKS}`
A formatted string containing the top-K retrieved chunks.

**Format per chunk:**
```text
[NCERT SOURCE]
Class: {class_num}
Subject: {subject}
Language: {language}
Chapter: {chapter}
Page: {page}

{text_content}

---
```

### `{USER_QUESTION}`
The raw question text provided by the student.

---

## 💡 EXAMPLE FILLED PROMPT

```text
[CONTEXT START]
[NCERT SOURCE]
Class: 6
Subject: Science
Language: English
Chapter: Food: Where Does It Come From?
Page: 1

Plants are potential sources of food ingredients like grains, cereals, vegetables and fruits. Animals provide us with milk, meat products and eggs.

---
[NCERT SOURCE]
Class: 6
Subject: Science
Language: English
Chapter: Components of Food
Page: 12

Carbohydrates mainly provide energy to our body. Fats also give us energy. In fact, fats give much more energy as compared to the same amount of carbohydrates.

---
[CONTEXT END]

USER QUESTION: What gives us more energy, fats or carbohydrates?

Please answer the question based strictly on the context above.
```
