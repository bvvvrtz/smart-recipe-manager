import os
import json
from openai import OpenAI

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

def analyze_image_for_ingredients(image_base64: str) -> list:
    prompt = """
    Przeanalizuj to zdjęcie (lodówki lub paragonu ze sklepów spożywczych). 
    Wypisz wszystkie znalezione produkty spożywcze.
    Zwróć odpowiedź WYŁĄCZNIE w formacie JSON jako tablicę obiektów, bez żadnego dodatkowego tekstu markdown.
    Każdy obiekt musi mieć klucze:
    - "name": nazwa produktu po polsku (np. "Mleko 3.2%", "Pierś z kurczaka")
    - "quantity": szacowana ilość lub waga (np. "1 szt.", "500g")
    - "days_left": szacowany czas przydatności w dniach (liczba całkowita, np. 3, 7, 14)
    
    Przykład:
    [
      {"name": "Mleko", "quantity": "1L", "days_left": 5},
      {"name": "Kurczak", "quantity": "400g", "days_left": 3}
    ]
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}
                        }
                    ]
                }
            ],
            max_tokens=1000,
            temperature=0.3
        )
        content = response.choices[0].message.content.strip()
        if content.startswith("```json"):
            content = content[7:-3].strip()
        elif content.startswith("```"):
            content = content[3:-3].strip()
        return json.loads(content)
    except Exception as e:
        return [{"name": "Produkt z analizy", "quantity": "1 szt.", "days_left": 5}]

def generate_recipe_from_ingredients(ingredients: list, style: str = "Dowolny") -> dict:
    ing_list_str = ", ".join([f"{i['name']} ({i.get('quantity', '1 szt.')}, ważne jeszcze {i.get('days_left', 5)} dni)" for i in ingredients])
    
    prompt = f"""
    Jesteś profesjonalnym szefem kuchni oraz dietetykiem. 
    Użytkownik ma w lodówce następujące składniki: {ing_list_str}.
    Wymagany styl gotowania / preferencja: {style}.
    
    Ułóż jeden świetny, konkretny przepis wykorzystujący w pierwszej kolejności składniki, które szybciej się psują.
    Jeśli do przepisu brakuje jakichś produktów (poza podstawowymi typu woda, sól, pieprz, oliwa/olej), wypisz je w polu "missing_ingredients".
    
    Zwróć odpowiedź WYŁĄCZNIE w formacie JSON (bez żadnego dodatkowego tekstu markdown) dokładnie w tej strukturze:
    {{
        "title": "Nazwa dania",
        "prep_time": "20 min",
        "calories": "ok. 550 kcal",
        "macros": "B: 38g | T: 18g | W: 60g",
        "recipe_text": "Dokładny opis przygotowania krok po kroku...",
        "missing_ingredients": ["Składnik 1", "Składnik 2"]
    }}
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        content = response.choices[0].message.content.strip()
        if content.startswith("```json"):
            content = content[7:-3].strip()
        elif content.startswith("```"):
            content = content[3:-3].strip()
        return json.loads(content)
    except Exception as e:
        return {
            "title": "Omlet domowy z warzywami",
            "prep_time": "15 min",
            "calories": "ok. 400 kcal",
            "macros": "B: 25g | T: 20g | W: 25g",
            "recipe_text": "1. Roztrzep jajka.\n2. Usmaż na patelni z dodatkiem warzyw.",
            "missing_ingredients": []
        }

def estimate_meal_macros(meal_description: str) -> dict:
    prompt = f"""
    Jesteś profesjonalnym dietetykiem i systemem analizy makroskładników.
    Przeanalizuj poniższy opis posiłku zjedzonego przez użytkownika i oszacuj jego kalorie oraz makroskładniki.
    
    Opis posiłku: "{meal_description}"
    
    Zwróć odpowiedź WYŁĄCZNIE w formacie JSON (bez żadnego dodatkowego tekstu markdown), dokładnie w takiej strukturze:
    {{
        "name": "Poprawiona, ładna nazwa potrawy",
        "calories": 500,
        "protein": 35,
        "fat": 15,
        "carbs": 60
    }}
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        content = response.choices[0].message.content.strip()
        if content.startswith("```json"):
            content = content[7:-3].strip()
        elif content.startswith("```"):
            content = content[3:-3].strip()
        return json.loads(content)
    except Exception as e:
        return {
            "name": meal_description,
            "calories": 400,
            "protein": 25,
            "fat": 12,
            "carbs": 45
        }