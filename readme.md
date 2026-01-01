# 🤖 AI SQL Agent Pro

**A Production-Grade, Self-Correcting Text-to-SQL Agent powered by Local LLMs.**

---

### 📸 Interface Preview

![frontend-image](image.png)

> The interface features a Glassmorphic Dark Mode design with real-time state visualization, syntax-highlighted SQL terminal, and interactive thinking indicators.

---

## 📖 Executive Summary

This project implements a robust **Autonomous Database Agent** that enables non-technical users to query complex PostgreSQL databases using natural language.

Unlike simple "wrapper" tools, this agent uses a **Cognitive Architecture** (LangGraph) to:

1. **Understand Intent:** Distinguishes between casual chat and data queries.
2. **Self-Correct:** If the generated SQL fails, the agent reads the error, fixes its own code, and retries automatically.
3. **Context Aware:** Remembers conversation history to resolve pronouns (e.g., _"What is **his** salary?"_).
4. **Real-Time Observability:** The frontend polls the backend to show the user exactly what the AI is thinking step-by-step.

All AI processing happens **locally** using **Ollama (Qwen 2.5-Coder)**, ensuring 100% data privacy.

---

## 🏗️ System Architecture & UML Diagrams

### 1. Deployment Diagram

This diagram illustrates how the application is containerized and deployed using Docker Compose.

```mermaid
graph TD
    subgraph "Docker Host (MacBook Air)"
        subgraph "Frontend Container"
            React[React App]
            Vite[Vite Server :5173]
        end

        subgraph "Backend Container"
            API[FastAPI Server :8000]
            Logic[LangGraph Engine]
            JobStore[In-Memory Job Store]
        end

        subgraph "Database Container"
            PG[(PostgreSQL :5432)]
            Schema[Employees Table]
        end

        subgraph "AI Engine Container"
            Ollama[Ollama Server :11434]
            Model[[Qwen 2.5-Coder 1.5B]]
        end
    end

    User((User)) -->|HTTP| Vite
    React -->|REST API| API
    API -->|Prompting| Ollama
    Ollama -->|Inference| Model
    API -->|SQL Execution| PG

```

### 2. Sequence Diagram (Async Polling)

We moved from synchronous waiting to an asynchronous **Job Queue pattern** to provide a better UX.

```mermaid
sequenceDiagram
    participant U as User (React)
    participant A as Backend API
    participant G as Background Worker
    participant D as Database

    U->>A: POST /query (Question)
    A->>G: Spawn Background Task
    A-->>U: Return { job_id: "123" }

    loop Every 500ms
        U->>A: GET /job/123
        A-->>U: Return { step: "generating_sql" }
    end

    G->>G: Generate SQL (LangGraph)
    G->>D: Execute SQL
    D-->>G: Result Rows
    G->>G: Update Job Store { status: "completed" }

    U->>A: GET /job/123
    A-->>U: Return { status: "completed", response: "..." }
    U->>U: Render Message & SQL Terminal

```

### 3. Activity Diagram (The "Brain")

This flow shows the decision-making process inside `app/graph.py`, including the **Self-Correction Loop**.

```mermaid
stateDiagram-v2
    [*] --> ClassifyIntent

    state intent_fork <<choice>>
    ClassifyIntent --> intent_fork

    intent_fork --> GeneralChat: Intent = "general"
    intent_fork --> FetchSchema: Intent = "database"

    GeneralChat --> [*]

    FetchSchema --> GenerateSQL
    GenerateSQL --> ExecuteSQL

    state check_error <<choice>>
    ExecuteSQL --> check_error

    check_error --> Summarize: Success
    check_error --> GenerateSQL: Error (Retry < 3)
    check_error --> Summarize: Error (Max Retries)

    Summarize --> [*]

```

### 4. Class Diagram (Backend Logic)

Structuring the code for modularity and type safety.

```mermaid
classDiagram
    class FastAPI_App {
        +start_query(req)
        +get_job_status(job_id)
        -run_graph_background(job_id, inputs)
    }

    class GraphState {
        +str question
        +List history
        +str schema
        +str sql_query
        +str error
        +int retry_count
    }

    class Nodes {
        +classify_input(state)
        +fetch_schema(state)
        +generate_sql(state)
        +execute_sql(state)
        +summarize(state)
    }

    class Tools {
        +get_schema()
        +run_query(sql)
        -_is_safe_query(sql)
    }

    FastAPI_App --> GraphState : Manages
    Nodes --> Tools : Uses
    Nodes -- GraphState : Modifies
```

### 5. Entity Relationship Diagram (ERD)

The optimized database schema designed for efficient querying without complex joins.

```mermaid
erDiagram
    EMPLOYEES {
        int id PK
        string name
        string department
        string role
        int salary
        int performance_score
        string location
        date join_date
        string manager_name
    }

```

---

## ⚡ Key Features

- **🛡️ Secure Guardrails:** The agent is restricted to `READ-ONLY` SQL permissions and sanitizes all inputs to prevent injection attacks.
- **🧠 Memory Injection:** The prompt dynamically retrieves the last `N` messages to maintain conversational context.
- **🏎️ Speed Optimized:** Uses the **Qwen 2.5-Coder (1.5B)** model, optimized to run on standard consumer hardware.
- **💅 Production UI:**
- Glassmorphism CSS
- Markdown Rendering
- Syntax-Highlighted SQL Terminal
- Animated "Thinking" Steps

---

## 🚀 Getting Started

### Prerequisites

- Docker & Docker Compose
- Node.js 18+ (Optional, for local dev)

### Installation

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/sql-agent-pro.git
cd sql-agent-pro

```

1. **Start the Stack**

```bash
docker-compose up -d --build

```

1. **Access the Application**

- Frontend: `http://localhost:5173`
- Backend Docs: `http://localhost:8000/docs`

---

## 🛠️ Tech Stack

| Component         | Technology            | Description                                     |
| ----------------- | --------------------- | ----------------------------------------------- |
| **Frontend**      | React + Vite          | Fast, modern web framework                      |
| **Styling**       | Tailwind CSS          | Utility-first styling with custom Glassmorphism |
| **Backend**       | FastAPI (Python)      | High-performance Async API                      |
| **Orchestration** | LangChain / LangGraph | State machine for AI logic                      |
| **LLM**           | Ollama (Qwen 2.5)     | Local AI Inference                              |
| **Database**      | PostgreSQL 15         | Relational Data Store                           |

---

**Developed with ❤️ by Jaspreet**
