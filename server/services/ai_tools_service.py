from services.supabase_service import SupabaseService
from config import settings
from pydantic_ai import Agent, Tool, RunContext
from models.ai import AIResponse, GraphAgentResponse, AIInput, GraphAgentFinalResponse, CodeFixAgent
from fastapi import HTTPException, status
from util.utils import generate_uuid, ensure_dir, run_r_script, fetch_sample_lines, strip_code_block
from services.sheet_service import SheetService
import os
from services.files_service import FilesService
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.azure import AzureProvider
from dataclasses import dataclass
from services.pinecone_service import PineconeService
from dotenv import load_dotenv
from e2b_code_interpreter import Sandbox

@dataclass
class SupportDependencies:  
    user_id: str
    org_id: str
    context_source: str 
    
class AIService:
    def __init__(self, db: SupabaseService, pinecone: PineconeService):
        self.db = db
        self.sheet_service = SheetService(self.db)
        self.files_service = FilesService(db, pinecone)
        self.retries = 3
        load_dotenv()

        # Unified system prompt describing available tools
        system_prompt = """
        You are Luvon, an AI research assistant. Always respond in English. You have three tools:

        1. graph (chart) (you can make any type of chart that exists)
        - Call `_tool_graph` tool and obtain `r_code` and `img_url`
            • Generates raw ggplot2 R code for charts.  
        • First Include a small message on the output
        • Second Include the image url `img_url` in your response in `answer`.
        • Third Return the R code only (no comments or preamble) in `answer`. (You must give me r code as part of response)  


        2. predict  
        • Produce data predictions.

        3. analysis  
        • Provide data analysis text.

        Your `answer` must be a VALID JSON array of objects, each with:
        {
            "type": "message" | "image" | "code",
            "value": "<text or URL or code>"
        }

        - For plain text answers use type "message".  
        - For charts use type "image" with the URL.  
        - For R code use type "code" with the raw ggplot2 script.

        If the user asks for anything outside these tools, you MUST return this:
        [
        {
            "type": "message",
            "value": "Sorry, I can only handle graph, predict, or analysis requests."
        }
        ]
        """


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
            deps_type=SupportDependencies,
            system_prompt=system_prompt,
            output_type=AIResponse,
            input_type=AIInput
        )
        
        self._sandboxes_file = "sandboxes.txt"
        self.sbx_template_id = "potaq3k9ta9l28671h7j"

        # 1) Load any previously‐used sandbox IDs
        if os.path.exists(self._sandboxes_file):
            with open(self._sandboxes_file, "r") as f:
                sandbox_ids = [line.strip() for line in f if line.strip()]
        else:
            sandbox_ids = []

        active_sbx = None
        updated_ids = []

        # 2) Try each ID in turn
        for sbx_id in sandbox_ids:
            try:
                sbx = Sandbox(sbx_id)      # attach to existing
                if sbx.is_running():       # check health
                    active_sbx = sbx
                    updated_ids.append(sbx_id)
                    break
            except Exception:
                # Either invalid ID or not accessible → skip
                pass

        # 3) If none was active, spin up a new one
        if active_sbx is None:
            # create from template
            active_sbx = Sandbox(self.sbx_template_id)
            # It will have a new .id property
            updated_ids = sandbox_ids + [active_sbx.sandbox_id]

        # 4) Persist the cleaned+updated list
        with open(self._sandboxes_file, "w") as f:
            f.write("\n".join(updated_ids))

        # 5) Store the sandbox for your later use
        self.sbx = active_sbx

    async def _tool_graph(self, ctx: RunContext[str], prompt: str) -> GraphAgentFinalResponse:
        print("SHEET ID", ctx.deps.context_source)
        # Loads the CSV data
        ensure_dir('temp_files')
        uuid = generate_uuid()
        csv_file_name = f"temp_files/{uuid}.csv"
        csv_file_only_name = f'/home/user/{uuid}.csv'
        run_script_name = f"temp_files/{uuid}.r"
        csv_absolute = os.path.abspath(csv_file_name)
        script_absolute = os.path.abspath(run_script_name)
        csv_escaped  = csv_absolute.replace('\\', '\\\\')
        output_png = f"temp_files/{uuid}.png"
        output_png_only = f"/home/user/{uuid}.png"
        output_png_absolute = os.path.abspath(output_png).replace('\\', '\\\\')
        img_url = None
        script_file_only = f'/home/user/{uuid}.r'
        
        code_gen_error = ''

        try:
            print("Pulling CSV data")
            csv_data = await self.sheet_service.get_sheet_data_csv_by_id(ctx.deps.context_source, False)
            
            print("Wrote CSV data")
            with open(csv_file_name, 'w', newline="") as fp:
                fp.write(csv_data.getvalue())
                fp.close()
            
            sample_data = fetch_sample_lines(csv_file_name, lines=3)
            print(f"Got sample data {sample_data}")

            # Local graph-only agent
            model = OpenAIModel(
                'o3-mini',
                provider=AzureProvider(
                    azure_endpoint='https://admin-magg5801-eastus2.openai.azure.com/',
                    api_version='2024-12-01-preview',
                    api_key='EVK8DO7H0s7dRsQdTQzbAnDopoCUIDLQukfui89GSkIvlFHbPgbsJQQJ99BEACHYHv6XJ3w3AAAAACOGLFmQ',
                ),
            )
            
            graph_agent = Agent(
                model=settings.AI_MODEL,
                system_prompt=f'''
                    You are the graph/chart tool which writes R code for making graphs/charts. 
                    You can make any type of chart that exists
                    Only use ggplot2 to make these graphs.
                    Your sole task is to produce professional, aesthetically pleasing ggplot2 
                    R code under `r_code` that:
                      • Reads the CSV at "{csv_file_only_name}" (Windows path must be escaped).  
                      • Uses R-safe variable names (handling spaces, parentheses, and other non-alphanumeric characters), use bugticks.  
                      • Saves the plot to "{output_png_only}".  
                      • Contains only the R code—no comments or extra text.
                    
                    The sample schema for this dataset is: {sample_data}
                    If you cannot generate this chart, apologize and list the available tools.
                ''',
                output_type=GraphAgentResponse,
            )
            res = await graph_agent.run(prompt)
            res = res.output
            print(res)
            
            if(res.status == 'success'):
                print("code generation success")
                r_code = strip_code_block(res.r_code)
                tries = 0
                success = False
                
                # Creates sandbox if not active
                if(not self.sbx.is_running()):
                    self.sbx = Sandbox(self.sbx_template_id)
                
                # Adds csv file to sandbox
                self.sbx.files.write(csv_file_only_name, csv_data.getvalue())
                
                while tries <= self.retries:
                    print(f"###### Retry: {tries}/{self.retries}")
                    try:
                        # with open(run_script_name, 'w', newline="") as fp:
                        #     fp.write(r_code)
                        #     fp.close()
                        
                        print("Wrote the code to R file, running...")
                        
                        self.sbx.files.write(script_file_only, r_code)
                        
                        output = self.sbx.commands.run(f"Rscript {script_file_only}")
                        #print(output)
                        code_gen_error = output
                        
                        #execution = sbx.run_code(code=r_code, language='r') # Execute Python inside the sandbox
                        #print(execution.logs)
                        #print(execution.results)
                        #print(execution)
                        #print(result)
                        
                        #print(f"Running {script_absolute}")
                        #output = run_r_script(script_absolute)
                        #print(output)
                        
                        img_url = None
                        img_filename = f'{uuid}.png'
                        
                        file_content = bytes(self.sbx.files.read(output_png_only, format="bytes"))
                        print("Got file content")
                
                        out = await self.files_service.upload_file(ctx.deps.org_id, ctx.deps.user_id, file_content, img_filename, is_chart=True, r_code=r_code)
                        img_url = out['file_url']
                        
                        self.sbx.files.remove(script_file_only)
                        self.sbx.files.remove(output_png_only)

                        # Uploads the file
                        # TODO fill in the org id and everything
                        # with open(output_png_absolute, 'rb') as fp:
                        #     data = fp.read()
                        #     out = await self.files_service.upload_file(ctx.deps.org_id, ctx.deps.user_id, data, img_filename, is_chart=True, r_code=r_code)
                        #     img_url = out['file_url']
                        
                        success = True
                        break
                    except Exception as e:
                        print(e)
                        tries += 1
                        print("Code failed, retrying with new code")
                    
                        code_fix_agent = Agent(
                            model=settings.AI_MODEL,
                            system_prompt = f"""
                                You are an R code fixer. Given the original R script and its prompt,
                                correct it to produce the intended ggplot2 chart.

                                Original R code:
                                {r_code}
                                
                                Error with R code:
                                {code_gen_error}

                                Original prompt:
                                {prompt}

                                Sample data schema:
                                {sample_data}

                                Return only the fixed R code—no explanations.
                                """,
                            output_type=CodeFixAgent
                        )
                        res = await code_fix_agent.run(prompt)
                        res = res.output
                        r_code = strip_code_block(res.r_code)
                        print(f"RETRY CODE: {res}")
                
                if(not success):
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"Failed to generate chart"
                    )

                if os.path.exists(csv_absolute):
                    os.remove(csv_absolute)
                    
                if os.path.exists(script_absolute):
                    os.remove(script_absolute)
                    
                if os.path.exists(output_png_absolute):
                    os.remove(output_png_absolute)     
                return GraphAgentFinalResponse(r_code=r_code, status='success', img_url=img_url)
            else:
                if os.path.exists(csv_absolute):
                    os.remove(csv_absolute)
                    
                if os.path.exists(script_absolute):
                    os.remove(script_absolute)
                    
                if os.path.exists(output_png_absolute):
                    os.remove(output_png_absolute)      

                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to generate chart: {res.r_code}"
                )
        except Exception as e:
            print(e)
            if os.path.exists(csv_absolute):
                os.remove(csv_absolute)
                
            if os.path.exists(script_absolute):
                os.remove(script_absolute)
                
            if os.path.exists(output_png_absolute):
                os.remove(output_png_absolute)    
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
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

    async def call(self, input: AIInput, user_id:str, org_id:str):
        """
        Dispatch the prompt to the appropriate tool via the unified agent.
        Returns a MainAgentResponse with `answer_path` and tool output attached.
        """
        
        ctx = SupportDependencies(
                user_id= user_id,
                org_id=org_id,
                context_source=input.context_source,
        )
        
        result = await self.agent.run(input.prompt, deps=ctx)
        return result.output
