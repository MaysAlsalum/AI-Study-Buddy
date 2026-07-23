# AAASE-CAPSTONE-Teem-AI Study Buddy

An AI-powered multi-agent study assistant that helps students transform study materials into concise summaries, generate quizzes, and create personalized study plans using Large Language Models (LLMs).

---

## 👥 Team

| Member | GitHub | Contribution |
|---------|---------|--------------|
| Member 1 | @MaysAlsalum | Summarization Agent, Security Layer, LangGraph Workflow |
| Member 2 | @RazanAlrashed | Quiz Generation Agent |
| Member 3 | @Rimas-Alhazmi | Study Planner Agent, Frontend Development & UI Integration |

---


## 📖 Problem Statement

Students often spend a significant amount of time organizing study materials before they can begin effective learning. Reading long documents, identifying important concepts, creating practice questions, and planning study schedules are repetitive and time-consuming tasks.

AI Study Buddy addresses this problem by automatically analyzing uploaded study materials and providing structured learning support. Instead of manually creating summaries, quizzes, and study plans, students receive personalized learning resources within seconds.

The project was developed to demonstrate how multiple AI agents can collaborate to solve a real educational problem while maintaining modularity, scalability, and security.


---


## 🤖 How the Agent Solves the Problem

AI Study Buddy follows a multi-agent workflow where each agent is responsible for a specific learning task. The workflow is orchestrated using **LangGraph**, allowing agents to collaborate while sharing a common state.

### Workflow

1. **Study Material Upload**
   - The user uploads a PDF document through the frontend.
   - The system extracts the text from the PDF.

2. **Security Inspection**
   - Before any AI processing begins, the uploaded content is inspected for prompt injection attempts and suspicious patterns.
   - If malicious content is detected, the workflow stops and returns an appropriate security message.

3. **Summarization Agent**
   - Reads the extracted study material.
   - Generates a concise summary.
   - Identifies the main topics.
   - Extracts important terms and their definitions.

4. **Quiz Generation Agent**
   - Uses the summary and extracted topics to generate multiple-choice questions.
   - Produces explanations and correct answers for each question.

5. **Study Planner Agent**
   - Creates a personalized study schedule based on:
     - Study duration
     - Difficulty level
     - Extracted topics

6. **Final Response**
   - The system combines the outputs from all agents and returns:
     - Summary
     - Key topics
     - Definitions
     - Quiz
     - Personalized study plan

### Agentic Behavior

The project demonstrates agentic AI by using multiple specialized agents coordinated through **LangGraph**. Each agent performs an independent task while sharing information through a common state object. The workflow supports sequential and parallel execution, enabling agents to collaborate efficiently without duplicating responsibilities.

The Summarization Agent prepares the learning material, while the Quiz Generation Agent and Study Planner Agent operate on the summarized knowledge to produce personalized educational outputs. This modular architecture makes the system scalable, maintainable, and easy to extend with additional agents in the future.



----


## 🏗️ Architecture

AI Study Buddy follows a modular multi-agent architecture built with **LangGraph**. Each agent has a single responsibility and communicates through a shared state object (`StudyState`).

### Workflow Architecture

```text
                    +----------------+
                    |   Upload PDF   |
                    +--------+-------+
                             |
                             v
                  +---------------------+
                  |   Extract PDF Text  |
                  +----------+----------+
                             |
                             v
                  +---------------------+
                  | Security Inspection |
                  +----------+----------+
                             |
                Safe         |        Malicious
                 |           |             |
                 |           |             v
                 |           |     Block Request
                 |           |
                 v
         +----------------------+
         | Summarization Agent  |
         +----------+-----------+
                    |
        +-----------+------------+
        |                        |
        v                        v
+------------------+    +------------------+
| Quiz Agent       |    | Study Planner    |
+--------+---------+    +--------+---------+
         |                       |
         +-----------+-----------+
                     |
                     v
          +-----------------------+
          |   Final JSON Output   |
          +-----------------------+
```

### Components

- **Frontend**
  - Allows users to upload study materials and view generated results.

- **PDF Processing**
  - Extracts readable text from uploaded PDF documents before AI processing begins.

- **Security Layer**
  - Detects prompt injection attempts and suspicious input before interacting with the language model.

- **Summarization Agent**
  - Produces a concise summary.
  - Extracts key topics.
  - Identifies important definitions.

- **Quiz Generation Agent**
  - Creates multiple-choice & Short-Answer questions with explanations based on the summarized content.

