import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
import smtplib

app = Flask(__name__)
CORS(app)

DB_FILE = 'data/database.json' 

load_dotenv() 

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")

def save_to_json_db(new_entry):
    dir_name = os.path.dirname(DB_FILE)
    if dir_name and not os.path.exists(dir_name):
        os.makedirs(dir_name, exist_ok=True)

    if not os.path.exists(DB_FILE) or os.stat(DB_FILE).st_size == 0:
        data_list = []
    else:
        with open(DB_FILE, 'r') as f:
            try:
                data_list = json.load(f)
            except json.JSONDecodeError:
                data_list = []

    data_list.append(new_entry)

    with open(DB_FILE, 'w') as f:
        json.dump(data_list, f, indent=4)

def send_email_notification(ticket_data):
    """Sends a formatted, professional HTML email containing ticket metrics and AI analysis."""
    msg = MIMEMultipart('alternative')
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL
    
    priority = ticket_data['ai_analysis']['priority']
    category = ticket_data['ai_analysis']['category']
    msg['Subject'] = f"[{priority.upper()}] New Support Ticket: {category}"

    # Determine priority badge color dynamically
    badge_color = "#6c757d"  
    if priority.lower() == "urgent":
        badge_color = "#dc3545"  
    elif priority.lower() == "high":
        badge_color = "#fd7e14"  
    elif priority.lower() == "medium":
        badge_color = "#0d6efd"  
    elif priority.lower() == "low":
        badge_color = "#198754"  

    # FIX: Process the line breaks HERE instead of inside the HTML template block
    formatted_reply = ticket_data['ai_analysis']['suggested_reply'].replace('\n', '<br>')

    # Professional HTML Email Body Template
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f6f9; color: #333333; margin: 0; padding: 0; }}
            .container {{ max-width: 600px; margin: 20px auto; background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 10px rgba(0,0,0,0.05); border: 1px solid #e1e4e8; }}
            .header {{ background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); color: #ffffff; padding: 25px; text-align: center; }}
            .header h1 {{ margin: 0; font-size: 22px; font-weight: 600; letter-spacing: 0.5px; }}
            .content {{ padding: 30px; }}
            .badge {{ display: inline-block; padding: 6px 14px; font-size: 12px; font-weight: bold; color: white; border-radius: 20px; text-transform: uppercase; margin-bottom: 20px; }}
            .section-title {{ font-size: 14px; font-weight: 700; color: #4a5568; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px; border-bottom: 2px solid #edf2f7; padding-bottom: 5px; }}
            .meta-table {{ width: 100%; margin-bottom: 25px; border-collapse: collapse; }}
            .meta-table td {{ padding: 8px 0; font-size: 15px; vertical-align: top; }}
            .meta-label {{ width: 30%; font-weight: 600; color: #718096; }}
            .meta-value {{ color: #1a202c; }}
            .message-box {{ background-color: #f8fafc; border-left: 4px solid #4a5568; padding: 15px; font-style: italic; border-radius: 0 6px 6px 0; margin-bottom: 25px; color: #2d3748; line-height: 1.5; }}
            .ai-box {{ background-color: #f0fdf4; border: 1px solid #bbf7d0; padding: 20px; border-radius: 6px; color: #166534; line-height: 1.6; }}
            .footer {{ background-color: #f7fafc; padding: 15px; text-align: center; font-size: 12px; color: #a0aec0; border-top: 1px solid #edf2f7; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Helpdesk Triage Automation</h1>
            </div>
            <div class="content">
                <div class="badge" style="background-color: {badge_color};">{priority} Priority</div>
                
                <div class="section-title">Customer Metadata</div>
                <table class="meta-table">
                    <tr>
                        <td class="meta-label">Name:</td>
                        <td class="meta-value">{ticket_data['customer_name']}</td>
                    </tr>
                    <tr>
                        <td class="meta-label">Email:</td>
                        <td class="meta-value"><a href="mailto:{ticket_data['customer_email']}" style="color: #2a5298; text-decoration: none;">{ticket_data['customer_email']}</a></td>
                    </tr>
                    <tr>
                        <td class="meta-label">Category:</td>
                        <td class="meta-value"><strong>{category}</strong></td>
                    </tr>
                </table>

                <div class="section-title">Inbound Message</div>
                <div class="message-box">
                    "{ticket_data['customer_message']}"
                </div>

                <div class="section-title">AI Generated Draft Response</div>
                <div class="ai-box">
                    {formatted_reply}
                </div>
            </div>
            <div class="footer">
                Automated via Flask & Groq LPU Core Routing Engine
            </div>
        </div>
    </body>
    </html>
    """
    
    msg.attach(MIMEText(html_body, 'html'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls() 
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
        print("HTML Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

@app.route('/api/data', methods=['POST'])
def handle_ticket():
    data = request.get_json()
    print(f"--- DEBUG: Incoming Payload From Frontend: {data} ---")
    
    clean_data = {str(k).lower().strip(): v for k, v in data.items()}

    user_name = clean_data.get('name', clean_data.get('ime', ''))
    
    user_email = clean_data.get('email', clean_data.get('mail', '')) 
    
    user_message = clean_data.get('message', clean_data.get('poruka', ''))

    if not user_message:
        return jsonify({"status": "error", "reply": "Message content is required."}), 400

    system_prompt = """
    You are an automated customer support triaging assistant. 
    Analyze the incoming customer support ticket and return a JSON object with the following fields:
    {
        "category": "e.g., Technical Issue, Billing, Feature Request, General Inquiry",
        "priority": "e.g., Low, Medium, High, Urgent",
        "suggested_reply": "A polite, professional draft response addressing the user's issue directly."
    }
    Output ONLY valid JSON. Do not include markdown code blocks or conversational filler text.
    """

    user_prompt = f"""
    Customer Name: {user_name}
    Customer Email: {user_email}
    Message: {user_message}
    """

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        raw_content = response.choices[0].message.content
        ai_analysis = json.loads(raw_content)
        
    except Exception as e:
        print(f"Groq API Error: {e}")
        ai_analysis = {
            "category": "Unknown",
            "priority": "Medium",
            "suggested_reply": "Thank you for reaching out. We are looking into your message."
        }
    
        
    final_ticket_record = {
        "customer_name": user_name,
        "customer_email": user_email,
        "customer_message": user_message,
        "ai_analysis": ai_analysis
    }

    save_to_json_db(final_ticket_record)
    
    send_email_notification(final_ticket_record)

    return jsonify({
        "status": "success",
        "reply": "Ticket filed and internal HTML email notification dispatched!"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)