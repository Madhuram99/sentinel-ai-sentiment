from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Conversation, Message
from .services import ChatService
import time

service = ChatService()

# ... keep your imports ...

def index(request):
    chat_id = request.session.get('chat_id')
    initial_history = []
    
    # 1. Try to find the existing chat
    if chat_id:
        try:
            chat = Conversation.objects.get(id=chat_id)
            # Load past messages to send to frontend
            msgs = chat.messages.order_by('timestamp')
            for m in msgs:
                initial_history.append({
                    'sender': m.sender,
                    'text': m.text
                })
        except Conversation.DoesNotExist:
            # ID was in cookie but DB record missing (rare)
            chat = Conversation.objects.create()
            request.session['chat_id'] = chat.id
    else:
        # No cookie, start fresh
        chat = Conversation.objects.create()
        request.session['chat_id'] = chat.id

    # 2. Pass history to the template
    import json
    return render(request, 'chat.html', {
        'initial_history': json.dumps(initial_history)
    })
    
@csrf_exempt
def chat_api(request):
    if request.method == "POST":
        import json
        data = json.loads(request.body)
        user_text = data.get("message", "")
        chat_id = request.session.get('chat_id')
        
        # 1. Get Conversation
        chat = Conversation.objects.get(id=chat_id)

        # 2. Analyze Sentiment
        label, score = service.analyze_sentiment(user_text)

        # 3. Save User Message to DB
        Message.objects.create(
            conversation=chat, sender='user', 
            text=user_text, sentiment_label=label, sentiment_score=score
        )

        # 4. Get AI Response
        start = time.time()
        ai_data = service.get_ai_response(user_text, label, chat)
        latency = round(time.time() - start, 2)

        # 5. Save Bot Message to DB
        Message.objects.create(
            conversation=chat, sender='bot', 
            text=ai_data['response'], sentiment_label=label, sentiment_score=score
        )

        return JsonResponse({
            "bot_response": ai_data['response'],
            "suggestions": ai_data.get('suggestions', []),
            "sentiment": label,
            "score": score,
            "latency": latency
        })
        
@csrf_exempt
def end_chat(request):
    chat_id = request.session.get('chat_id')
    if not chat_id: return JsonResponse({"overall": "No Data"})
    
    chat = Conversation.objects.get(id=chat_id)
    msgs = chat.messages.filter(sender='user')
    
    if not msgs: return JsonResponse({"overall": "No Data"})

    avg = sum(m.sentiment_score for m in msgs) / msgs.count()
    overall = "Positive" if avg >= 0.05 else "Negative" if avg <= -0.05 else "Neutral"
    
    # Format log for PDF (using DB data)
    history_log = [
        {
            "user": m.text, 
            "sentiment": m.sentiment_label, 
            "bot_text": chat.messages.filter(id__gt=m.id, sender='bot').first().text if chat.messages.filter(id__gt=m.id, sender='bot').exists() else ""
        } 
        for m in msgs
    ]

    return JsonResponse({
        "overall": overall,
        "avg_score": round(avg, 2),
        "history_log": history_log,
        "graph_data": [m.sentiment_score for m in msgs],
        "graph_labels": [f"Msg {i+1}" for i in range(len(msgs))]
    })