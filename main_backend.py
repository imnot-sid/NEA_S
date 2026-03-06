import json
from datetime import datetime
from google import genai
from ultralytics import YOLO

model = YOLO('best.pt')

def run_model(image_source, accuracy, username):
    username=username
    accuracy = accuracy
    # Check if the model was loaded successfully before attempting to run predictions
    if model is None:
        return "Error: Model failed to load."
    
    full_response = ""
    last_disease_found = None
    confidence_score = 0.0

    results = model.predict(source=image_source, show=False, conf=0.65,)

    for r in results:
        # when there are no detections in a frame just continue streaming
        if len(r.boxes) == 0:
            continue

        for box in r.boxes:
            class_id = int(box.cls[0]) # Get the class ID of the detected object
            confidence_score = float(box.conf[0]) # Get the confidence score
            disease_name = model.names[class_id] # Get the disease name using the class ID
            last_disease_found = disease_name # Update the last detected disease
            break
        break
        
    # if no disease was detected, set the full response to indicate that no disease was found
    if last_disease_found is None:
        full_response = "No disease found in the image."
        # Save the response to history even if no disease was found
        save_history(last_disease_found, full_response, confidence_score=0.0, accuracy=accuracy, username=username)
        return full_response

    # Generate informative text using GenAI
    client = genai.Client(api_key='AIzaSyAGecHsgmbKh6SeA-c9fqeVhiQWAtsbXwo')

    # Generate information about the detected disease
    response_info = client.models.generate_content_stream(
        model="gemini-2.5-flash",
        contents=f"Tell me information about this plant disease: {last_disease_found}",
    )

    # lets the full response be printed as it is generated
    for stream in response_info:
        full_response += stream.text

    # Generate a cure for the detected disease
    response_cure = client.models.generate_content_stream(
        model="gemini-2.5-flash",
        contents=f"Tell me about a cost-effective cure for this plant disease: {last_disease_found}"
    )

    for stream in response_cure:
        full_response += stream.text


    # Response, detected disease and timestamp are saved to history_logs
    save_history(last_disease_found, full_response, confidence_score, accuracy=accuracy, username=username)

    return full_response

def save_history(disease, response_text, confidence_score, accuracy, username):
    # Response, disease and timestamp are saved to history_logs
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "disease": disease,
        "response": response_text,
    }

    # If accuracy is enabled, also save the confidence score to the log entry
    if accuracy:
        log_entry["confidence_score"] = confidence_score

    # Load existing user data
    try:
        with open('History_logs.json', 'r') as f:
            data = json.load(f)
            users = data.get('users', [])
    except (FileNotFoundError, json.JSONDecodeError):
        print("Error: History_logs.json not found or is invalid.")
        return

    # Find the logged-in user and append the log entry to their history
    user_found = False
    for user in users:
        # Ensure each entry is a dict before indexing
        if isinstance(user, dict) and str(user.get('username')) == username:
            if "history" not in user:
                user["history"] = []
            user["history"].append(log_entry)
            user_found = True
            break

    if user_found:
        # Save the updated users list back to the JSON file
        with open('History_logs.json', 'w') as f:
            json.dump({"users": users}, f, indent=2)
        print(f"Response saved to history for user: {username}")
    else:
        print(f"User {username} not found. History not saved.")
