# AskSQL 🔍⛃  
**Analyze and Talk to Large Databases in Natural Language**

AskSQL is an intelligent natural language interface for interacting with large-scale relational databases. It enables users to perform CRUD operations, generate ER diagrams, and analyze trends or insights—all by simply asking questions in plain English. Powered by a multi-agent architecture and enhanced with LLM capabilities, AskSQL bridges the gap between raw database structures and intuitive human communication.

<img src="./assets/asksql-connect.png" alt="AskSQL Overview" />

---

## 🧠 Agent Flow

```mermaid
graph TD

%% Main Nodes
UserQuery["User Query"]
Orchestrator["Chief Database<br>Orchestrator"]

%% Primary Roles
SchemaAnalyst["Senior Database Schema<br>Analyst"]
DBManager["Senior Database Manager"]
DataAnalyst["Senior Data Analyst"]
ERDSpecialist["ERD Diagram Specialist"]

%% Sub-tasks
ExtractSchema["Extract Schema Details"]
SchemaDetails["Schema Details"]
SQLExecutor["SQLExecutor Tool - Read<br>Only SQL"]
AnalyzeTrends["Analyze Data & Trends"]
Insights["Insights & Analysis"]
GenerateERD["Generate ERD Diagram"]
MermaidERD["MermaidJS ERD Diagram"]
Formatter["Response Formatting Agent"]
FinalResponse["Final Formatted Response"]

%% Connections
UserQuery --> Orchestrator

Orchestrator --> SchemaAnalyst
Orchestrator --> DBManager
Orchestrator --> DataAnalyst
Orchestrator --> ERDSpecialist

SchemaAnalyst --> ExtractSchema --> SchemaDetails --> SQLExecutor
DBManager --> SQLExecutor
DataAnalyst --> AnalyzeTrends --> Insights --> SQLExecutor
ERDSpecialist --> GenerateERD --> MermaidERD --> SQLExecutor

SQLExecutor --> Formatter --> FinalResponse
```

---

## 🚀 Features

### 📄 Perform CRUD Operations  
**Database Used:** IMDb  
<img src="./assets/crud.png" alt="CRUD Operations" />

---

### 📊 Perform Data Analysis  
**Database Used:** [Mystery Database (KnightLab)](https://mystery.knightlab.com/)  
<img src="./assets/analysis.png" alt="Data Analysis" />

---

### 🧩 Generate ERD Diagram  
**Database Used:** IMDb  
<img src="./assets/erd.png" alt="ERD Diagram" />

---

## ⚙️ Installation

Clone the repository:

```bash
git clone https://github.com/0xMihirK/AskSQl
cd ./AskSQL
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Set your Gemini API Key from [Google AI Studio](https://aistudio.google.com/) in the `.env` file:

```
GEMINI_API_KEY=your_api_key_here
```

Run the Streamlit app:

```bash
streamlit run ./app.py
```

---
