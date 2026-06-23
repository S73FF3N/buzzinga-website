import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

@csrf_exempt
@require_POST
def telegram_webhook(request):
    data = json.loads(request.body)
    if 'message' in data:
        chat_id = data['message']['chat']['id']
        text    = data['message'].get('text', '')
        _send(chat_id, f'✅ Bot läuft! Deine Nachricht: {text}')
    return JsonResponse({'ok': True})

def _send(chat_id, text, reply_markup=None):
    import requests, os
    payload = {'chat_id': chat_id, 'text': text}
    if reply_markup:
        payload['reply_markup'] = json.dumps(reply_markup)
    requests.post(
        f"https://api.telegram.org/bot{os.environ['TELEGRAM_TOKEN']}/sendMessage",
        json=payload
    )