import pandas as pd
import openai

# Set your API key in environment: export OPENAI_API_KEY='your_key_here'

def get_rate_from_library(element, description, unit):
    try:
        df = pd.read_csv("rate_library.csv")
        match = df[
            (df["Element"].str.lower() == element.lower()) &
            (df["Description"].str.lower() == description.lower()) &
            (df["Unit"].str.lower() == unit.lower())
        ]
        if not match.empty:
            return float(match.iloc[0]["Rate"])
    except FileNotFoundError:
        pass
    return None

def get_rate_from_ai(element, description, unit, location="Nigeria"):
    prompt = f"""
    You are a quantity surveyor. Provide a realistic market unit rate for the following BoQ item:

    Element: {element}
    Description: {description}
    Unit: {unit}
    Location: {location}

    Respond with only the numeric rate value in {unit}, without currency symbols.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        rate_text = response.choices[0].message["content"].strip()
        return float(rate_text)
    except Exception as e:
        print(f"AI pricing error: {e}")
        return None
