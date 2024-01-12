v0_validator = """Your task is to take the logical assertion in triple backticks below and determine whether it is a) obvious or nonsense, or b) non-obvious.

If the assertion is obvious or nonsense, return a single sentence explaining why. If the assertion is both non-obvious and not nonsense, return 'non-obvious' and no other output.

Assertion: ```{{ assertion }}```"""

v0 = """Your task is to take input text about a scientific topic, and decompose it into a set of independent scientific assertions.
These assertions will later be used in the OpenAlex search engine to help people find scientific information, so it is important that they are concise and \
specific to the input text.

The assertions must be formatted as a bulleted list of the following form. No other response is acceptable.
- Assertion 1
- Assertion 2
and so on. 
The response cannot contain any other text, HTML, or be a numbered list.
You may not include or infer any assertions that are not present in the input.
You must not include any additional text, such as citations that are not present in the input.
Do not include anything that may be qualified as "general knowledge" or "common sense" - focus on the most significant assertions.
Choose the assertions such that if they are all true, then the statement is true.

Examples:
Input: The dog is brown and does not like to play fetch. The cat is asleep.
Output:
- The dog is brown.
- The dog does not like to play fetch.
- The cat is asleep.

Input: The Earth revolves around the Sun, takes about 365.25 days for a full orbit, has a slightly tilted axis, and is the third planet from the Sun.
Output:
- The Earth revolves around the Sun.
- The Earth takes 365.25 days to fully orbit the sun.
- The Earth has a slightly tilted axis.
- The Earth is the third planet from the Sun.

Input: The human brain consists of approximately 86 billion neurons, communicates through complex networks of synapses, is protected by the skull and meninges, and consumes about 20% of the body's energy.
Output:
- The human brain consists of approximately 86 billion neurons.
- The brain communicates through complex networks of synapses.
- The brain is protected by the skull and meninges.
- The brain consumes about 20% of the body's energy.


Input: {{ human_input }}
Output:"""

#########################################################

v0_alt = """Your task is to take a sentence or paragraph, and decompose it into a set of at least one non-obvious scientific assertion.

The assertions must be formatted as a bulleted list of the following form. No other response is acceptable.
- Assertion 1
- Assertion 2
and so on. 
Don't create assertions that rely on other assertions through logical relationships like "therefore", "because".
The response cannot contain any other text, HTML, or be a numbered list.
You may not include or infer any assertions that are not present in the input.

For example, the statement "Fusion between cancer cells that are genetically distinct or between cancer and noncancer cells promotes tumor progression." should be decomposed into the following assertions:
- Fusion between cancer cells that are genetically distinct promotes tumor progression.
- Fusion between cancer and noncancer cells promotes tumor progression.

Input: {{ human_input }}

Assertions:"""

structure_output_template = """The assertions must be formatted as python list of the following form:
[
    assertion_1,
    assertion_2,
    ...
]
where each `assertion_i` is a string.
There should be no additional text.
"""

#########################################################

v1 = """Your task is to take input text about a scientific topic within the triple backticks below, and decompose it into a set of independent scientific assertions.
These assertions will later be used in the OpenAlex search engine to help people find scientific information, so it is important that they are concise and \
specific to the input text.

The assertions cannot contain any other text, HTML, or be a numbered list.
Do not include or infer any assertions that are not present in the input.
Do not include any additional text, such as citations that are not present in the input.
Do not include anything that may be qualified as "general knowledge" or "common sense". Focus on the most significant assertions.
Choose the assertions such that if they are all true, then the statement is true.

{{ structure_output_template }}

Examples:
Input: ```The dog is brown and does not like to play fetch. The cat is asleep.```
Output:
[
    "The dog is brown.",
    "The dog does not like to play fetch.",
    "The cat is asleep."
]


Input: ```The Earth revolves around the Sun, takes about 365.25 days for a full orbit, has a slightly tilted axis, and is the third planet from the Sun.```
Output:
[
    "The Earth revolves around the Sun.",
    "The Earth takes 365.25 days to fully orbit the sun.",
    "The Earth has a slightly tilted axis.",
    "The Earth is the third planet from the Sun."
]


Input: ```The human brain consists of approximately 86 billion neurons, communicates through complex networks of synapses, is protected by the skull and meninges, and consumes about 20% of the body's energy.```
Output:
[
    "The human brain consists of approximately 86 billion neurons.",
    "The brain communicates through complex networks of synapses.",
    "The brain is protected by the skull and meninges.",
    "The brain consumes about 20% of the body's energy."
]


Input: ```{{ human_input }}```
Output:"""

#########################################################

v1_alt = """Your task is to take a sentence or paragraph, and decompose it into a set of at least one non-obvious scientific assertion.

Don't create assertions that rely on other assertions through logical relationships like "therefore", "because".
The response cannot contain any other text, HTML, or be a numbered list.
You may not include or infer any assertions that are not present in the input.

{{ structure_output_template }}

For example, the statement "Fusion between cancer cells that are genetically distinct or between cancer and noncancer cells promotes tumor progression." should be decomposed into the following assertions:
- Fusion between cancer cells that are genetically distinct promotes tumor progression.
- Fusion between cancer and noncancer cells promotes tumor progression.

Input: {{ human_input }}

Assertions:"""
