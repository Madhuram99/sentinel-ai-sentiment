from django.conf import settings
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
import json

class ChatService:
    def __init__(self):
        self.analyzer = SentimentIntensityAnalyzer()
        self.llm = ChatGroq(
            temperature=0.3, 
            model_name="llama-3.1-8b-instant", 
            api_key=settings.GROQ_API_KEY
        )

    def analyze_sentiment(self, text):
        scores = self.analyzer.polarity_scores(text)
        compound = scores['compound']
        if compound >= 0.05: return "Positive", compound
        elif compound <= -0.05: return "Negative", compound
        return "Neutral", compound

    def get_ai_response(self, user_text, sentiment, conversation_obj):
        # Fetch last 3 messages from DB for context
        history_msgs = conversation_obj.messages.order_by('-timestamp')[:3][::-1]
        
        # Build Prompt
        messages = [SystemMessage(content=f"""
            User Sentiment: {sentiment}. Return JSON ONLY.
            Format: {{"response": "text", "suggestions": ["opt1", "opt2"]}}
        """)]
        
        for msg in history_msgs:
            if msg.sender == 'user': messages.append(HumanMessage(content=msg.text))
            else: messages.append(AIMessage(content=msg.text))
            
        messages.append(HumanMessage(content=user_text))

        # Call AI
        try:
            raw = self.llm.invoke(messages).content
            clean = raw.replace('```json', '').replace('```', '').strip()
            return json.loads(clean)
        except:
            return {
                "response": "Connection error.", 
                "suggestions": ["Retry"]
            }