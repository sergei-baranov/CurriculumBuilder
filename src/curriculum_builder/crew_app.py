"""Сборка Crew: исследование → траектория → Markdown с чекбоксами."""

from __future__ import annotations

import os

from crewai import Agent, Crew, Process, Task
from crewai_tools import SerperDevTool

from curriculum_builder import prompts
from curriculum_builder.settings import get_crew_memory, get_crew_verbose, get_serper_n_results
from curriculum_builder.tools import study_assistant


def _search_tools() -> list:
    if os.environ.get("SERPER_API_KEY"):
        return [SerperDevTool(n_results=get_serper_n_results())]
    return []


def build_crew(topic: str, audience: str, region: str) -> Crew:
    safety = prompts.safety_policy_snippet(region)
    search_tools = _search_tools()

    researcher = Agent(
        role=prompts.researcher_role(),
        goal=prompts.researcher_goal(topic, audience, region),
        backstory=prompts.researcher_backstory(safety),
        tools=search_tools,
        verbose=get_crew_verbose(),
        allow_delegation=False,
    )

    architect = Agent(
        role=prompts.architect_role(),
        goal=prompts.architect_goal(),
        backstory=prompts.architect_backstory(topic, audience, region, safety),
        tools=search_tools + [study_assistant],
        verbose=get_crew_verbose(),
        allow_delegation=False,
    )

    editor = Agent(
        role=prompts.editor_role(),
        goal=prompts.editor_goal(),
        backstory=prompts.editor_backstory(safety),
        tools=[study_assistant],
        verbose=get_crew_verbose(),
        allow_delegation=False,
    )

    t_research = Task(
        description=prompts.task_research_description(topic, audience, region),
        expected_output=prompts.task_research_expected_output(),
        agent=researcher,
    )

    t_trajectory = Task(
        description=prompts.task_trajectory_description(topic, audience, region),
        expected_output=prompts.task_trajectory_expected_output(),
        agent=architect,
        context=[t_research],
    )

    t_markdown = Task(
        description=prompts.task_markdown_description(topic, audience, region),
        expected_output=prompts.task_markdown_expected_output(),
        agent=editor,
        context=[t_trajectory],
    )

    return Crew(
        agents=[researcher, architect, editor],
        tasks=[t_research, t_trajectory, t_markdown],
        process=Process.sequential,
        verbose=get_crew_verbose(),
        memory=get_crew_memory(),
    )
