from dotenv import load_dotenv
load_dotenv()
from e2b_code_interpreter import Sandbox

sbx = Sandbox(timeout=20) # By default the sandbox is alive for 5 minutes

file_data = None

csv_data = '''
X,Y
1,1
2,4
3,9
4,16
5,25
6,36
7,
8,
9,
10,
11,
12,
'''
sbx.files.write('test.csv', csv_data)
code = '''
import pandas as pd
from sklearn.linear_model import LinearRegression

# 1) Load CSV (with header row)
df = pd.read_csv("/home/user/test.csv")

# 2) Define test rows for X=7…12  (indices 6 through 11)
test_indices = list(range(6, 12))

# 3) Split
test_df  = df.loc[test_indices]
train_df = df.drop(index=test_indices)

# 4) Ensure no NaN in training targets
train_df = train_df.dropna(subset=['Y'])

# 5) Train
X_train = train_df[['X']]
y_train = train_df['Y']
model   = LinearRegression().fit(X_train, y_train)

# 6) Predict
X_test = test_df[['X']]
y_pred = model.predict(X_test)

# 7) Output
results = pd.DataFrame({
    'X': test_df['X'].values,
    'Predicted_Y': y_pred
})

print("Table headers:", results.columns.tolist())
print("Table data:", results.values.tolist())
'''
execution = sbx.run_code(code) # Execute Python inside the sandbox
print(execution)

# files = sbx.files.list("/")
# print(files)
# print("--------------")

sbx.kill()
#f = sbx.files.read("test.txt")
#print(f)