- **Study Planner Agent**
  - Generates a personalized study schedule according to the user's preferences.

- **Shared State (StudyState)**
  - Stores information exchanged between all agents during workflow execution.

- **LLM (OpenRouter)**
  - Powers all AI agents using Large Language Models through a unified interface.

The modular architecture allows each agent to operate independently while sharing information through a centralized workflow, making the system scalable, maintainable, and easy to extend with additional educational agents.


---




## ⚙️ Tech Stack

### Backend

| Technology | Purpose | Why We Chose It |
|------------|---------|-----------------|
| **Python 3.10+** | Backend development | Widely used for AI applications and provides strong support for agent frameworks and API development. |
| **LangGraph** | Multi-agent workflow orchestration | Enables stateful coordination between specialized agents and supports sequential and parallel execution. |
| **LangChain** | LLM integration and prompt handling | Simplifies interaction with language models and provides reusable components for AI workflows. |
| **LangChain OpenAI** | OpenAI-compatible model integration | Allows the backend to communicate with OpenRouter through an OpenAI-compatible interface. |
| **OpenRouter API** | Large Language Model access | Provides access to multiple LLMs through a unified API and allows flexible model selection. |
| **FastAPI** | Backend API | Provides a high-performance REST API with automatic Swagger documentation. |
| **Uvicorn** | ASGI server | Runs the FastAPI application during local development and testing. |
| **PyPDF** | PDF text extraction | Extracts readable text from uploaded PDF documents before AI processing. |
| **python-dotenv** | Environment variable management | Loads API keys and configuration values securely from a local `.env` file. |
| **Requests** | HTTP communication | Supports communication with external APIs and services when required. |
| **python-multipart** | File upload handling | Enables FastAPI to receive uploaded PDF files through multipart form requests. |

### Frontend

| Technology | Purpose | Why We Chose It |
|------------|---------|-----------------|
| **React** | User interface development | Supports reusable components and dynamic rendering for the study assistant interface. |
| **Vite** | Frontend development and build tool | Provides a fast development server and efficient production builds. |
| **JavaScript / JSX** | Frontend logic and components | Used to build interactive pages and connect the user interface with the backend API. |
| **HTML5** | Application structure | Provides the base structure for the frontend application. |
| **CSS3** | Styling and responsive design | Used to create a clear and user-friendly interface across different screen sizes. |
| **Fetch API / HTTP Requests** | Backend communication | Sends uploaded files and user preferences to the FastAPI backend and receives generated results. |

### Development and Testing Tools

| Technology | Purpose |
|------------|---------|
| **Git and GitHub** | Version control, collaboration, and capstone submission. |
| **VS Code** | Development environment for both frontend and backend code. |
| **Swagger UI** | Testing and documenting FastAPI endpoints. |
| **Pytest / Python Test Scripts** | Testing agents, workflow behavior, PDF processing, and the security layer. |

### Why This Stack?

AI Study Buddy uses a full-stack, multi-agent architecture. **LangGraph** coordinates the Summarization, Quiz Generation, and Study Planner agents through a shared state. **OpenRouter** provides flexible access to large language models, while **FastAPI** exposes the agent workflow through a structured backend API.

The frontend is built with **React and Vite**, providing a responsive and interactive user experience for uploading PDF files, configuring study preferences, and viewing summaries, quizzes, and study plans. **PyPDF** handles document extraction, while the security layer validates the uploaded content before it reaches the language model.



---


## 🚀 Installation & Running the Project

### 1. Clone the Repository

```bash
git clone https://github.com/<your-username>/AI-Study-Buddy.git
cd AI-Study-Buddy
```

---

### 2. Backend Setup

Create and activate a virtual environment:

```bash
python -m venv .venv
```

**Windows**

```bash
.venv\Scripts\activate
```

**macOS / Linux**

