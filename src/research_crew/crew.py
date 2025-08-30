# src/research_crew/crew.py
from typing import List
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai_tools import SerperDevTool  # search tool
from research_crew.tools.technical_analysis_tool import technical_analysis   



@CrewBase
class ResearchCrew():
    """Research crew adapted for Ticker Collector - Data Collector → Trend Analyzer → Report Generator → Insight Synthesizer"""

    agents: List[BaseAgent]
    tasks: List[Task]


    # === Agents ===
    @agent
    def ticker_collector(self) -> Agent:
        return Agent(
            config=self.agents_config['ticker_collector'],  # type: ignore[index]
            verbose=True
        )
    
    @agent
    def data_collector(self) -> Agent:
        return Agent(
            config=self.agents_config['data_collector'],  # type: ignore[index]
            verbose=True,
            tools=[SerperDevTool()]  # web search for recency/citations
        )

    @agent
    def trend_analyzer(self) -> Agent:
        return Agent(
            config=self.agents_config['trend_analyzer'],  # type: ignore[index]
            verbose=True,
            tools = [technical_analysis]
        )

    @agent
    def report_generator(self) -> Agent:
        return Agent(
            config=self.agents_config['report_generator'],  # type: ignore[index]
            verbose=True
        )

    @agent
    def insight_synthesizer(self) -> Agent:
        return Agent(
            config=self.agents_config['insight_synthesizer'],  # type: ignore[index]
            verbose=True
        )

    # === Tasks ===
    @task
    def infer_ticker(self) -> Task:
        return Task(
            config=self.tasks_config['infer_ticker']  # type: ignore[index]
        )
    
    @task
    def collect_data(self) -> Task:
        return Task(
            config=self.tasks_config['collect_data']  # type: ignore[index]
        )

    @task
    def analyze_trends(self) -> Task:
        return Task(
            config=self.tasks_config['analyze_trends']  # type: ignore[index]
        )

    @task
    def draft_report(self) -> Task:
        return Task(
            config=self.tasks_config['draft_report']  # type: ignore[index]
        )

    @task
    def synthesize_insights(self) -> Task:
        return Task(
            config=self.tasks_config['synthesize_insights']  # type: ignore[index]
        )

    # === Crew ===
    @crew
    def crew(self) -> Crew:
        """Creates the research crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,  # linear handoff DC → TA → RG → IS
            verbose=True,
        )
