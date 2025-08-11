import os
import re
from openai import OpenAI
import pandas as pd

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_rate_from_ai(element, description, unit, location="local"):
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
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful QS assistant providing accurate construction unit rates."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )

        rate_str = response.choices[0].message.content.strip()
        rate_str = re.sub(r"[^\d.]", "", rate_str)  # Remove currency symbols, text

        try:
            return float(rate_str)
        except ValueError:
            print(f"⚠️ Could not parse AI rate: {rate_str}")
            return None

    except Exception as e:
        print(f"AI pricing error: {e}")
        return None

def get_rate_from_library(element, description, unit):
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
    