"""
backend/core/workflow.py

This file defines the LangGraph workflow that connects all AI agents.

Workflow order:


Summarization Agent
        │
   ┌────┴────┐
   ▼         ▼
Quiz      Planner
   └────┬────┘
        ▼
Final State

"""

from langgraph.graph import END, START, StateGraph

from backend.agents.quiz_generator import generate_quiz
from backend.agents.study_planner import study_planner_agent
from backend.agents.summarizer import summarization_agent
from backend.core.state import StudyState


def quiz_agent_node(state: StudyState) -> dict:
    result = generate_quiz(
        summary=state["summary"],
        key_topics=state["key_topics"],
        difficulty=state["difficulty"],
    )

    return {
        "quiz": result["quiz"],
    }


def study_planner_node(state: StudyState) -> dict:
    result = study_planner_agent(state)

    return {
        "study_plan": result["study_plan"],
    }


def build_workflow():
    workflow = StateGraph(StudyState)

    workflow.add_node(
        "summarization_agent",
        summarization_agent,
    )

    workflow.add_node(
        "quiz_generator_agent",
        quiz_agent_node,
    )

    workflow.add_node(
        "study_planner_agent",
        study_planner_node,
    )

    workflow.add_edge(
        START,
        "summarization_agent",
    )

    # Both agents run after summarization.
    workflow.add_edge(
        "summarization_agent",
        "quiz_generator_agent",
    )

    workflow.add_edge(
        "summarization_agent",
        "study_planner_agent",
    )

    workflow.add_edge(
        "quiz_generator_agent",
        END,
    )

    workflow.add_edge(
        "study_planner_agent",
        END,
    )

    return workflow.compile()


# Compiled graph used by the backend API.
graph = build_workflow()