from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import re

# Initialize the API with professional English descriptions
app = FastAPI(
    title="Academic English & Essay Analyzer API",
    description="Analyzes English text, extracts advanced vocabulary, calculates readability, and estimates academic proficiency levels."
)

# The expected input format from the user/developer
class TextRequest(BaseModel):
    text: str

@app.post("/api/v1/analyze-text")
def analyze_text(request: TextRequest):
    text = request.text
    
    # Check if the text is too short to analyze properly
    if not text or len(text.strip()) < 15:
        raise HTTPException(status_code=400, detail="Text is too short. Please provide a longer paragraph or essay.")

    try:
        # 1. Basic Text Processing
        # Extract all words (ignoring punctuation)
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        # Split into sentences based on punctuation
        sentences = re.split(r'[.!?]+', text)
        # Remove empty strings from the sentences list
        sentences = [s for s in sentences if len(s.strip()) > 0]
        
        word_count = len(words)
        sentence_count = len(sentences)
        avg_words_per_sentence = word_count / sentence_count if sentence_count > 0 else 0

        # 2. Advanced Vocabulary Extraction
        # For this MVP, we consider words with 8 or more letters as potential academic/advanced vocabulary
        advanced_words_set = set(word for word in words if len(word) >= 8)
        advanced_words_list = list(advanced_words_set)
        
        # 3. Academic Scoring Logic
        # A simple algorithm to estimate the English proficiency level based on sentence complexity and vocabulary
        score_estimate = "B1 (Intermediate)"
        ielts_band_estimate = "5.0 - 5.5"
        
        if avg_words_per_sentence >= 14 and len(advanced_words_list) > (word_count * 0.1):
            score_estimate = "C1/C2 (Advanced/Proficient)"
            ielts_band_estimate = "7.5+"
        elif avg_words_per_sentence >= 10 and len(advanced_words_list) > (word_count * 0.05):
            score_estimate = "B2 (Upper Intermediate)"
            ielts_band_estimate = "6.0 - 7.0"

        # Return the structured JSON response
        return {
            "status": "success",
            "metrics": {
                "total_words": word_count,
                "total_sentences": sentence_count,
                "average_words_per_sentence": round(avg_words_per_sentence, 2),
            },
            "analysis": {
                "estimated_cefr_level": score_estimate,
                "estimated_ielts_band": ielts_band_estimate,
                "advanced_vocabulary_count": len(advanced_words_list),
                "advanced_vocabulary_extracted": advanced_words_list[:10] # Return up to 10 advanced words
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred during analysis: {str(e)}")