```bash
source .venv/bin/activate
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file from the example:

```bash
cp .env.example .env
```

or on Windows:

```bash
copy .env.example .env
```

Update the `.env` file with your OpenRouter API key:

```env
OPENROUTER_API_KEY=your_api_key
MODEL_NAME=your_model_name
```

Start the FastAPI server:

```bash
uvicorn backend.main:app --reload
```

The backend will be available at:

```
http://127.0.0.1:8000
```

Swagger API documentation:

```
http://127.0.0.1:8000/docs
```

---

### 3. Frontend Setup

Navigate to the frontend folder:

```bash
cd Frontend
```

Install dependencies:

```bash
npm install
```

Run the development server:

```bash
npm run dev
```

The frontend will be available at:

```
http://localhost:5173
```

---

### 4. Using the Application

1. Open the frontend in your browser.
2. Upload a PDF study document.
3. Select the desired study preferences.
4. Submit the document for processing.
5. View the generated:
   - Summary
   - Key Topics
   - Definitions
   - Quiz (Multiple Choice & Short Answer)
   - Personalized Study Plan


---


## 🎥 Demonstration

The project demonstration showcases the complete workflow of **AI Study Buddy**, including:

- Uploading a PDF study document.
- Extracting text from the uploaded PDF.
- Performing security inspection to detect prompt injection attempts.
- Generating a concise summary.
- Extracting key topics and important definitions.
- Creating multiple-choice and short-answer quiz questions.
- Generating a personalized study plan.
- Displaying the final results through the frontend interface.

### Demo Video

📺 **Watch the full project demonstration here:**

**Video Link:**  
[https://your-demo-video-link](https://drive.google.com/file/d/1E2O8RU1x-PWE6K3EqqgKFLrUm8c6_Cxy/view?usp=sharing)

---


## 📁 Project Structure

```text
AAASE-CAPSTONE-Teem-AI-Study-Buddy/
│
├── backend/
│   ├── agents/
│   │   ├── quiz_generator.py
│   │   ├── study_planner.py
│   │   └── summarizer.py
│   │
│   ├── core/
│   │   ├── llm.py
│   │   ├── state.py
│   │   └── workflow.py
│   │
│   └── main.py
│
├── Frontend/
│   ├── src/
│   │   ├── context/
│   │   ├── data/
│   │   ├── pages/
│   │   ├── styles/
│   │   ├── App.jsx
│   │   └── main.jsx
│   │
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
│
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

### Directory Overview

| Directory | Description |
|-----------|-------------|
| **backend/** | Contains the FastAPI backend and AI workflow. |
| **backend/agents/** | Implements the Summarization, Quiz Generation, and Study Planner agents. |
| **backend/core/** | Contains the LangGraph workflow, shared state, and LLM configuration. |
| **backend/main.py** | Entry point for the FastAPI application. |
| **Frontend/** | React-based frontend application. |
| **Frontend/src/pages/** | Contains the application's pages, including Login, Dashboard, Summary, Quiz, Results, and Study Plan. |
| **Frontend/src/context/** | Manages shared application state using React Context. |
| **Frontend/src/data/** | Stores mock data and frontend resources. |
| **Frontend/src/styles/** | Contains the application's CSS styling. |
| **requirements.txt** | Lists the Python dependencies required for the backend. |
| **.env.example** | Example environment variables needed to configure the project. |
| **README.md** | Project documentation, setup instructions, and usage guide. |


---


## 🚧 Limitations & Future Work

### Current Limitations

- The system currently accepts **PDF documents only** as study material.
- The quality of the generated summary, quiz, and study plan depends on the clarity and structure of the uploaded document.
- The application relies on an internet connection and access to the configured Large Language Model through OpenRouter.
- The current security layer focuses on detecting prompt injection and suspicious input patterns, but no security mechanism can guarantee protection against every possible attack.
- The study plan is generated from the uploaded material and user preferences, but it does not adapt dynamically based on the student's learning progress.

### Future Work

Future improvements for AI Study Buddy include:

- Supporting additional document formats such as Word (.docx), PowerPoint (.pptx), and plain text files.
- Adding user authentication and personalized study history.
- Tracking student progress and generating adaptive study plans based on previous performance.
- Expanding the quiz agent to support more question types and difficulty levels.
- Integrating Retrieval-Augmented Generation (RAG) to improve accuracy when processing large study materials.
- Enhancing the security layer with more advanced prompt injection detection and automated risk analysis.
- Deploying the application to a cloud platform for public access and improved scalability.


---

### Collaboration

This project was developed collaboratively as part of the AAASE Capstone Project. Team members worked together on the system design, implementation, testing, debugging, and integration to deliver a complete AI-powered study assistant.



## Acknowledgements

This project was developed as part of the **AAASE Capstone Program** delivered by **SDAIA Academy**.

Special thanks to **Eng. Ibrahim Alshehri** for his guidance and mentorship throughout the program.

- **SDAIA Academy:** https://github.com/SDAIAAcademy
