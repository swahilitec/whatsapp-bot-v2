# chatbot/views.py

from .utils import *
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework import viewsets
import requests, json

class WhatsAppViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    @csrf_exempt
    @action(detail=False, methods=['post'])
    def send_message(self, request):
        data = request.data
        print(f'\nReceived data (in the WhatsAppViewSet\'s send_message action ): {data}\n')  # Print the received data for debugging
        try:
            response = send_whatsapp_message(data)
            if isinstance(response, JsonResponse):
                return response
            response.raise_for_status()  # Raise an exception for HTTP error responses
            return Response({"status": "success", "message": "Message sent successfully."})
        except requests.exceptions.HTTPError as http_err:
            return Response({"status": "failure", "message": f"HTTP error occurred: {http_err}"}, status=response.status_code)
        except requests.exceptions.RequestException as req_err:
            return Response({"status": "failure", "message": f"Error occurred: {req_err}"}, status=500)
        except Exception as err:
            return Response({"status": "failure", "message": f"An unexpected error occurred: {err}"}, status=500)
    
    @csrf_exempt
    @action(detail=False, methods=['post'])
    def chat_with_bot(self, request):
        input_text = request.data.get('input_text')
        print(f'\nInput text for bot: {input_text}\n')  # Print the input text for debugging
        response_text = bot_respond(input_text, '255755888555', '255755888555')
        return Response({"response": response_text})
    

@csrf_exempt
def webhook(request):
    print('', 'webhook triggered', '\n')
    if request.method == 'GET':
        return verify_webhook_token(request)
    
    elif request.method == 'POST':
        data = json.loads(request.body)
        if 'object' in data and 'entry' in data:
            if data['object'] == 'whatsapp_business_account':
                try:
                    for entry in data['entry']:
                        changes = entry.get('changes', [])
                        for change in changes:
                            value = change.get('value', {})
                            metadata = value.get('metadata', {})
                            phoneNumber = metadata.get('display_phone_number')
                            phoneId = metadata.get('phone_number_id')
                            
                            contacts = value.get('contacts', [])
                            messages = value.get('messages', [])
                            statuses = value.get('statuses', [])

                            if contacts and messages:
                                if is_valid_message(messages[0]):
                                    profileName = contacts[0].get('profile', {}).get('name')
                                    whatsappId = contacts[0].get('wa_id')
                                    fromId = messages[0].get('from')
                                    messageId = messages[0].get('id')
                                    timestamp = messages[0].get('timestamp')
                                    textContent = messages[0].get('text', {}).get('body', '')

                                    # bot_response = openai_bot_process(textContent, phoneNumber, whatsappId)
                                    bot_response = google_bot_process(textContent, phoneNumber, whatsappId)
                                    


                                    sendingData = {
                                        "recipient": fromId,
                                        "text_content": bot_response
                                    }
                                    send_whatsapp_message(sendingData)
                            
                                    return JsonResponse({'success': True}, status=200)

                            if statuses:
                                for status in statuses:
                                    recipientId = status.get('recipient_id')
                                    messageId = status.get('id')
                                    messageStatus = status.get('status')
                                    timestamp = status.get('timestamp')
                                return JsonResponse({'status_received': True}, status=200)

                except Exception as e:
                    error_message = f"Error: {str(e)}"
                    print(error_message)
                    return JsonResponse({'failed': True}, status=500)

        return JsonResponse({'invalid_data': True}, status=400)

    return JsonResponse
