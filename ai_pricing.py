import os
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_rate_from_ai(element, description, unit, location=""):
    """
    Uses GPT model to suggest a unit rate based on BoQ item description.
    """
    prompt = f"""
    You are a professional Quantity Surveyor familiar with {location} construction market rates.
    Provide a realistic unit rate for the following BoQ item:
    Element: {element}
    Description: {description}
    Unit: {unit}
    Output ONLY the number without currency symbol or extra text.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Faster, cheaper model; change to "gpt-4" if needed
            messages=[
                {"role": "system", "content": "You are a helpful QS assistant providing accurate construction unit rates."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )

        rate_str = response.choices[0].message.content.strip()

        # Try to convert to float
        try:
            rate = float(rate_str)
        except ValueError:
            print(f"⚠️ Could not parse AI rate: {rate_str}")
            rate = None

        return rate

    except Exception as e:
        print(f"AI pricing error: {e}")
        return None


def get_rate_from_library(element, description, unit):
    """
    Look up rate from a local CSV library (rate_library.csv).
    """
    import pandas as pd

    try:
        df = pd.read_csv("rate_library.csv")
        match = df[
            (df["Element"].str.lower() == element.lower()) &
            (df["Unit"].str.lower() == unit.lower())
        ]

        if not match.empty:
            return float(match.iloc[0]["Rate"])

    except FileNotFoundError:
        print("⚠️ rate_library.csv not found.")
    except Exception as e:
        print(f"Error reading rate library: {e}")

    return None

