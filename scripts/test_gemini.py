from app.services.gemini_service import interpret_query


query = "I want wireless headphones under 5000 for gaming"


result = interpret_query(query)


print("\nGemini Response:\n")
print(result)