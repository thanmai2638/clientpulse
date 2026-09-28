import os
import re
import json

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from hindsight_client import Hindsight
from groq import Groq
from pydantic import BaseModel


# ==========================================
# LOAD ENVIRONMENT VARIABLES
# ==========================================

load_dotenv()

HINDSIGHT_API_KEY = os.getenv("HINDSIGHT_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not HINDSIGHT_API_KEY:
    raise ValueError("HINDSIGHT_API_KEY is missing from .env")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is missing from .env")


# ==========================================
# CLIENTS
# ==========================================

hindsight = Hindsight(
    base_url="https://api.hindsight.vectorize.io",
    api_key=HINDSIGHT_API_KEY
)

groq = Groq(
    api_key=GROQ_API_KEY
)


# ==========================================
# FASTAPI
# ==========================================

app = FastAPI(title="ClientPulse")

templates = Jinja2Templates(
    directory="templates"
)


# ==========================================
# LOCAL INTERACTION TRACKER
# ==========================================

STATS_FILE = "client_stats.json"


def load_stats():

    if not os.path.exists(STATS_FILE):
        return {}

    try:
        with open(
            STATS_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except Exception:
        return {}


def save_stats(stats):

    with open(
        STATS_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            stats,
            file,
            indent=2
        )


def update_interaction_count(client_name):

    stats = load_stats()

    if client_name not in stats:

        stats[client_name] = {
            "interactions": 0
        }

    stats[client_name]["interactions"] += 1

    save_stats(stats)

    return stats[client_name]["interactions"]


# ==========================================
# CLIENT MEMORY BANK
# ==========================================

def get_bank_id(client_name):

    clean_name = client_name.lower().strip()

    clean_name = re.sub(
        r"[^a-z0-9]+",
        "-",
        clean_name
    )

    clean_name = clean_name.strip("-")

    return f"clientpulse-{clean_name}"


def ensure_bank(client_name):

    bank_id = get_bank_id(client_name)

    try:

        hindsight.create_bank(
            bank_id=bank_id,
            name=f"ClientPulse - {client_name}"
        )

    except Exception:
        pass

    return bank_id


# ==========================================
# REMOVE DUPLICATE MEMORIES
# ==========================================

def clean_memories(memories):

    unique_memories = []
    seen = set()

    for memory in memories:

        text = memory.strip()

        if not text:
            continue

        normalized = re.sub(
            r"\s+",
            " ",
            text.lower()
        )

        if normalized in seen:
            continue

        seen.add(normalized)

        unique_memories.append(text)

    return unique_memories


# ==========================================
# CLEAN AI RESPONSE
# ==========================================

def clean_ai_response(text):

    if not text:
        return ""

    text = re.sub(
        r"<br\s*/?>",
        "\n",
        text,
        flags=re.IGNORECASE
    )

    text = text.replace("**", "")
    text = text.replace("__", "")

    lines = text.splitlines()

    cleaned_lines = []

    for line in lines:

        line = line.strip()

        if "|" in line:

            parts = [
                part.strip()
                for part in line.strip("|").split("|")
            ]

            parts = [
                part for part in parts
                if part
            ]

            if parts:
                line = " - ".join(parts)

        cleaned_lines.append(line)

    text = "\n".join(cleaned_lines)

    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text
    )

    return text.strip()


# ==========================================
# GENERATE CLIENT PROFILE
# ==========================================

def generate_profile(client_name, memory_text):

    prompt = f"""
You are analyzing the long-term memory of a client.

Client:
{client_name}

Remembered information:
{memory_text}

Create a concise client profile.

Return ONLY valid JSON in this exact structure:

{{
  "preferences": ["..."],
  "dislikes": ["..."],
  "budget": "...",
  "feedback": ["..."],
  "important_notes": ["..."]
}}

Rules:

- Only use information explicitly present.
- Never invent information.
- If a category has no information, use [].
- If budget is unknown, use "Not specified".
"""

    response = groq.chat.completions.create(

        model="openai/gpt-oss-20b",

        messages=[
            {
                "role": "system",
                "content": "Return only valid JSON."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0.1
    )

    content = response.choices[0].message.content.strip()

    try:

        content = re.sub(
            r"```json|```",
            "",
            content,
            flags=re.IGNORECASE
        ).strip()

        return json.loads(content)

    except Exception:

        return {
            "preferences": [],
            "dislikes": [],
            "budget": "Not specified",
            "feedback": [],
            "important_notes": []
        }


# ==========================================
# HOME
# ==========================================

@app.get("/", response_class=HTMLResponse)
def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "request": request
        }
    )


# ==========================================
# ANALYZE INTERACTION
# ==========================================

@app.post("/analyze")
def analyze(data: dict):

    client_name = data.get(
        "client_name",
        "Unknown Client"
    ).strip()

    interaction = data.get(
        "interaction",
        ""
    ).strip()

    if not interaction:

        return {
            "error": "Please enter a client interaction."
        }


    # ======================================
    # INTERACTION COUNT
    # ======================================

    interaction_count = update_interaction_count(
        client_name
    )


    # ======================================
    # CLIENT MEMORY BANK
    # ======================================

    bank_id = ensure_bank(client_name)


    # ======================================
    # STORE IN HINDSIGHT
    # ======================================

    hindsight.retain(

        bank_id=bank_id,

        content=f"""
Client: {client_name}

Client interaction:
{interaction}
"""
    )


    # ======================================
    # RECALL MEMORY
    # ======================================

    memory_result = hindsight.recall(

        bank_id=bank_id,

        query=f"""
What important information do we remember
about {client_name}?

Focus on:

- preferences
- dislikes
- budget
- previous requests
- feedback
- deadlines
- commitments
- things the client liked
- things the client disliked
"""
    )


    # ======================================
    # EXTRACT MEMORIES
    # ======================================

    raw_memories = []

    for memory in memory_result.results:

        raw_memories.append(
            memory.text
        )


    memories = clean_memories(
        raw_memories
    )


    memory_text = "\n".join(
        f"- {memory}"
        for memory in memories
    )


    # ======================================
    # GENERATE CLIENT PROFILE
    # ======================================

    profile = generate_profile(
        client_name,
        memory_text
    )


    # ======================================
    # GENERATE PERSONALIZED RESPONSE
    # ======================================

    prompt = f"""
You are ClientPulse, an AI client relationship
agent for freelancers and agencies.

Your key ability is remembering client history
and using it to personalize future responses.

CLIENT:
{client_name}

NEW INTERACTION:
{interaction}

REMEMBERED CLIENT INFORMATION:
{memory_text}

CLIENT PROFILE:
{json.dumps(profile, indent=2)}

Create a personalized response.

IMPORTANT:

- Use only known information.
- Never invent prices.
- Never invent deadlines.
- Never invent deliverables.
- Never invent meetings.
- Never invent technical requirements.
- Never invent business requirements.
- If information is missing, say it needs confirmation.

Use these sections:

PROJECT OVERVIEW

CLIENT PREFERENCES

BUDGET

HOW MEMORY INFLUENCED THIS RESPONSE

NEXT STEPS

Use simple bullet points.

Do NOT use tables.
Do NOT use "|" characters.
Do NOT use HTML.
Do NOT use markdown bold.

Keep it concise.
"""

    response = groq.chat.completions.create(

        model="openai/gpt-oss-20b",

        messages=[

            {
                "role": "system",
                "content": (
                    "You are ClientPulse, a professional "
                    "client relationship memory agent."
                )
            },

            {
                "role": "user",
                "content": prompt
            }

        ],

        temperature=0.1
    )


    ai_response = clean_ai_response(
        response.choices[0].message.content
    )


    # ======================================
    # WHY THIS RESPONSE?
    # ======================================

    why_prompt = f"""
Explain in 3 short bullet points how the
remembered client information influenced
the response.

Client:
{client_name}

New interaction:
{interaction}

Memory:
{memory_text}

Only mention information actually present.
Do not invent anything.
"""

    why_result = groq.chat.completions.create(

        model="openai/gpt-oss-20b",

        messages=[
            {
                "role": "user",
                "content": why_prompt
            }
        ],

        temperature=0.1
    )


    why_memory = clean_ai_response(
        why_result.choices[0].message.content
    )


    # ======================================
    # BEFORE MEMORY RESPONSE
    # ======================================

    before_prompt = f"""
Respond to this client request as a generic
AI assistant WITHOUT using any previous client
memory.

Client:
{client_name}

Request:
{interaction}

Keep it short and generic.
Do not invent client preferences.
"""

    before_result = groq.chat.completions.create(

        model="openai/gpt-oss-20b",

        messages=[
            {
                "role": "user",
                "content": before_prompt
            }
        ],

        temperature=0.1
    )


    before_response = clean_ai_response(
        before_result.choices[0].message.content
    )


    # ======================================
    # RETURN EVERYTHING
    # ======================================

    return {

        "client": client_name,

        "response": ai_response,

        "memories": memories,

        "profile": profile,

        "interaction_count": interaction_count,

        "memory_count": len(memories),

        "why_memory": why_memory,

        "before_response": before_response

    }


# ==========================================
# ASK CLIENTPULSE
# ==========================================

class AskRequest(BaseModel):

    client_name: str
    question: str


@app.post("/ask")
def ask_clientpulse(data: AskRequest):

    client_name = data.client_name.strip()

    question = data.question.strip()


    if not client_name:

        return {
            "answer": "Please enter a client name."
        }


    if not question:

        return {
            "answer": "Please enter a question."
        }


    # ======================================
    # GET CLIENT MEMORY BANK
    # ======================================

    bank_id = ensure_bank(client_name)


    # ======================================
    # RECALL RELEVANT HINDSIGHT MEMORY
    # ======================================

    memory_result = hindsight.recall(

        bank_id=bank_id,

        query=question
    )


    # ======================================
    # EXTRACT MEMORIES
    # ======================================

    raw_memories = []

    for memory in memory_result.results:

        raw_memories.append(
            memory.text
        )


    memories = clean_memories(
        raw_memories
    )


    if memories:

        memory_text = "\n".join(
            f"- {memory}"
            for memory in memories
        )

    else:

        memory_text = "No relevant memories were found."


    # ======================================
    # GENERATE ANSWER
    # ======================================

    ask_prompt = f"""
You are ClientPulse, an AI client relationship
agent with long-term memory.

Answer the user's question using ONLY the
information retrieved from Hindsight.

CLIENT:
{client_name}

RELEVANT HINDSIGHT MEMORIES:
{memory_text}

USER QUESTION:
{question}

RULES:

- Use only information supported by the memories.
- Never invent client information.
- Never guess.
- Do not use information that is not in the memories.
- If the memories do not contain the answer, say:
  "I don't have enough information in the client's
  memory to answer that."
- Keep the answer concise and natural.
"""


    result = groq.chat.completions.create(

        model="openai/gpt-oss-20b",

        messages=[

            {
                "role": "system",
                "content": (
                    "You are ClientPulse. "
                    "Answer questions using the "
                    "client's retrieved Hindsight memories."
                )
            },

            {
                "role": "user",
                "content": ask_prompt
            }

        ],

        temperature=0.1
    )


    answer = clean_ai_response(
        result.choices[0].message.content
    )


    # ======================================
    # RETURN ANSWER
    # ======================================

    return {

        "client": client_name,

        "question": question,

        "answer": answer,

        "memories_used": memories

    }