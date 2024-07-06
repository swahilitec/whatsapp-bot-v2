# chatbot/utils.py


# chatbot/utils.py
import os
import openai
import requests
from django.core.cache import cache
from django.http import JsonResponse, HttpResponse
from dotenv import load_dotenv
import google.generativeai as genai
from django.core.cache import cache


# Load environment variables
load_dotenv()
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
VERSION = os.getenv("VERSION")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")


# Instantiate OpenAI client
openai.api_key = OPENAI_API_KEY
client = openai.OpenAI()


LLM_model = "gpt-4"


LLM_role_instructions = """
You are Lil Trey, a fun and engaging chatbot. Keep your responses conversational, 
as if you're texting a friend. Use casual language, throw in some jokes or puns when appropriate, 
and don't be afraid to use emojis 😊. Remember past context and refer back to it naturally. 
Ask questions to keep the conversation going. If the user seems down, try to cheer them up!
"""


def is_valid_message(message):
    text_content = message.get('text', {}).get('body', '').lower()
    if len(text_content.split()) < 1:
        return False
    return True


def send_whatsapp_message(data):
    recipient = data.get("recipient")
    text_content = data.get("text_content")
    
    if not recipient or not text_content:
        return JsonResponse({"status": "failure", "message": "Recipient and text content are required."}, status=400)

    sending_data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": recipient,
        "type": "text",
        "text": {"preview_url": False, "body": text_content},
    }
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {ACCESS_TOKEN}",
    }
    url = f"https://graph.facebook.com/{VERSION}/{PHONE_NUMBER_ID}/messages"
    
    # Pass a dictionary to is_valid_message
    message_data = {
        "text": {"body": text_content}
    }
    if is_valid_message(message_data):
        response = requests.post(url, json=sending_data, headers=headers)
        if response.status_code != 200:
            print("\n WhatsApp failed to send message! \n")
            return JsonResponse({"status": "failure", "message": "WhatsApp failed to send message!"}, status=response.status_code)
        return JsonResponse({"status": "success", "message": "Message sent successfully."})
    else:
        return JsonResponse({"status": "failure", "message": "Invalid message."}, status=400)


def verify_webhook_token(request):
    if request.method == 'GET':
        mode = request.GET.get('hub.mode')
        token = request.GET.get('hub.verify_token')
        challenge = request.GET.get('hub.challenge')
        if mode == 'subscribe' and token == VERIFY_TOKEN:
            return HttpResponse(challenge, content_type='text/plain')
        else:
            return HttpResponse('Verification token mismatch', status=403)
    return HttpResponse('Method not allowed', status=405)


def bot_respond(input_text, sender_id, recipient_id):
    try:
        # response_text = openai_bot_process(input_text, sender_id, recipient_id)
        response_text = google_bot_process(input_text, sender_id, recipient_id)
        return response_text
    except Exception as e:
        error_message = f"Error generating bot response: {e}"
        print(error_message)
        return f"Oops! I hit a snag. Can you try saying that again? ({error_message})"


# def openai_bot_process(input_text, sender_id, recipient_id):
#     user_input = input_text
#     chat_history_key = f'chat_history_{sender_id}_{recipient_id}'
#     chat_history = cache.get(chat_history_key, [])
    
#     # Limit chat history to last 10 messages to maintain context without overloading
#     if len(chat_history) > 10:
#         chat_history = chat_history[-10:]
    
#     try:
#         chat_history.append({"role": "user", "content": user_input})
        
#         system_message = {
#             "role": "system", 
#             "content": LLM_role_instructions
#         }
        
#         response = client.chat.completions.create(
#             model=LLM_model,
#             messages=[system_message] + chat_history,
#             max_tokens=150,  # Adjusted for shorter, more conversational responses
#             temperature=0.7  # Slightly increased for more variety in responses
#         )
        
#         assistant_response = response.choices[0].message.content
#         chat_history.append({"role": "assistant", "content": assistant_response})
        
#         # Save updated chat history
#         cache.set(chat_history_key, chat_history, timeout=3600)  # Cache for 1 hour
        
#         return assistant_response
#     except Exception as e:
#         return f"Oops! I hit a snag. Can you try saying that again? 😅"
    




# 

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)


# Initialize the model
model = genai.GenerativeModel('gemini-pro')  # Changed to 'gemini-pro' for testing

LLM_role_instructions = """
You are Lil Trey, a fun and engaging chatbot. Keep your responses conversational, 
as if you're texting a friend. Use casual language, throw in some jokes or puns when appropriate, 
and don't be afraid to use emojis 😊. Remember past context and refer back to it naturally. 
Ask questions to keep the conversation going. If the user seems down, try to cheer them up!
"""

def google_bot_process(input_text, sender_id, recipient_id):
    user_input = input_text
    chat_history_key = f'chat_history_{sender_id}_{recipient_id}'
    chat_history = cache.get(chat_history_key, [])
    
    if len(chat_history) > 10:
        chat_history = chat_history[-10:]
    
    try:
        chat_history.append(f"User: {user_input}")
        
        conversation = f"{LLM_role_instructions}\n\n{''.join(chat_history)}\nAssistant:"
        
        response = model.generate_content(conversation)
        
        assistant_response = response.text
        chat_history.append(f"Assistant: {assistant_response}")
        
        cache.set(chat_history_key, chat_history, timeout=3600)
        
        return assistant_response
    except Exception as e:
        print(f"Error in google_bot_process: {str(e)}")
        return f"Oops! I hit a snag. Can you try saying that again? Error: {str(e)}"