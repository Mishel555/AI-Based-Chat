v0 = """
Current conversation:
{% if history is defined %}
{{ history }}
{% endif %}
Human: {{ human_input }}
AI: 
"""
