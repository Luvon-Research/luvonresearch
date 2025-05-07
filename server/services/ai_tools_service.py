from services.supabase_service import SupabaseService
from config import settings
from pydantic_ai import Agent, Tool
from models.ai import AIResponse, MainAgentResponse, GraphAgentResponse, AIInput
from fastapi import HTTPException, status
from util.utils import generate_uuid, ensure_dir, run_r_script, fetch_sample_lines, strip_code_block
from services.sheet_service import SheetService
import os
from fastapi.responses import FileResponse
from services.files_service import FilesService

class AIService:
    def __init__(self, db: SupabaseService):
        self.db = db
        self.sheet_service = SheetService(self.db)
        self.files_service = FilesService(db)
        self.context_source = None

        # Unified system prompt describing available tools
        system_prompt = '''
You are an AI research assistant chatbot called Luvon. You have three tools at your disposal:

1. graph    - Create graphs based on the user prompt (returns JSON + R code). Set `img_path` to the fileanme. Set `extra_metadata` to include the `r_code` that you get from `_tool_graph`.
2. predict  - Predict data based on the user prompt (returns prediction results).
3. analysis - Perform data analysis based on the user prompt (returns analysis text).

You cannot answer personal questions. If a request falls outside these tasks, respond with a message stating you can't handle it and list the available tools.
'''

        # Define the three tools bound to internal methods
        tools = [
            Tool(name="graph", description="Generate a graph based on the prompt and context_source", function=self._tool_graph),
            Tool(name="predict", description="Make data predictions based on the prompt.", function=self._tool_predict),
            Tool(name="analysis", description="Perform data analysis based on the prompt.", function=self._tool_analysis),
        ]

        # Single unified agent with tools
        self.agent = Agent(
            model=settings.AI_MODEL,
            tools=tools,
            system_prompt=system_prompt,
            output_type=AIResponse,
            input_type=AIInput
        )

    async def _tool_graph(self, prompt: str):
        print("SHEET ID", self.context_source)
        # Loads the CSV data
        ensure_dir('temp_files')
        uuid = generate_uuid()
        csv_file_name = f"temp_files/{uuid}.csv"
        run_script_name = f"temp_files/{uuid}.r"
        csv_absolute = os.path.abspath(csv_file_name)
        script_absolute = os.path.abspath(run_script_name)
        csv_escaped  = csv_absolute.replace('\\', '\\\\')
        output_png = f"temp_files/{uuid}.png"
        output_png_absolute = os.path.abspath(output_png).replace('\\', '\\\\')

        try:
            print("Pulling CSV data")
            csv_data = await self.sheet_service.get_sheet_data_csv_by_id(self.context_source, False)
            
            print("Wrote CSV data")
            with open(csv_file_name, 'w', newline="") as fp:
                fp.write(csv_data.getvalue())
                fp.close()
            
            sample_data = fetch_sample_lines(csv_file_name, lines=3)
            print(f"Got sample data {sample_data}")

            # Local graph-only agent
            graph_agent = Agent(
                model=settings.AI_MODEL,
                system_prompt=f'''
                    You are the graph tool you can create R code for any type of chart that is supported by R. 
                    Generate R code under `r_code` to make this chart. 
                    Your only job is to just create R code for this prompt (USE ggplot2 package), the actually running of this code
                    is done later on. The charts should be visually professional and asthethically pleasing.
                    The R code that you generate has to read read a input file called: {csv_escaped},
                    make sure you correctly format the file path for windows
                    to make this chart. Also for x and y variable names, make sure you format the names correctly to work with R.
                    
                    Then once the chart is created, you have to save the chart as an image
                    to this file name: {output_png_absolute}. DO NOT INCLUDE ANY COMMENTS IN THIS CODE (IMPORTANT)
                    
                    The sample schema for this document is: {sample_data}
                    If you cannot create this type of graph, apologize and list available tools.
                ''',
                output_type=GraphAgentResponse
            )
            res = await graph_agent.run(prompt)
            res = res.output
            print(res)
            
            if(res.status == 'success'):
                print("code generation success")
                r_code = strip_code_block(res.r_code)
                
                with open(run_script_name, 'w', newline="") as fp:
                    fp.write(r_code)
                    fp.close()
                
                print("Wrote the code to R file, running...")
                print(f"Running {script_absolute}")
                output = run_r_script(script_absolute)
                print(output)
                
                # Uploads the file
                # TODO fill in the org id and everything
                with open(output_png_absolute, 'rb') as fp:
                    data = fp.read()
                    out = await self.files_service.upload_file('test_org', 'test', data, f'{uuid}.png', 'image/png')
                
                # if os.path.exists(csv_absolute):
                #     os.remove(csv_absolute)
                    
                # if os.path.exists(script_absolute):
                #     os.remove(script_absolute)
                    
                # if os.path.exists(output_png_absolute):
                #     os.remove(output_png_absolute)     
                return GraphAgentResponse(r_code=r_code, status='success', filename=f'{uuid}.png').model_dump()
            else:
                # if os.path.exists(csv_absolute):
                #     os.remove(csv_absolute)
                    
                # if os.path.exists(script_absolute):
                #     os.remove(script_absolute)
                    
                # if os.path.exists(output_png_absolute):
                #     os.remove(output_png_absolute)      

                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to generate chart"
                )
        except Exception as e:
            print(e)
            # if os.path.exists(csv_absolute):
            #     os.remove(csv_absolute)
                
            # if os.path.exists(script_absolute):
            #     os.remove(script_absolute)
                
            # if os.path.exists(output_png_absolute):
            #     os.remove(output_png_absolute)    
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate chart: " + str(e)
            )

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

    async def call(self, input: AIInput) -> MainAgentResponse:
        """
        Dispatch the prompt to the appropriate tool via the unified agent.
        Returns a MainAgentResponse with `answer_path` and tool output attached.
        """
        self.context_source = input.context_source
        result = await self.agent.run(input.prompt)
        return result.output
