from transformers import AutoTokenizer, AutoModel, AutoModelForSequenceClassification, AutoModelForSeq2SeqLM
import torch
from typing import List

from app.config import settings

class NLPTasks:
    semantic_model_name = "sentence-transformers/all-MiniLM-L6-v2"
    semantic_tokenizer = AutoTokenizer.from_pretrained(semantic_model_name)
    semantic_model = AutoModel.from_pretrained(semantic_model_name)

    sentiment_model_name = "ProsusAI/finbert"
    sentiment_tokenizer = AutoTokenizer.from_pretrained(sentiment_model_name)
    sentiment_model = AutoModelForSequenceClassification.from_pretrained(sentiment_model_name)
    
    # BART-large for keyword generation (without pipeline)
    keyword_model_name = "facebook/bart-large"
    keyword_tokenizer = AutoTokenizer.from_pretrained(keyword_model_name)
    keyword_model = AutoModelForSeq2SeqLM.from_pretrained(keyword_model_name)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    semantic_model.to(device)
    sentiment_model.to(device)
    keyword_model.to(device)

    @staticmethod
    def generate_semantic_embedding(text: str) -> List[float]:
        inputs = NLPTasks.semantic_tokenizer(text, return_tensors="pt", truncation=True, padding=True)
        inputs = {k: v.to(NLPTasks.device) for k, v in inputs.items()}
        with torch.no_grad():
            outputs = NLPTasks.semantic_model(**inputs)
        embedding = outputs.last_hidden_state.mean(dim=1).squeeze().tolist()
        return embedding

    @staticmethod
    def summarize_into_keywords(content: str, top_n=5) -> List[str]:
        inputs = NLPTasks.keyword_tokenizer(
            content,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=512
        )
        inputs = {k: v.to(NLPTasks.device) for k, v in inputs.items()}

        with torch.no_grad():
            summary_ids = NLPTasks.keyword_model.generate(
                **inputs,
                max_length=30,
                min_length=10,
                num_return_sequences=2,
                do_sample=True
            )

        outputs = NLPTasks.keyword_tokenizer.batch_decode(summary_ids, skip_special_tokens=True)
        
        keywords = []
        for generated_text in outputs:
            generated_text = generated_text.strip()
            for delimiter in [',', ';', '-', '•']:
                if delimiter in generated_text:
                    keywords.extend([k.strip() for k in generated_text.split(delimiter) if k.strip()])
                    break
            if not keywords:
                words = generated_text.split()
                if len(words) <= 3:
                    keywords.append(generated_text)
                else:
                    from nltk.util import ngrams
                    phrases = list(ngrams(words, 2))
                    keywords.extend([' '.join(phrase) for phrase in phrases])

        unique_keywords = []
        for kw in keywords:
            if kw not in unique_keywords:
                unique_keywords.append(kw)
                if len(unique_keywords) >= top_n:
                    break
        return unique_keywords[:top_n]

    @staticmethod
    def analyze_sentiment(content: str) -> dict:
        inputs = NLPTasks.sentiment_tokenizer(content, return_tensors="pt", truncation=True, padding=True)
        inputs = {k: v.to(NLPTasks.device) for k, v in inputs.items()}
        with torch.no_grad():
            outputs = NLPTasks.sentiment_model(**inputs)
        probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
        labels = ["negative", "neutral", "positive"]
        scores = {label: float(probs[0][i]) for i, label in enumerate(labels)}
        return scores

    @staticmethod
    def classify_sentiment(scores: dict) -> str:
        return max(scores, key=scores.get)
