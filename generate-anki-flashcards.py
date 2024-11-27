#%%
from dotenv import load_dotenv
from openai import OpenAI 

load_dotenv()

client = OpenAI()

#%%Load the contents of one markdown file
with open("assets/baroque-essay.md", "r") as file:
    baroque = file.read()

print(baroque)
# %%


