from crewai import Agent, Task, Crew, LLM, Process
from crewai.project import CrewBase, agent, task, crew, before_kickoff
from src.tools.SQLExecutorTool import SQLExecutorTool 
from os import getenv
from dotenv import load_dotenv

load_dotenv()

@CrewBase
class SolveUserQueryCrew:
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"
    """nvidia_deepseek_llm = LLM(model='nvidia_nim/'+getenv('NVIDIA_MODEL'),
            temperature=0.2,
            api_key=getenv('NVIDIA_API_KEY'),
            max_tokens=8192)"""
    google_llm = LLM(model='gemini/'+getenv('GEMINI_MODEL'),
              temperature=0.2,
              api_key=getenv('GEMINI_API_KEY'),
              max_tokens=8192)
    reasoning_llm = LLM(model='gemini/'+getenv('GEMINI_MODEL_REASONING'),
                     temperature=0.2,api_key=getenv('GEMINI_API_KEY'))

    @before_kickoff
    def connect_database(self, inputs):
        db_uri = inputs['db_uri']
        try:
            self.execute_sql_query = SQLExecutorTool(db_uri=db_uri)
            self.schema_analyst_agent().tools=[self.execute_sql_query]
            self.database_manager().tools=[self.execute_sql_query]
            self.data_analyst().tools=[self.execute_sql_query]
        except Exception as err:
            raise err
        return inputs

    @agent
    def schema_analyst_agent(self) -> Agent:
        return Agent(config=self.agents_config['schema_analyst_agent'],
                    allow_delegation=False,
                    max_iter=10,
                    execution_timeout=120,
                    memory=True,
                    cache=True,
                    respect_context_window=True,
                    llm=self.google_llm)
    
    @agent
    def database_manager(self) -> Agent:
        return Agent(config=self.agents_config['database_manager'],
                    allow_delegation=False,
                    memory=True,
                    cache=True,
                    max_iter=30,
                    llm=self.google_llm)

    @agent
    def data_analyst(self) -> Agent:
        return Agent(config=self.agents_config['data_analyst'],
                    allow_delegation=False,
                    memory=True,
                    cache=True,
                    execution_timeout=120,
                    max_iter=50,
                    max_rpm=10,
                    llm=self.reasoning_llm)

    @agent
    def erd_diagram_specialist(self) -> Agent:
        return Agent(config=self.agents_config['erd_diagram_specialist'],
                    allow_delegation=False,
                    llm=self.google_llm,
                    memory=True,
                    cache=True,
                    execution_timeout=120)

    @agent
    def orchestrator_agent(self) -> Agent:
        return Agent(config=self.agents_config['orchestrator_agent'],
                    dependencies=[
                        self.schema_analyst_agent,
                        self.database_manager,
                        self.data_analyst,
                        self.erd_diagram_specialist
                    ],
                    allow_delegation=True,
                    delegation_mode="hybrid",
                    memory=True,
                    max_iter=30,
                    cache=True,
                    respect_context_window=True,
                    llm=self.google_llm)
    @agent
    def format_user_response_agent(self) -> Agent:
        return Agent(config=self.agents_config['format_user_response_agent'],
                    allow_delegation=False,
                    max_iter=2,
                    cache=True,
                    respect_context_window=True,
                    llm=self.google_llm)

    @task
    def user_task(self) -> Task:
        return Task(
            config=self.tasks_config['solve_user_query'],
            output_format="plain"
        )

    @task
    def format_response(self) -> Task:
        return Task(config=self.tasks_config['format_response'],
                    context=[self.user_task()],
                    agent=self.format_user_response_agent())

    @crew
    def solve_query_crew(self) -> Crew:
        return Crew(
            tasks=[self.user_task(),self.format_response()],
            agents=[
                self.schema_analyst_agent(),
                self.database_manager(),
                self.data_analyst(),
                self.erd_diagram_specialist(),
                self.format_user_response_agent()
            ],
            process=Process.hierarchical,
            verbose=True,
            max_rpm=15,
            manager_agent=self.orchestrator_agent(),
            output_log_file="log.txt"
        )
        
        