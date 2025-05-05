from services.supabase_service import SupabaseService
from config import settings
from pydantic_ai import Agent, Tool
from models.ai import AIResponse, MainAgentResponse, GraphAgentResponse

class AIService:
    def __init__(self, db: SupabaseService):
        self.db = db

        # Unified system prompt describing available tools
        system_prompt = '''
You are an AI research assistant chatbot. You have three tools at your disposal:

1. graph    - Create graphs based on the user prompt (returns JSON + R code).
2. predict  - Predict data based on the user prompt (returns prediction results).
3. analysis - Perform data analysis based on the user prompt (returns analysis text).

You cannot answer personal questions. If a request falls outside these tasks, respond with a message stating you can't handle it and list the available tools.
'''

        # Define the three tools bound to internal methods
        tools = [
            Tool(name="graph", description="Generate a graph R code format.", function=self._tool_graph),
            Tool(name="predict", description="Make data predictions based on the prompt.", function=self._tool_predict),
            Tool(name="analysis", description="Perform data analysis based on the prompt.", function=self._tool_analysis),
        ]

        # Single unified agent with tools
        self.agent = Agent(
            model=settings.AI_MODEL,
            tools=tools,
            system_prompt=system_prompt,
            output_type=AIResponse
        )

    async def _tool_graph(self, prompt: str) -> GraphAgentResponse:
        # Local graph-only agent
        graph_agent = Agent(
            model=settings.AI_MODEL,
            system_prompt='''
You are the graph tool. Generate R code under `r_code`.
If you cannot graph, apologize and list available tools.
''',
            output_type=GraphAgentResponse
        )
        res = await graph_agent.run(prompt)
        return res.output

    async def _tool_predict(self, prompt: str) -> AIResponse:
        # Local prediction-only agent
        predict_agent = Agent(
            model=settings.AI_MODEL,
            system_prompt='''
You are the prediction tool. Return predicted values in AIResponse format.
''',
            output_type=AIResponse
        )
        res = await predict_agent.run(prompt)
        return res.output

    async def _tool_analysis(self, prompt: str) -> AIResponse:
        # Local analysis-only agent
        analysis_agent = Agent(
            model=settings.AI_MODEL,
            system_prompt='''
You are the analysis tool. Provide detailed analysis in AIResponse format.
''',
            output_type=AIResponse
        )
        res = await analysis_agent.run(prompt)
        return res.output

    async def call(self, prompt: str) -> MainAgentResponse:
        """
        Dispatch the prompt to the appropriate tool via the unified agent.
        Returns a MainAgentResponse with `answer_path` and tool output attached.
        """
        result = await self.agent.run(prompt)
        return result.output
