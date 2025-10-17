# ai_pricing.py
import os
import re
import pandas as pd

try:
    from openai import OpenAI, OpenAIError
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# Initialize OpenAI client only if key exists
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = None
if OPENAI_AVAILABLE and OPENAI_API_KEY:
    client = OpenAI(api_key=OPENAI_API_KEY)
else:
    print("⚠️ OpenAI API not available or API key missing. AI pricing disabled.")

# -------------------------------
# 🔹 AI Rate Fetching
# -------------------------------
def get_rate_from_ai(element, description, unit, location="local"):
    """
    Query GPT to suggest a unit rate for a BoQ item.
    Falls back gracefully if API key is missing or invalid.
    """
    if not (OPENAI_AVAILABLE and client):
        # Skip AI rate lookup if OpenAI not set up
        return None

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
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful QS assistant providing accurate construction unit rates."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )
        rate_str = response.choices[0].message.content.strip()
        rate_str = re.sub(r"[^\d.]", "", rate_str)

        return float(rate_str) if rate_str else None

    except OpenAIError as e:
        print(f"AI pricing error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected AI pricing error: {e}")
        return None


# -------------------------------
# 🔹 Local Rate Library
# -------------------------------
_RATE_LIBRARY = None

def _load_rate_library():
    """Load rate_library.csv into memory."""
    global _RATE_LIBRARY
    csv_path = os.path.join(os.getcwd(), "rate_library.csv")

    if not os.path.exists(csv_path):
        print("⚠️ rate_library.csv not found.")
        _RATE_LIBRARY = pd.DataFrame(columns=["Element", "Unit", "Rate"])
        return

    try:
        _RATE_LIBRARY = pd.read_csv(csv_path, comment="#").dropna(subset=["Element"])
        _RATE_LIBRARY["Element"] = _RATE_LIBRARY["Element"].str.strip().str.lower()
        _RATE_LIBRARY["Unit"] = _RATE_LIBRARY["Unit"].str.strip().str.lower()
    except Exception as e:
        print(f"⚠️ Error loading rate_library.csv: {e}")
        _RATE_LIBRARY = pd.DataFrame(columns=["Element", "Unit", "Rate"])


def get_rate_from_library(element: str, description: str = "", unit: str = ""):
    """Retrieve a rate from the local rate_library.csv file."""
    global _RATE_LIBRARY
    if _RATE_LIBRARY is None:
        _load_rate_library()

    if _RATE_LIBRARY.empty:
        return None

    element_key = (element or "").strip().lower()
    unit_key = (unit or "").strip().lower()

    # Try exact match
    match = _RATE_LIBRARY[
        (_RATE_LIBRARY["Element"] == element_key) &
        (_RATE_LIBRARY["Unit"] == unit_key)
    ]

    # Fallback: element only
    if match.empty:
        match = _RATE_LIBRARY[_RATE_LIBRARY["Element"] == element_key]

    if not match.empty:
        try:
            return float(match.iloc[0]["Rate"])
        except ValueError:
            return None

    # Fuzzy match
    for _, row in _RATE_LIBRARY.iterrows():
        if element_key in row["Element"]:
            try:
                return float(row["Rate"])
            except ValueError:
                continue

    return None


# -------------------------------
# 🔹 Debugging
# -------------------------------
if __name__ == "__main__":
    print("🔍 Testing rate lookup from library...")
    print("Blockwork (m²):", get_rate_from_library("Blockwork", unit="m²"))
    print("Excavation (m³):", get_rate_from_library("Excavation", unit="m³"))
    print("Painting (m²):", get_rate_from_library("Painting", unit="m²"))
    print("Doors (No.):", get_rate_from_library("Doors", unit="No."))
    if OPENAI_AVAILABLE and client:
        print("\n🔍 Testing AI rate fetching...")
        ai_rate = get_rate_from_ai("Concrete Slab", "Concrete slab 150mm thick", "m²")
        print("AI suggested rate for Concrete Slab (m²):", ai_rate)
    else:
        print("\n⚠️ OpenAI API not available or API key missing. Skipping AI rate test.")


    