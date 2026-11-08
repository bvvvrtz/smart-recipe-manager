import os
import json
from datetime import datetime
from openai import OpenAI

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

def analyze_image_for_ingredients(image_base64: str) -> list:
    prompt = """
    Przeanalizuj to zdjęcie (lodówki lub paragonu ze sklepów spożywczych). 
    Wypisz wszystkie znalezione produkty spożywcze.
    Jeśli na zdjęciu NIE MA żadnych produktów spożywczych ani paragonu, zwróć pustą tablicę: []
    Zwróć odpowiedź WYŁĄCZNIE w formacie JSON jako tablicę obiektów, bez żadnego dodatkowego tekstu markdown.
    Każdy obiekt musi mieć klucze:
    - "name": nazwa produktu po polsku (np. "Mleko 3.2%", "Pierś z kurczaka")
    - "quantity": szacowana ilość lub waga (np. "1 szt.", "500g")
    - "days_left": szacowany czas przydatności w dniach (liczba całkowita, np. 3, 7, 14)
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
        return []

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

def calculate_nutrition_onboarding(data: dict) -> dict:
    current_year = datetime.now().year
    prompt = f"""
    Jesteś zaawansowanym dietetykiem sportowym i klinicznym.
    Oblicz dzienne zapotrzebowanie kaloryczne oraz optymalny rozkład makroskładników (Białko, Tłuszcze, Węglowodany) dla użytkownika o następujących parametrach:
    - Płeć: {data.get('gender')}
    - Data urodzenia: {data.get('birth_date')} (aktualny rok to {current_year})
    - Wzrost: {data.get('height')} cm
    - Aktualna waga: {data.get('current_weight')} kg
    - Docelowa waga: {data.get('target_weight')} kg
    - Tempo zmiany wagi (wahanie tygodniowe): {data.get('weekly_pace')}
    - Ilość treningów w tygodniu: {data.get('workouts_per_week')}
    - Poziom ruchu w ciągu dnia (poza treningami): {data.get('daily_activity')}

    Weź pod uwagę wzór Mifflin-St Jeor, współczynnik aktywności PAL (NEAT + EAT), a następnie dodaj lub odejmij kalorie zgodnie z wybranym tempem zmiany wagi (1 kg tkanki tłuszczowej to ok. 7700 kcal, więc 0.5 kg/tydzień to ok. 550 kcal deficytu/nadwyżki dziennie). Zadbaj o wysoką podaż białka wspierającą sylwetkę.

    Zwróć odpowiedź WYŁĄCZNIE w formacie JSON (bez bloków markdown), dokładnie w takiej strukturze:
    {{
        "calories_goal": 2400,
        "protein_goal": 160,
        "fat_goal": 75,
        "carbs_goal": 270
    }}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        content = response.choices[0].message.content.strip()
        if content.startswith("```json"):
            content = content[7:-3].strip()
        elif content.startswith("```"):
            content = content[3:-3].strip()
        return json.loads(content)
    except Exception as e:
        return {
            "calories_goal": 2400,
            "protein_goal": 160,
            "fat_goal": 75,
            "carbs_goal": 270
        }