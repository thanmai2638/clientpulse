# ClientPulse 🧠

## AI Client Relationship Agent powered by Hindsight Memory

ClientPulse is an AI-powered client relationship agent for freelancers and agencies.

It learns from client interactions, remembers preferences, feedback, budgets, dislikes, and important requests, and uses that accumulated memory to generate increasingly personalized responses.

---

## 🎯 Problem

Freelancers and agencies interact with clients across multiple conversations.

Important details such as:

- Client preferences
- Budget
- Feedback
- Likes and dislikes
- Previous requests
- Important requirements

can easily be forgotten or scattered across conversations.

This can lead to repetitive questions, generic responses, and weaker client relationships.

---

## 💡 Solution

ClientPulse gives an AI agent long-term memory.

Instead of treating every client interaction as a new conversation, ClientPulse:

1. Receives a client interaction
2. Stores useful information in Hindsight
3. Recalls relevant memories when needed
4. Uses recalled context to generate a personalized response
5. Continues learning from future interactions

### Core idea

**Learn → Remember → Recall → Personalize → Learn again**

---

## 🧠 Hindsight Memory

Hindsight is the core memory layer of ClientPulse.

Client interactions are retained in a dedicated memory bank for each client.

When a new request or question arrives, ClientPulse retrieves relevant memories from Hindsight and provides them as context to the AI.

This allows the system to build a continuously growing understanding of the client.

---

## ✨ Key Features

### 💬 Client Interaction

Add new client requirements, preferences, feedback, budgets, and requests.

### 🧠 Long-Term Memory

ClientPulse stores important interaction history using Hindsight.

### 🔍 Relevant Memory Recall

Hindsight retrieves memories relevant to the current request.

### 👤 Client Memory Profile

ClientPulse builds a profile containing:

- Preferences
- Dislikes
- Budget
- Feedback
- Important notes

### 💬 Ask ClientPulse

Ask questions about a client using their accumulated memory.

Examples:

> What does this client dislike?

> What is their budget?

> What feedback did they give about the previous proposal?

The answer is generated using relevant memories retrieved from Hindsight.

### 🔄 Before vs After Memory

The dashboard demonstrates the difference between a generic response and a response personalized using client memory.

### 📈 Memory Growth

The dashboard tracks interactions learned and relevant memories retrieved.

---

## 🏗️ How It Works

```text
             Client Interaction
                     │
                     ▼
             ┌──────────────┐
             │ ClientPulse  │
             │   AI Agent   │
             └──────┬───────┘
                    │
                    ▼
             ┌──────────────┐
             │  Hindsight   │
             │    Memory    │
             └──────┬───────┘
                    │
              Store + Recall
                    │
                    ▼
             ┌──────────────┐
             │     Groq     │
             │  AI Reasoning│
             └──────┬───────┘
                    │
                    ▼
          Personalized Response
## 🛠️ Tech Stack

- **Python** — Core backend logic
- **FastAPI** — Backend API and application server
- **Hindsight** — Long-term memory for client interactions
- **Groq** — AI reasoning and response generation
- **HTML** — Frontend structure
- **CSS** — UI design and animations
- **JavaScript** — Frontend interactions and API calls
- **Jinja2** — HTML templating
- **Git & GitHub** — Version control and collaboration
## 📁 Project Structure

```text
clientpulse/
│
├── app.py                  # FastAPI backend and AI logic
├── requirements.txt        # Python dependencies
├── client_stats.json       # Interaction statistics
├── test_hindsight.py       # Hindsight connection testing
├── .gitignore              # Protects environment files
│
└── templates/
    └── index.html          # ClientPulse frontend
## ⚙️ Setup

### 1. Clone the repository

```bash
git clone https://github.com/thanmai2638/clientpulse.git
cd clientpulse
## 🎬 Demo Flow

Use a fictional client such as **Nova Studios**.

### Interaction 1

> We prefer minimal designs.

### Interaction 2

> Our budget for the website is $500.

### Interaction 3

> We don't like excessive animations.

### Interaction 4

> The previous proposal was too technical.

### Interaction 5

> We want our new website to feel modern but simple.

Then use **Ask ClientPulse**:

> What does Nova Studios dislike?

ClientPulse recalls the relevant memory from Hindsight and generates an answer based on the stored client history.
## 🔐 Security

API keys are stored in the `.env` file and excluded from Git using `.gitignore`.

Never publish API keys, credentials, or other sensitive information in the repository.
## 🚀 Future Scope

- Client communication history
- Email and messaging integrations
- Automatic follow-up suggestions
- Proposal generation
- Client relationship insights
- Team collaboration
- CRM integrations
- More advanced memory-based recommendations
## 👥 Project

**ClientPulse — AI Client Relationship Agent**

Built as a hackathon prototype focused on AI agents that learn using long-term memory.
## 📜 License

This project is created as a hackathon prototype.