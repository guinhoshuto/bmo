import llm from utils.gemini import *


test = llm.invoke("Hello, how are you?")
print(test)