from services.supabase_service import SupabaseService
from config import settings
from pydantic_ai import Agent, Tool, RunContext
from models.ai import AIResponse, GraphAgentResponse, AIInput, GraphAgentFinalResponse, CodeFixAgent, CodeFixAgentResponsePython
from fastapi import HTTPException, status, Request
from util.utils import generate_uuid, ensure_dir, run_r_script, fetch_sample_lines, strip_code_block, check_user_connected, parse_table_json
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
    request: Request
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
        You are Luvon, an AI research assistant. Always respond in English.
        You are interacting with a user who is looking at a data sheet.

        IMPORTANT: The user's prompt may be prefixed with a "System Note" and a "Sheet Data Sample". This sample is for YOUR USE ONLY to answer simple, direct questions about the sheet's content (like "What are the column headers?", "What's in row 2?", "How many rows in sample?").
        Use this provided sample data for these simple, direct lookups.
        DO NOT pass the "System Note" or "Sheet Data Sample" text itself to any of your tools (graph, predict, analysis). These tools have their own data access methods.

        General Instructions:
        When a user asks questions about the sheet's content, try to answer directly using the provided sample if the question is simple (e.g., "What are the column headers?", "How many rows are in this sheet based on sample?", "What is the value in cell A1 of the sample?", "What does row 2 of the sample say?").
        Be cautious: if asked to display a large amount of data (e.g., "show me all data"), politely decline or ask them to narrow their request, even if you have a sample. The sample is small.
        
        For summaries: If the user asks for a general summary of a column or the data without specifying 'full dataset' or 'entire sheet', first try to provide a brief summary based *only* on the 'Sheet Data Sample' you were given. Clearly state that your summary is based on this sample (e.g., "Based on the sample, column X contains..."). If the sample is insufficient for the summary requested, or if the user explicitly asks for a comprehensive analysis or summary of the 'entire sheet' or 'full dataset', then use the 'analysis' tool.
        You can also provide simple descriptive summaries based *only* on the provided sample, like "Describe the first few values in column X from the sample."

        If the user's request requires more complex data interpretation (beyond simple lookups or sample-based summaries), calculations, insights beyond what the provided sample can offer, or actions on the full dataset, you should use one of the specialized tools. For example: "What is the correlation between column A and column B over the whole dataset?" or "Find trends in the sales data for all entries" should use the 'analysis' tool.

        You have three tools available (call only one tool if a tool is needed):

        1. graph (chart)
        - Use for generating charts or graphs (e.g., "Make a bar chart of column X").
        - Call `_tool_graph` tool and obtain `r_code` and `img_url`.
        - Your response should first include a small introductory message.
        - Then, include the image URL `img_url` (type "image").
        - Finally, return the R code (type "code").
        - Terminate and return output.

        2. predict
        - Use for making data predictions or finding details about data that require computation.
        - If `selectedCells` are not mentioned or relevant to the prediction task, ask the user to highlight cells if necessary for the prediction. If they are clearly not needed for the type of prediction requested, proceed without error.
        - Call `_tool_predict` once.
        - Your response should first include a small introductory message.
        - Second, include a data table with the prediction output (type "data_table").
        - Third, create an action to apply predictions to the sheet (type "action", target "sheet", action_type "update"). Action description should be "Apply to cells".
        - If the predict tool returns an error, inform the user.
        - Terminate and return output.
        
        3. analysis
        - Use for in-depth data analysis, complex queries, summarizations that require computation, or open-ended questions about data insights (e.g., "Explain the distribution of values in column Y", "What are the key takeaways from this dataset?").
        - This tool can access and process the sheet data to answer such questions.
        - Provide data analysis text (type "message").

        Your `answer` must be a VALID JSON array of objects, each with:
        {
            "type": "message" | "image" | "code" | "data_table" | "action",
            "value": "<text or URL or code or data_table (format should be {headers: <list>, data: <data>}) or action (format should be {description: <description text of this action>, target: <target to apply to>, action_type: <type of action> data: [{x: <x>, y: <y>, val:<value>}]})>"
        }

        - For plain text answers (including direct answers to simple sheet questions), use type "message".  
        - For charts, use type "image" with the URL.  
        - For R code, use type "code" with the raw ggplot2 script.

        If the user asks for something completely unrelated to the sheet or these tools (e.g., general knowledge questions not about the data), you MUST return:
        [
        {
            "type": "message",
            "value": "Sorry, I can only assist with questions and tasks related to your sheet data and the available tools: graph, predict, and analysis."
        }
        ]
        
        Remember: If a question is a simple lookup of sheet content (headers, row count, specific cell/row data, simple summary of a few values) and you can confidently answer it, do so directly with a 'message' type. Otherwise, use the 'analysis' tool for more complex data questions or summarizations.
        """

        # Define the three tools bound to internal methods
        tools = [
            Tool(name="graph", 
                 description="Use when the user asks to create a chart or graph of the sheet data. Input should be the user's request for a graph (e.g., 'make a bar chart of sales').", 
                 function=self._tool_graph),
            Tool(name="predict", 
                 description="Use when the user asks for data predictions, forecasting, or to generate data based on existing patterns that requires computational modeling (e.g., 'predict next month's sales', 'what if analysis for Q4'). The user may need to specify or highlight relevant data if it's not obvious from the prompt.", 
                 function=self._tool_predict),
            Tool(name="analysis", 
                 description="Use for complex queries about the data that require computation, interpretation, or in-depth summarization beyond simple lookups (e.g., 'analyze trends in column X', 'what's the correlation between A and B?', 'summarize the key findings in this dataset'). Do not use for simple questions like 'what are the column headers?' or 'how many rows are there?' which you can answer directly.", 
                 function=self._tool_analysis),
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
        await check_user_connected(ctx.deps.request)
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
            
            await check_user_connected(ctx.deps.request)


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
            
            await check_user_connected(ctx.deps.request)
            
            if(res.status == 'success'):
                print("code generation success")
                r_code = strip_code_block(res.r_code)
                tries = 0
                success = False
                
                tool_sandbox = E2BService(id=uuid)
                
                # Adds csv file to sandbox
                await tool_sandbox.add_file(csv_file_only_name, csv_data.getvalue())
                
                while tries <= self.MAX_RETRIES:
                    await check_user_connected(ctx.deps.request)
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
            output_type=CodeFixAgentResponsePython
        )
                    
        for i in range(self.MAX_RETRIES):
            await check_user_connected(ctx.deps.request)
            print(f"RUNNING CODE------ Retry: {i}: \n {code}")
            output = await ctx.deps.sandbox.run_code(code, language="python")
            print(output)
            output_error = f"{output.logs.stderr} \n {output.error}"
            output_logs = output.logs.stdout
            print("----OUTPUT ERROR: ", output_error)
            
            if(len(output_logs) != 0):
                print("Run is successful!")
                return output_logs
            
            res = await code_agent.run(f"Code:\n{code}\nOutput Error: {output_error}")
            print("CODE AGENT OUTPUT", res.output)
            
            if(res.output):
                code = res.output.code
            else: break
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate the code for this prompt..."
        )
        
    async def _tool_predict(self, ctx: RunContext[str], prompt: str) -> AIResponse:
        uuid = generate_uuid()
        csv_file_local = f"temp_files/{uuid}.csv"
        csv_file_sandbox = f'/home/user/{uuid}.csv'
        
        await check_user_connected(ctx.deps.request)

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
                You are a prediction tool that generates Python code for ML tasks using 
                PyTorch, TensorFlow, scikit-learn, NumPy, and/or pandas.
                
                The user's request is: {prompt}
                The available data schema (sample) is: {sample_data}
                Selected cells by the user (if any, 1-based UI indexing): {ctx.deps.selectedCells}

                Your primary task is to generate robust Python code to perform the prediction.
                If specific cells (`selectedCells`) are provided and relevant, the generated code should use them.
                If `selectedCells` are not provided or not relevant for the type of prediction requested (e.g., time series forecast on a whole column), 
                the generated code should adapt, for example, by using relevant columns or the entire dataset as appropriate.
                The code must handle cases where `selectedCells` might be empty or not provided.
                It is crucial that the Python code itself includes logic for data loading, preprocessing (like dropping headers), 
                and ESPECIALLY SAFE INDEXING.
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

                **Always prioritize safe, index error-free code. The generated code must handle all possible user index mistakes (e.g. selected cells outside actual data range, off-by-one errors due to header row), and exclude rows with missing target values during training.**
                """,
                output_type=AIResponse, # Although this agent's direct output is Python code via a tool, its interaction with the main agent is through AIResponse structure
                tools=tools, # The code_executor tool
                deps_type=SupportDependencies,
            )
            
            print("Init sandbox")
                        
            tool_sandbox = E2BService(id=uuid)
            
            tool_ctx = SupportDependencies(
                user_id= '',
                org_id='',
                context_source='',
                request=ctx.deps.request,
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

    async def _tool_analysis(self, ctx: RunContext[str], prompt: str) -> AIResponse:
        await check_user_connected(ctx.deps.request)
        uuid = generate_uuid()
        csv_file_name = f"temp_files/{uuid}.csv"
        # csv_file_only_name = f'/home/user/{uuid}.csv' # Not needed if analysis agent doesn't run code in sandbox directly

        ensure_dir('temp_files')

        try:
            print(f"Analysis tool called for sheet: {ctx.deps.context_source}")
            csv_data_io = await self.sheet_service.get_sheet_data_csv_by_id(ctx.deps.context_source, False)
            csv_content_str = csv_data_io.getvalue()

            with open(csv_file_name, 'w', newline="") as fp:
                fp.write(csv_content_str)
            
            sample_data = fetch_sample_lines(csv_file_name, lines=5) # Provide more sample lines for analysis context
            print(f"Sample data for analysis: {sample_data}")

            # Local analysis-only agent
            analysis_agent = Agent(
                model=settings.AI_MODEL, # Could be a more powerful model if needed for analysis
                system_prompt=f'''
                You are the data analysis tool. Your purpose is to provide insights, summaries, and answers 
                to complex questions based on the provided sheet data. 
                You have been given a user's question and a sample of the data from their sheet.
                The sample data is: 
                {sample_data}

                Based on the user's prompt: "{prompt}", and the sample data, perform the analysis.
                If the sample data is insufficient for a comprehensive answer, state that you are basing your analysis 
                on the provided sample and the full data might yield more details.
                Provide your analysis as a text response. Your output must be in the standard AIResponse format, 
                specifically using the "message" type.
                For example:
                [
                    {{
                        "type": "message",
                        "value": "Based on the sample, the column 'Sales' appears to have an increasing trend..."
                    }}
                ]
                Do not attempt to use other tools. Focus solely on providing a textual analysis.
                ''',
                output_type=AIResponse # Expecting a structured response
            )
            
            # The prompt for the analysis_agent is effectively the user's original question/prompt.
            # The system prompt for analysis_agent already incorporates the sample_data and original prompt.
            res = await analysis_agent.run(prompt) # Pass the original user prompt to the analysis agent
            
            if os.path.exists(csv_file_name):
                os.remove(csv_file_name)
            
            return res.output

        except Exception as e:
            print(f"Error in _tool_analysis: {e}")
            if os.path.exists(csv_file_name):
                os.remove(csv_file_name)
            # Return a structured error message in AIResponse format
            return AIResponse(answer=json.dumps([{"type": "message", "value": f"Error during analysis: {str(e)}"}]))

    async def call(self, input: AIInput, user_id:str, org_id:str, req: Request):
        """
        Dispatch the prompt to the appropriate tool via the unified agent.
        Yields structured JSON chunks of the AI response.
        """
        
        ctx = SupportDependencies(
                user_id= user_id,
                org_id=org_id,
                context_source=input.context_source,
                request=req,
                sandbox=None, # Sandbox is only for tool execution contexts
                selectedCells=input.selectedCells
        )

        sample_csv_data_string = ""
        try:
            if ctx.deps.context_source: # Ensure there's a sheet ID
                print(f"Fetching sheet data sample for: {ctx.deps.context_source}")
                # Fetch full data, then take a sample. Max 5 lines.
                csv_data_io = await self.sheet_service.get_sheet_data_csv_by_id(ctx.deps.context_source, False)
                lines = []
                for i in range(5): # Read up to 5 lines
                    line = csv_data_io.readline()
                    if not line:
                        break
                    lines.append(line.strip())
                
                if lines:
                    sample_csv_data_string = "\n".join(lines)
                    print(f"Sample data:\n{sample_csv_data_string}")
                else:
                    sample_csv_data_string = "The sheet appears to be empty or no data could be sampled."
            else:
                sample_csv_data_string = "No sheet context provided for sampling."
        except Exception as e:
            print(f"Error fetching sheet data sample: {e}")
            sample_csv_data_string = "Could not retrieve a sample of the sheet data due to an error."

        enhanced_prompt_parts = [
            "System Note: You have access to a sample of the current sheet data to help answer direct questions. This sample is part of the user's message below. Use it for simple lookups. Do not pass this sample data or this note to any tools you call.",
            "Sheet Data Sample (CSV format, up to 5 rows including header):",
            sample_csv_data_string,
            "---",
            f"User Prompt: {input.prompt}"
        ]
        
        adjusted_input_cells_str = ""
        if input.selectedCells:
            adjusted_input_cells = {
                'left': input.selectedCells['left'],
                'right': input.selectedCells['right'],
                'top': input.selectedCells['top'] - 1,
                'bottom': input.selectedCells['bottom'] - 1,
            }
            adjusted_input_cells_str = f"Selected cells (0-indexed, from API): {adjusted_input_cells}"
            enhanced_prompt_parts.append(adjusted_input_cells_str)

        enhanced_prompt_for_agent = "\n".join(enhanced_prompt_parts)
        
        # Attempt to stream the response from the agent
        async for chunk in self.agent.stream_run(enhanced_prompt_for_agent, deps=ctx):
            # Handle different types of StreamingChunk
            if chunk.text is not None and chunk.text != "": # Text chunk
                yield {"type": "message", "value": chunk.text}
            
            if chunk.tool_call is not None:
                # Potentially log or handle tool call start if needed
                # For now, we'll wait for tool_output
                pass

            if chunk.tool_output is not None:
                # Tool output is a string, needs parsing.
                # This assumes tool output is structured like the 'answer' field in AIResponse
                # or parts of it.
                try:
                    tool_data_str = chunk.tool_output
                    # The output from tools like _tool_graph is GraphAgentFinalResponse,
                    # which is then wrapped into the AIResponse format by the agent's system prompt.
                    # stream_run's tool_output for pydantic-ai gives the direct tool function's return.
                    # We need to ensure this is formatted correctly or adapt.
                    # For now, let's assume the agent's final processing will format this.
                    # The actual output of the tool (e.g., GraphAgentFinalResponse) is in chunk.tool_output
                    # The agent's system prompt expects a JSON array.
                    # Let's try to parse it directly if it's simple, or wrap it.
                    # The current tools (_tool_graph, _tool_predict) return Pydantic models.
                    # The agent's system prompt tells the LLM to structure its *final* answer
                    # as a JSON array of objects. When a tool is called, the LLM first outputs
                    # a tool_call, then the tool runs, then its output is fed back to the LLM,
                    # which then generates the final response.
                    # The `chunk.tool_output` should be the direct output of our _tool_xxx methods.
                    
                    # The main agent's output_type is AIResponse.
                    # The system prompt dictates the *final* JSON structure.
                    # When a tool is called, its direct output (e.g., GraphAgentFinalResponse)
                    # is returned in `chunk.tool_output`. This output is then fed back to the LLM.
                    # The LLM then crafts a *new* response based on this tool output, adhering to the
                    # main system prompt's JSON array structure.
                    # So, we should primarily be interested in `chunk.text` for streaming intermediate text
                    # and `chunk.model_output` for the final structured response from the LLM.
                    # `chunk.tool_output` itself might not need to be directly yielded to the client in this format,
                    # but rather it's an intermediate step.
                    # However, if the tool itself produces something directly displayable and we want to show it early,
                    # we might yield it. For now, let's assume the final response will come via model_output or text.
                    print(f"Tool output: {chunk.tool_output}") # Logging for now

                except Exception as e:
                    print(f"Error processing tool_output chunk: {e}")
                    # yield {"type": "error", "value": f"Error processing tool output: {str(e)}"}


            if chunk.model_output is not None:
                # model_output contains the final response from the LLM, which should be AIResponse.
                # The 'answer' field of AIResponse is a string that needs to be parsed into a list of dicts.
                final_response_obj = chunk.model_output # This is already an AIResponse object
                if isinstance(final_response_obj, AIResponse) and isinstance(final_response_obj.answer, str):
                    try:
                        answer_list = json.loads(repair_json(final_response_obj.answer))
                        for item in answer_list:
                            # Process items as before (e.g., parsing 'action' or 'data_table' values)
                            if item.get('type') == 'action' and isinstance(item.get('value'), str):
                                item['value'] = json.loads(repair_json(item['value']))
                            elif item.get('type') == 'data_table' and isinstance(item.get('value'), str):
                                table_data = json.loads(repair_json(item['value']))
                                item['value'] = {
                                    "headers": table_data.get("headers", []),
                                    "data": parse_table_json(table_data.get("headers", []), table_data.get("data", []))
                                }
                            yield item
                    except json.JSONDecodeError as e:
                        print(f"JSON decode error in model_output: {e}")
                        # yield {"type": "error", "value": "Failed to parse final AI response."}
                    except Exception as e:
                        print(f"Error processing model_output: {e}")
                        # yield {"type": "error", "value": "Error processing final AI response."}
                elif isinstance(final_response_obj, dict): # If it's already a dict (e.g. from a sub-agent without strong typing)
                    # This case might occur if a sub-agent doesn't strictly return AIResponse
                    # Or if the structure is different than expected.
                    # We should try to adapt or log this.
                    # For now, assume it matches the item structure {type: ..., value: ...}
                    yield final_response_obj


        # The following is a placeholder for how tool outputs might be handled.
        # If agent.stream() handles tools correctly and yields their output,
        # this manual handling might not be necessary.
        # For now, this is commented out as we test agent.stream()

        # result = await self.agent.run(input.prompt + f"Selected cells: {adjusted_input_cells}", deps=ctx)
        # print("MODEL DUMP", result.output.model_dump())
        # model_dumped = result.output.model_dump()
        # answer_response = json.loads(repair_json(model_dumped['answer']))
        
        # for msg in answer_response:
        #     print("MESSAGE", msg)
        #     if(msg['type'] == 'action'):
        #         msg['value'] = json.loads(repair_json(str(msg['value'])))
                
        #     if(msg['type'] == 'data_table'):
        #         table_data = json.loads(repair_json(str(msg['value'])))
        #         table_formatted = {
        #             "headers": table_data["headers"],
        #             "data": parse_table_json(table_data['headers'], table_data['data'])
        #         }
        #         msg['value'] = table_formatted
        # print(answer_response)
        
        # yield model_dumped # This would yield the whole response at once
