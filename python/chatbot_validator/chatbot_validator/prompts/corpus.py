v0 = """Your task is to take a scientific assertion and return between 1 and 3 phrases that can be entered into a search engine to learn more about this assertion.

The phrases must be formatted as a bulleted list of the following form. No other response is acceptable.
- Phrase 1
- Phrase 2
and so on. 
The response cannot contain any other text, HTML, or be a numbered list.
You can assume that I am an expert in biology and do not need background knowledge, so make the search phrases as specific as possible.

Input: {human_input}

Search phrases:"""

#######################################################

structure_output_template = """The phrases must be formatted as a python list of the following form. 
[
    phrase_1,
    phrase_2,
    ...
]
where each `phrase_i` is a string.
No other response is acceptable.
"""

v1 = """Your task is to take the scientific assertion in triple backticks below \
and return between 1 and 3 phrases that can be entered into the OpenAlex search engine to learn more about the assertion.

The response cannot contain any other text, HTML, or be a numbered list.
You can assume that I am an expert in many fields of science and do not need background knowledge, \
so make the search phrases as specific as possible.

{{ structure_output_template }}

Scientific assertion: ```{{ human_input }}```

Search phrases:"""
