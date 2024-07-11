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


Internal_LLM_role_instructions = """
Your name is bongapal, you are an internal customer service agent for Bonga.
You work in the tech department and your job is to help businesses use the capabilities of AI and LLM's to automate their customer service.
You are responsible for handling any technical issues or inquiries from customers. 
You are also responsible to handle any customer enquiries relating to business and operations at Bonga LTD
Bonga is based in East Africa with HQ in dar es salaam.
Bonga focuses on local languages to simplify customer service using AI

Dont talk too much. 
If the question is irrevant, remind the user that the question is irrelevant and steer them to the main focus of your purpose or the business' purpose
If a customer asks you a question in mixed languages, eg in swahili or mixes swahili and english, you can also mix swahili and english in your response. Just stay short, concise and proffesional friendly. 
"""



Customer_LLM_role_instructions = """
Your name is EcoPal, you are a customer service agent for Ecobank.
You provide 24/7 online customer service to customers of Ecobank.
Your job is to assist customers with any inquiries or issues they may have regarding their bank accounts or transactions. 
You are also responsible for promoting and educating customers on the various digital banking services offered by Ecobank.
Ecobank is a Pan-African bank with operations in 36 countries across the continent, more than any other bank in the world. 
Ecobank is a full-service bank providing wholesale, retail, investment and transaction banking services and products to governments, financial institutions, multinationals,
international organizations, medium small and micro businesses.
You are responsible for answering any questions or concerns that customers may have about their bank accounts, 
transactions, or other banking services. You should always maintain a professional and helpful tone,
and provide accurate information to the

Dont talk too much. 
If the question is irrevant, remind the user that the question is irrelevant and steer them to the main focus of your purpose or the business' purpose
If a customer asks you a question in mixed languages, eg in swahili or mixes swahili and english, you can also mix swahili and english in your response. Just stay short, concise and proffesional friendly. 
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


# Set up and Initialize the model for google/gemini-pro
model = genai.GenerativeModel('gemini-pro') 
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)


# def bot_respond(input_text, sender_id, recipient_id, instructions):
#     try:
#         # response_text = openai_bot_process(input_text, sender_id, recipient_id)
#         response_text = google_bot_process(input_text, sender_id, recipient_id, instructions)
#         return response_text
#     except Exception as e:
#         error_message = f"Error generating bot response: {e}"
#         print(error_message)
#         return f"Oops! I hit a snag. Can you try saying that again? ({error_message})"

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

# def google_bot_process(input_text, sender_id, recipient_id, instructions):
#     user_input = input_text
#     chat_history_key = f'chat_history_{sender_id}_{recipient_id}'
#     chat_history = cache.get(chat_history_key, [])
    
#     if len(chat_history) > 10:
#         chat_history = chat_history[-10:]
    
#     try:
#         chat_history.append(f"User: {user_input}")
        
#         conversation = f"{instructions}\n\n{''.join(chat_history)}\nAssistant:"
        
#         response = model.generate_content(conversation)
        
#         assistant_response = response.text
#         chat_history.append(f"Assistant: {assistant_response}")
        
#         cache.set(chat_history_key, chat_history, timeout=3600)
        
#         return assistant_response
#     except Exception as e:
#         print(f"Error in google_bot_process: {str(e)}")
#         return f"Oops! I hit a snag. Can you try saying that again? Error: {str(e)}"


def bot_respond_for_us(input_text, sender_id, recipient_id):
    try:
        # response_text = openai_bot_process(input_text, sender_id, recipient_id)
        response_text = google_bot_process_for_us(input_text, sender_id, recipient_id)
        return response_text
    except Exception as e:
        error_message = f"Error generating bot response: {e}"
        print(error_message)
        return f"Oops! I hit a snag. Can you try saying that again? ({error_message})"
    
def bot_respond_for_demo(input_text, sender_id, recipient_id):
    try:
        # response_text = openai_bot_process(input_text, sender_id, recipient_id)
        response_text = google_bot_process_for_demo(input_text, sender_id, recipient_id)
        return response_text
    except Exception as e:
        error_message = f"Error generating bot response: {e}"
        print(error_message)
        return f"Oops! I hit a snag. Can you try saying that again? ({error_message})"


def google_bot_process_for_us(input_text, sender_id, recipient_id):
    user_input = input_text
    chat_history_key = f'us_chat_history_{sender_id}_{recipient_id}'  # Added 'us_' prefix
    chat_history = cache.get(chat_history_key, [])
    
    if len(chat_history) > 10:
        chat_history = chat_history[-10:]
    
    try:
        chat_history.append(f"User: {user_input}")
        
        conversation = f"{Internal_LLM_role_instructions}\n\n{''.join(chat_history)}\nAssistant:"
        
        response = model.generate_content(conversation)
        
        assistant_response = response.text
        chat_history.append(f"Assistant: {assistant_response}")
        
        cache.set(chat_history_key, chat_history, timeout=3600)
        
        return assistant_response
    except Exception as e:
        print(f"Error in google_bot_process_for_us: {str(e)}")
        return f"Oops! I hit a snag. Can you try saying that again? Error: {str(e)}"


def google_bot_process_for_demo(input_text, sender_id, recipient_id):
    user_input = input_text
    chat_history_key = f'demo_chat_history_{sender_id}_{recipient_id}'  # Added 'demo_' prefix
    chat_history = cache.get(chat_history_key, [])
    
    if len(chat_history) > 10:
        chat_history = chat_history[-10:]
    
    try:
        chat_history.append(f"User: {user_input}")
        
        conversation = f"{Customer_LLM_role_instructions}\n\n{''.join(chat_history)}\nAssistant:"
        
        response = model.generate_content(conversation)
        
        assistant_response = response.text
        chat_history.append(f"Assistant: {assistant_response}")
        
        cache.set(chat_history_key, chat_history, timeout=3600)
        
        return assistant_response
    except Exception as e:
        print(f"Error in google_bot_process_for_demo: {str(e)}")
        return f"Oops! I hit a snag. Can you try saying that again? Error: {str(e)}"