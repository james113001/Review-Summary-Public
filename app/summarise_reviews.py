from ollama import chat, ChatResponse

def summarize_reviews(reviews: list[str]) -> str:
    """
    Summarize a list of product reviews into a short, clear summary.
    
    Args:
        reviews (list[str]): List of review texts.
    
    Returns:
        str: Summary of reviews.
    """
    if not reviews:
        return "No reviews available for summarization."

    # Build prompt for the language model
    prompt = "Summarize the following product reviews into a short, clear, and honest summary:\n\n"
    for r in reviews:
        prompt += f"- {r}\n"
    prompt += "\nReturn a concise and useful summary."

    print("\n--- Prompt Sent to Model ---")
    print(prompt)

    try:
        response: ChatResponse = chat(
            model='mistral',
            messages=[{"role": "user", "content": prompt}]
        )
        return response['message']['content']
    except Exception as e:
        print("Error during chat:", e)
        return "Error generating summary."
