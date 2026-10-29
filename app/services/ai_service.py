import os
import json
from openai import OpenAI
from typing import List, Dict, Any

# WKLEJ SWÓJ KLUCZ API PONIŻEJ:
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

def generate_recipe_from_ingredients(items_data: List[Dict[str, Any]], style: str = "Dowolny") -> Dict[str, Any]:
    """Generuje ustrukturyzowany przepis z kaloriami, makro i listą brakujących składników"""
    if not items_data:
        return {
            "title": "Pusta lodówka!",
            "prep_time": "0 min",
            "calories": "0 kcal",
            "macros": "B: 0g | T: 0g | W: 0g",
            "missing_ingredients": [],
            "recipe_text": "Dodaj produkty do lodówki lub zeskanuj paragon, aby wygenerować przepis!"
        }

    # Formatujemy listę składników wraz z ich terminem ważności
    formatted_items = [
        f"{item['name']} ({item['quantity']}, ważne jeszcze: {item['days_left']} dni)"
        for item in items_data
    ]
    ingredients_str = ", ".join(formatted_items)

    prompt = f"""
    Jesteś szefem kuchni Zero Waste oraz dietetykiem.
    Składniki w lodówce: {ingredients_str}.
    Wybrany styl kuchni / sprzęt: {style}.

    Priorytetowo wykorzystaj składniki, którym zostało najmniej dni ważności!
    Zwróć odpowiedź WYŁĄCZNIE jako czysty obiekt JSON w następującym formacie:
    {{
        "title": "Nazwa dania",
        "prep_time": "np. 20 min",
        "calories": "np. 620 kcal",
        "macros": "np. B: 38g | T: 22g | W: 65g",
        "missing_ingredients": ["ewentualny brakujący składnik 1", "składnik 2"],
        "recipe_text": "Dokładna instrukcja krok po kroku oraz lista użytych składników z gramaturą (używaj znaków nowej linii \\n)."
    }}
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": "Zwracasz wyłącznie poprawny kod JSON z przepisem kulinarnym po polsku."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )

    try:
        return json.loads(response.choices[0].message.content)
    except Exception:
        return {
            "title": "Przepis Zero Waste",
            "prep_time": "25 min",
            "calories": "~500 kcal",
            "macros": "B: 25g | T: 15g | W: 50g",
            "missing_ingredients": [],
            "recipe_text": response.choices[0].message.content
        }


def analyze_image_for_ingredients(image_base64: str) -> List[Dict[str, Any]]:
    """Rozpoznaje produkty ze zdjęcia lodówki LUB paragonu sklepowego i szacuje dni ważności"""
    prompt = """
    Przeanalizuj to zdjęcie. Może to być wnętrze lodówki, produkty na blacie LUB paragon ze sklepu.
    Jeśli to paragon, rozszyfruj skróty nazw produktów spożywczych na pełne polskie nazwy (pomiń chemię, reklamówki i kwoty).
    Dla każdego produktu oszacuj domyślną świeżość w dniach (days_left: np. 2-3 dla mięsa/ryb, 5-7 dla nabiału/warzyw, 14+ dla sosów/suchych).
    
    Zwróć odpowiedź WYŁĄCZNIE jako obiekt JSON w formacie:
    {
        "items": [
            {"name": "Kurczak", "quantity": "1 op.", "days_left": 3},
            {"name": "Mleko", "quantity": "1 szt.", "days_left": 7}
        ]
    }
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"},
                    },
                ],
            }
        ],
        max_tokens=500,
    )

    try:
        data = json.loads(response.choices[0].message.content)
        return data.get("items", [])
    except Exception:
        return []