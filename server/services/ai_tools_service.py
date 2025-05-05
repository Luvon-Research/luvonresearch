from services.supabase_service import SupabaseService
from config import settings
from pydantic_ai import Agent
from config import settings
from models.ai import AIResponse, MainAgentResponse, GraphAgentResponse

class AIService:
    def __init__(self, db: SupabaseService):
        self.db = db
        self.sys_prompt = '''
        You are a AI research assistant chatbot and you have three main tasks: 
        1. Making graphs (answer_path = graph)
        2. Predicting data (answer_path = predict)
        3. Making analysis (analysis)
        
        Your main job is to return the relevant answer_path based on the prompt 
        You cannot answer personal questions.
        If you cannot do any of the tasks, return a relevant message saying you can't,
        and tell the user what tasks you can do.
        '''
        self.main_agent = Agent(model=settings.AI_MODEL, output_type=MainAgentResponse, system_prompt=self.sys_prompt)

        self.graph_sys_prompt = '''
        You are a AI graph agent and your task is to create graphs based on a user prompt,
        the graph should be in a JSON output format, and return code written in R
        to generate this graph as well in the output filed r_code.
        
        You cannot answer personal questions.
        If you cannot do any of the tasks, return a relevant message saying you can't,
        and tell the user what tasks you can do.
        '''
        self.graph_agent = Agent(model=settings.AI_MODEL, output_type=GraphAgentResponse, system_prompt=self.graph_sys_prompt)
    async def call_main_agent(self, prompt):
        res = await self.main_agent.run(prompt)
        output = res.output
        
        if(output.answer_path == 'graph'):
            graph_res = await self.call_graph_agent(prompt)
            return graph_res
    
    async def call_graph_agent(self, prompt):
        res = await self.graph_agent.run(prompt)
        output = res.output
        
        return output
        