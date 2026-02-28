from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import re

# Premium Product Initialization
app = FastAPI(
    title="ProText: Advanced Academic English & Essay Analyzer API",
    description="A premium NLP-lite API for EdTech. Calculates Flesch-Kincaid grade levels, extracts academic vocabulary, and estimates CEFR/IELTS scores without external API dependencies."
)

class TextRequest(BaseModel):
    text: str

# Helper Function 1: English Syllable Counter
def count_syllables(word: str) -> int:
    word = word.lower()
    if len(word) <= 3:
        return 1
    count = 0
    vowels = "aeiouy"
    if word[0] in vowels:
        count += 1
    for index in range(1, len(word)):
        if word[index] in vowels and word[index - 1] not in vowels:
            count += 1
    if word.endswith("e"):
        count -= 1
    if word.endswith("le") and len(word) > 2 and word[-3] not in vowels:
        count += 1
    if count == 0:
        count += 1
    return count

@app.post("/api/v1/analyze-text")
def analyze_text(request: TextRequest):
    text = request.text
    
    if not text or len(text.strip()) < 20:
        raise HTTPException(status_code=400, detail="Text is too short. Please provide a substantive paragraph or essay for accurate analysis.")

    try:
        # 1. Text Parsing
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        sentences = [s for s in re.split(r'[.!?]+', text) if len(s.strip()) > 0]
        
        word_count = len(words)
        sentence_count = len(sentences)
        
        # Guard clause to prevent division by zero
        if word_count == 0 or sentence_count == 0:
            raise ValueError("No valid words or sentences found.")

        # 2. Syllable Calculation
        total_syllables = sum(count_syllables(word) for word in words)
        
        # 3. Scientific Readability: Flesch-Kincaid Grade Level Formula
        # Formula: 0.39 * (words/sentences) + 11.8 * (syllables/words) - 15.59
        avg_words_per_sentence = word_count / sentence_count
        avg_syllables_per_word = total_syllables / word_count
        
        fk_grade = (0.39 * avg_words_per_sentence) + (11.8 * avg_syllables_per_word) - 15.59
        fk_grade = max(0, round(fk_grade, 1)) # Prevent negative scores
        
        # 4. Academic Vocabulary Simulation (Targeting rigorous academic/transfer program levels)
        # In a real heavy-weight app, this would query a database. Here we use an algorithmic heuristic
        # that catches complex academic suffix/prefix structures + length.
        academic_words = set()
        for word in words:
            if len(word) >= 9 or (len(word) >= 7 and count_syllables(word) >= 3):
                academic_words.add(word)
        academic_words_list = list(academic_words)
        
        # 5. CEFR / IELTS Logic strictly based on Flesch-Kincaid Grade Level
        score_estimate = "B1 (Intermediate)"
        ielts_band = "5.0 - 5.5"
        
        if fk_grade >= 12: # College/University level
            score_estimate = "C1/C2 (Advanced/Proficient)"
            ielts_band = "7.5+"
        elif fk_grade >= 9: # High School level
            score_estimate = "B2 (Upper Intermediate)"
            ielts_band = "6.0 - 7.0"

        # 6. Structured Premium Output
        return {
            "status": "success",
            "metrics": {
                "total_words": word_count,
                "total_sentences": sentence_count,
                "total_syllables": total_syllables,
                "average_words_per_sentence": round(avg_words_per_sentence, 2),
                "average_syllables_per_word": round(avg_syllables_per_word, 2)
            },
            "scientific_readability": {
                "flesch_kincaid_grade_level": fk_grade,
                "reading_level_description": f"Grade {round(fk_grade)} (US Education System)"
            },
            "proficiency_analysis": {
                "estimated_cefr_level": score_estimate,
                "estimated_ielts_band": ielts_band,
                "academic_vocabulary_count": len(academic_words_list),
                "academic_vocabulary_extracted": academic_words_list[:15]
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis engine error: {str(e)}")
