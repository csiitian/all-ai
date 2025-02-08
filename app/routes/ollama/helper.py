import re

def remove_think_tags(text):
  return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)

def parseDeepseekResponse(response):
  return remove_think_tags(response)