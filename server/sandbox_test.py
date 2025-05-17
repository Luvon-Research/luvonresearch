from dotenv import load_dotenv
load_dotenv()
from e2b_code_interpreter import Sandbox

sbx = Sandbox() # By default the sandbox is alive for 5 minutes

file_data = None

sbx.files.write('test.csv', "hello")
code = '''
x = 10
print(x)
'''
execution = sbx.run_code(code) # Execute Python inside the sandbox
print(execution.logs)

code = '''
x += 1
print(x)
'''
execution1 = sbx.run_code(code) # Execute Python inside the sandbox
print(execution1)

files = sbx.files.list("/")
# print(files)
# print("--------------")

sbx.kill()
#f = sbx.files.read("test.txt")
#print(f)