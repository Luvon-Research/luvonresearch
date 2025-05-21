from services.supabase_service import SupabaseService
from config import settings
from pydantic_ai import Agent, Tool, RunContext
from models.ai import AIResponse, GraphAgentResponse, AIInput, GraphAgentFinalResponse, CodeFixAgent
from fastapi import HTTPException, status
from util.utils import generate_uuid, ensure_dir, run_r_script, fetch_sample_lines, strip_code_block, parse_table_json
from services.sheet_service import SheetService
import os
from services.files_service import FilesService
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.azure import AzureProvider
from dataclasses import dataclass, field
from services.pinecone_service import PineconeService
from services.e2b_service import E2BService
import json
from json_repair import repair_json
from typing import Optional, Dict

@dataclass
class SupportDependencies:  
    user_id: str
    org_id: str
    context_source: str 
    sandbox: E2BService
    selectedCells: Optional[dict] = field(default_factory=dict)
    
class AIService:
    def __init__(self, db: SupabaseService, pinecone: PineconeService):
        self.db = db
        self.sheet_service = SheetService(self.db)
        self.files_service = FilesService(db, pinecone)
        self.MAX_RETRIES = 3
        # self.sbx = sbx

        # Unified system prompt describing available tools
        system_prompt = """
        You are Luvon, an AI research assistant. Always respond in English. You have three tools (call only one tool):

        1. graph (chart) (you can make any type of chart that exists)
        - Call `_tool_graph` tool and obtain `r_code` and `img_url`
            • Generates raw ggplot2 R code for charts.  
        • First Include a small message on the output
        • Second Include the image url `img_url` in your response in `answer`.
        • Third Return the R code only (no comments or preamble) in `answer`. (You must give me r code as part of response)  
        • Terminate and return output


        2. predict  
        • If selectedCells are not included, give error message that cells must be highlighted and terminate here, do not call tool (important)
        • Produce data predictions. And also run code to find details about the data
        • Call `_tool_predict` once and do the following steps
        • First Include a small message on the output
        • Second include a data table with the values of the output (always have this in data table format)
        • Third, create a action, where it takes the predictions and the original cells to predict
            and maps it to replace those cells in the action format below. Target is "sheet" and action_type is "update"
        • Action description should be "Apply to cells"
        • If predict tool returns error, give user error message
        • Terminate and return output
        

        3. analysis  
        • Provide data analysis text.

        Your `answer` must be a VALID JSON array of objects, each with:
        {
            "type": "message" | "image" | "code" | "data_table | action",
            "value": "<text or URL or code or data_table (format should be {headers: <list>, data: <data>}) or action (format should be {description: <description text of this action>, target: <target to apply to>, action_type: <type of action> data: [{x: <x>, y: <y>, val:<value>}]})>"
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
                'gpt-4.1-nano',
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
                
                tool_sandbox = E2BService(id=uuid)
                
                # Adds csv file to sandbox
                await tool_sandbox.add_file(csv_file_only_name, csv_data.getvalue())
                
                while tries <= self.MAX_RETRIES:
                    print(f"###### Retry: {tries}/{self.MAX_RETRIES}")
                    try:
                        # with open(run_script_name, 'w', newline="") as fp:
                        #     fp.write(r_code)
                        #     fp.close()
                        
                        print("Wrote the code to R file, running...")
                        
                        await tool_sandbox.add_file(script_file_only, r_code)
                        
                        output = await tool_sandbox.run_command(f"Rscript {script_file_only}")
                        print(output)
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
                        
                        file_content = await tool_sandbox.get_file(output_png_only, format="bytes")
                        print("Got file content")
                
                        out = await self.files_service.upload_file(ctx.deps.org_id, ctx.deps.user_id, file_content, img_filename, is_chart=True, r_code=r_code)
                        img_url = out['file_url']
                        
                        await tool_sandbox.remove_files([script_file_only, output_png_only])

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

    async def _tool_code_execution(self, ctx: RunContext[str], code: str):
        code_agent = Agent(
            model=settings.AI_MODEL,
            system_prompt=f'''
            You are an expert Python code fixer.
            Given the original code and the runtime error message, 
            fix the code, and return only the corrected Python script.
            Do not include any explanation, comments, 
            or extra output—just return the corrected code block.
            ''',
            output_type=AIResponse
        )
                    
        for i in range(self.MAX_RETRIES):
            print(f"RUNNING CODE------ Retry: {i}: \n {code}")
            output = await ctx.deps.sandbox.run_code(code, language="python")
            print(output)
            #print(output.logs)
            #print(output.logs.stderr)
            #print(output.logs.stdout)
            output_error = output.logs.stderr
            output_logs = output.logs.stdout
            
            if(len(output_logs) != 0):
                print("Run is successful!")
                return output_logs
            
            res = await code_agent.run(f"Code:\n{code}\nOutput Error: {output_error}")
            print("CODE AGENT OUTPUT", res.output)
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate the code for this prompt..."
        )
        
    async def _tool_predict(self, ctx: RunContext[str], prompt: str) -> AIResponse:
        uuid = generate_uuid()
        csv_file_local = f"temp_files/{uuid}.csv"
        csv_file_sandbox = f'/home/user/{uuid}.csv'

        try:
            print("Pulling CSV data")
            csv_data = await self.sheet_service.get_sheet_data_csv_by_id(ctx.deps.context_source, False)
                
            print("Writing CSV data")
            if not os.path.exists("temp_files"):
                os.makedirs("temp_files")
                
            with open(csv_file_local, 'w', newline="") as fp:
                fp.write(csv_data.getvalue())
            
            print("Wrote csv data")
            
            print("temp files", os.listdir("temp_files"))
            
            sample_data = fetch_sample_lines(csv_file_local, lines=3)
            header_row = fetch_sample_lines(csv_file_local, lines=1)
            print(f"Got sample data {sample_data}")
            
            tools = [
                Tool(name="code_executor", description="This code is connected to a sandbox where you can run any code you want", function=self._tool_code_execution),
            ]
            
            model = OpenAIModel(
                'gpt-4.1-nano',
                provider=AzureProvider(
                    azure_endpoint='https://admin-magg5801-eastus2.openai.azure.com/',
                    api_version='2024-12-01-preview',
                    api_key='EVK8DO7H0s7dRsQdTQzbAnDopoCUIDLQukfui89GSkIvlFHbPgbsJQQJ99BEACHYHv6XJ3w3AAAAACOGLFmQ',
                ),
            )
            
            totalCells = ((ctx.deps.selectedCells['right'] - ctx.deps.selectedCells['left'])+1) * (ctx.deps.selectedCells['bottom'] - ctx.deps.selectedCells['top'])
            print("TOTAL CELLS", totalCells)
            
            # Local prediction-only agent
            predict_agent = Agent(
                model=settings.AI_MODEL,
                system_prompt = f"""
                If `{ctx.deps.selectedCells}` is empty, return an error message and terminate

                You are a prediction tool that generates Python code for ML tasks using 
                PyTorch, TensorFlow, scikit-learn, NumPy, and/or pandas.
                
                Prompt: {prompt}
                Data schema (sample): {sample_data}

                The CSV data is presented to the user as follows:
                - Index: 1. | LABEL, LABEL, ...    (header row)
                - Index: 2. | DATA, DATA, ...      (first data row; pandas DataFrame index 0 after dropping header)
                - Index: 3. | DATA, DATA, ...      (DataFrame index 1)
                - ...

                When mapping row indices from the user (in the prompt or in `selectedCells`):
                - User-provided indices are **1-based** and refer to the UI.
                - Always **subtract 2** from each user index (after dropping the header) to convert to 0-based DataFrame indices.
                - **Before using indices:**
                - Never select indices outside the available data range.
                - All index arithmetic and validation must be handled in the generated code before subsetting the DataFrame.

                Instructions:
                1. Load CSV from `{csv_file_sandbox}` into a pandas DataFrame.
                    - Always drop the first row (the header).
                2. Determine the train/test split:
                    - If the prompt specifies certain rows or indices, use those as the test set (with index conversion).
                    - Otherwise, use `{ctx.deps.selectedCells}` (a grid of user-selected cell ranges), applying the same index handling.
                    - All other rows become the training set.
                    
                3. Identify the target column(s):
                    - If specified in the prompt, predict only those.
                    - Otherwise, infer missing/empty column(s) and predict them.
                4. **Before training: Remove any rows from the training set where the target column(s) (e.g., Y) are NaN or missing.**
                5. Generate Python code that:
                    a. Safely converts, clamps, and validates user indices before splitting into train/test sets.
                    b. Drops any training rows with NaN in the target column(s) before fitting the model.
                    c. Trains an appropriate model on the cleaned training set.
                    d. Predicts on the test set.
                6. Execute the code via the provided tool. If execution fails, auto-fix and retry up to 3 times. On final failure, return an error message.
                7. Output results as:
                print({{ "headers" : [<col1>, <col2>, ...]
                   "data" : [ [row1_vals], [row2_vals], ... ]
                }})

                **Always prioritize safe, index error-free code that handles all possible user index mistakes and excludes rows with missing target values during training.**
                """,
                output_type=AIResponse,
                tools=tools,
                deps_type=SupportDependencies,
            )
            
            print("Init sandbox")
            
            tool_sandbox = E2BService(id=uuid)
            
            tool_ctx = SupportDependencies(
                user_id= '',
                org_id='',
                context_source='',
                sandbox=tool_sandbox
            )
            
            print("Adding file to sandbox")
            await tool_sandbox.add_file(csv_file_sandbox, csv_data)
            
            print("Added file to sandbox file")
            res = await predict_agent.run(prompt, deps=tool_ctx)
            
            # Checks if data_table is in data            
            print("ran agent")
            
            print(res)
            
            if os.path.exists(csv_file_local):
                os.remove(csv_file_local)

            return res.output

        except Exception as e:
            if os.path.exists(csv_file_local):
                os.remove(csv_file_local)
                
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

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
                sandbox=None,
                selectedCells=input.selectedCells
        )
        adjusted_input_cells = None
        
        if(input.selectedCells):
            adjusted_input_cells = {
                'left': input.selectedCells['left'],
                'right': input.selectedCells['right'],
                'top': input.selectedCells['top']-1,
                'bottom': input.selectedCells['bottom']-1,
            }
        
        result = await self.agent.run(input.prompt + f"Selected cells: {adjusted_input_cells}", deps=ctx)
        
        #print(result.output.answer)
        print("MODEL DUMP", result.output.model_dump())
        model_dumped = result.output.model_dump()
        answer_response = json.loads(repair_json(model_dumped['answer']))
        
        for msg in answer_response:
            print("MESSAGE", msg)
            if(msg['type'] == 'data_table'):
                table_data = json.loads(repair_json(str(msg['value'])))
                table_formatted = {
                    "headers": table_data["headers"],
                    "data": parse_table_json(table_data['headers'], table_data['data'])
                }
                msg['value'] = table_formatted
        print(answer_response)
        
        model_dumped['answer'] = answer_response
        return model_dumped
