import africastalking

AT_USERNAME = "sandbox"
AT_API_KEY = 'atsk_3f85bedc51e302fc03029fb187f9c8e10b0ca0588b6c4da3e7880b0b8f8b1e5c0bc8c13c'
africastalking.initialize(AT_USERNAME, AT_API_KEY)
sms = africastalking.SMS


def send_sms(to, message):
    """
    Sends SMS to the given phone number(s).
    `to` can be a string or a list of numbers (e.g., ["+2547XXXXXXX"])
    """
    try:
        response = sms.send(message, [to])  # or pass list
        return response
    except Exception as e:
        print(f"Error sending SMS: {e}")
        return None
