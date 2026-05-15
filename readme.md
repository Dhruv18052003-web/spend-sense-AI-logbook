# Spend Sense AI Logbook

A conversational AI-powered personal expense tracker. Log expenses, add income, and query your spending history — all through natural language chat. Supports English, Hindi, and mixed-language input.

## Features

- **Chat-based expense logging** — Type "Chips 50" or "Auto 120" and the AI logs it automatically
- **Income tracking** — "Salary aayi 25000" adds money to your wallet
- **Natural language queries** — "Last month food ka kharcha?" returns aggregated spending data
- **Multi-agent AI pipeline** — Intent classification, semantic resolution, query scoping, and response generation
- **Semantic categorization** — Expenses are auto-classified into reusable semantic concepts (e.g., `food`, `transport`)
- **Broad & specific queries** — "How much on food?" expands to include snacks, groceries, etc.
- **Multilingual support** — Responds in the same language and script as the user's input
- **Wallet balance tracking** — Real-time balance displayed in the chat UI
- **JWT authentication** — Secure login with automatic token refresh

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Django 6.0, Django REST Framework |
| AI/LLM | OpenAI GPT-5-mini |
| Database | PostgreSQL |
| Auth | SimpleJWT (access + refresh tokens) |
| Frontend | React 19, Vite 7, Tailwind CSS 4 |
| HTTP Client | Axios (with refresh token interceptor) |
| Routing | React Router v7 |

## Architecture

```
User Message
     │
     ▼
┌─────────────────┐
│ Intent Classifier│ ─── Classifies into: log_expense | add_money | query_analysis | greetings | chitchat
└────────┬────────┘
         │
         ├── log_expense ──► Expense Extractor → Expense Normalizer → Semantic Resolver → Save Record
         │
         ├── add_money ────► Add Money Extractor → Update Wallet Balance
         │
         ├── query_analysis► Query Extractor → Semantic Resolver → Query Scope Agent → Semantic Expansion → DB Query → Response Generator
         │
         ├── greetings ────► Greeting Response Generator
         │
         └── chitchat ─────► Chitchat Response Generator (redirects to app usage)
```

Each agent is a focused LLM call with strict JSON output contracts and fallback handling.

## Project Structure

```
spend-sense-AI-logbook/
├── backend/
│   ├── chat/                    # Core chat logic & AI agents
│   │   ├── intent_classifier.py
│   │   ├── expense_extractor.py
│   │   ├── expense_normalizer.py
│   │   ├── add_money_extractor.py
│   │   ├── query_extractor.py
│   │   ├── query_scope_agent.py
│   │   ├── semantic_expansion_agent.py
│   │   ├── semantic_resolver.py
│   │   ├── response_generator.py
│   │   ├── query_response_generator.py
│   │   ├── gretting_response.py
│   │   ├── chitchat_response.py
│   │   ├── views.py            # ChatView API endpoint
│   │   └── models.py           # ChatLogs
│   ├── records/                 # Expense records model
│   ├── semantic/                # SemanticConcept model
│   ├── users/                   # Auth, registration, wallet
│   └── spend_sense_project/     # Django settings & root URLs
├── frontend/
│   ├── src/
│   │   ├── pages/              # Login, Signup, Chat
│   │   ├── services/           # API client, auth, chat services
│   │   └── context/            # AuthContext
│   └── package.json
└── readme.md
```

## Getting Started

### Prerequisites

- Python 3.12+
- Node.js 20+
- PostgreSQL
- OpenAI API key

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
# Create a .env file in the backend directory:
# OPENAI_API_KEY=your_openai_api_key
# DATABASE_URL=postgres://user:password@localhost:5432/spend_sense

# Run migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Start server
python manage.py runserver
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

The frontend runs on `http://localhost:5173` and the backend API on `http://localhost:8000`.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/login/` | Get JWT access & refresh tokens |
| POST | `/api/auth/refresh/` | Refresh access token |
| POST | `/api/users/register/` | Register new user |
| POST | `/api/users/logout/` | Blacklist refresh token |
| GET | `/api/chat/intent-test/` | Fetch chat history |
| POST | `/api/chat/intent-test/` | Send message (triggers AI pipeline) |

## Usage Examples

```
User: "Chai 20"
AI: "Noted — ₹20 spent on chai."

User: "Salary aayi 25000"
AI: "₹25,000 added. Your balance is now ₹24,980."

User: "Last week food pe kitna kharch hua?"
AI: "Last 7 days mein food pe ₹1,240 kharch hue."

User: "List my expenses today"
AI: "Today's expenses: Chai ₹20, Auto ₹120, Lunch ₹180."
```

## How the AI Pipeline Works

1. **Intent Classifier** — Determines what the user wants (log expense, add money, query, greeting, or chitchat)
2. **Extractors** — Pull structured data (amount, label, date) from natural language
3. **Semantic Resolver** — Maps raw labels to reusable semantic concepts, creating new ones when needed
4. **Query Scope Agent** — Decides if a query is "broad" (food → all food subcategories) or "specific"
5. **Semantic Expansion** — For broad queries, finds all related semantic concepts in the database
6. **Response Generator** — Converts structured results into natural language, matching the user's language and script

## License

This project is for personal/educational use.
