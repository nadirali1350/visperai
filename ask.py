from operator import length_hint
import os
import openai
import config
openai.api_key = config.OPENAI_API_KEY

def ask_here(query):
    response = openai.Completion.create(
      model="text-davinci-002",
      prompt="answer me: {}".format(query),
      temperature=0.98,
      max_tokens=500,
      top_p=1,
      frequency_penalty=0,
      presence_penalty=0
)
    if response.choices:
        if len(response['choices']) > 0:
            answer= response['choices'][0]['text']
        else:
            answer = "No answer found"
    else:
        answer = "No answer found"

    return answer