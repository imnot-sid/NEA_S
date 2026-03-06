from tkinter import *
from tkinter import font
from dark_mode import THEMES
import cv2
from PIL import Image, ImageTk
import json

# Global variables to track theme, settings, history and information windows, and accuracy toggle
dark_mode_enabled = False
settings_window = None
history_window = None
info_window = None
accuracy = False
main_window = None


def get_theme(): #function to get the current theme
  global dark_mode_enabled
  return THEMES['dark'] if dark_mode_enabled else THEMES ['light']

def toggle_accuracy(): #function to toggle accuracy
    global accuracy
    accuracy = not accuracy

def apply_theme(): #function to apply theme
    theme = get_theme()
    # Apply the theme to the main window and any open sub-windows
    main_window.configure(bg = theme['bg'])
    widget_theme(main_window,theme)
      
    if settings_window is not None and settings_window.winfo_exists():
        settings_window.configure(bg=theme["bg"])
        widget_theme(settings_window,theme)
    
    if history_window is not None and history_window.winfo_exists():
        history_window.configure(bg=theme["bg"])
        widget_theme(history_window,theme)
    
    if info_window is not None and info_window.winfo_exists():
        info_window.configure(bg=theme["bg"])
        widget_theme(info_window,theme)

# Functipon to apply the theme to all widgets in a given window
def widget_theme(window,theme):
  for widget in window.winfo_children():
    widget_type = widget.winfo_class()
      
    if widget_type == 'Label':
      widget.configure(bg = theme['bg'], fg=theme['fg'])
    elif widget_type == 'Scale':
      widget.configure(bg = theme['scale_bg'], fg=theme['scale_fg'])

def toggle_theme(): #function to toggle between light and dark mode
  global dark_mode_enabled
  if dark_mode_enabled == False:
    dark_mode_enabled = True
    apply_theme()
  else:
    dark_mode_enabled = False
    apply_theme()

def change_font_size(value): #function for changing font size
    app_font.configure(size=int(value))

def back_info(): #function for going back from information to main window
    info_window.destroy()
    main_window.deiconify()

def back_settings(): #function for going back from settings to main window
    settings_window.destroy()
    main_window.deiconify()

def back_history(): #function for going back from history to main window
    history_window.destroy()
    main_window.deiconify()

def create_information_window(response): #function for creating information window
    global info_window
    info_window = Toplevel(main_window)
    info_window.geometry("400x600")
    info_window.title("Information")
    main_window.withdraw()


    theme = get_theme()
    info_window.configure(bg=theme['bg'])

    Button(info_window, text="Back", font=app_font, command=back_info).pack(pady=10)
    # Create a text widget to display the response with word wrapping
    # As otherwise it would be one long line that goes off the screen
    text_widget = Text(info_window, wrap=WORD, bg=theme['bg'], fg=theme['fg'])
    text_widget.insert(END, response)
    text_widget.pack(fill=BOTH, expand=True)

def create_history_window(username):
    username=username
    global history_window
    history_window = Toplevel(main_window)
    history_window.geometry("400x600")
    main_window.withdraw()

    theme = get_theme()
    history_window.configure(bg=theme['bg'])

    Button(history_window, text="Back", font=app_font, command=back_history).pack(pady=10)

    title_label = Label(history_window, text="Analysis History", font=app_font)
    title_label.pack(pady=10)

    # Create a scrollable area for history logs
    container = Frame(history_window, bg=theme['bg'])
    container.pack(fill=BOTH, expand=True)

    canvas = Canvas(container, bg=theme['bg'], highlightthickness=0)
    scrollbar = Scrollbar(container, orient="vertical", command=canvas.yview)
    scrollable_frame = Frame(canvas, bg=theme['bg'])

    # Update the scroll region of the canvas whenever the size of the scrollable frame changes
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    try:
        with open('History_logs.json', 'r') as f:
            data = json.load(f)
        users = data.get('users', [])
        # Find the logged-in user and get their history data
        history_data = []
        for user in users:
            if isinstance(user, dict) and str(user.get('username')) == username:
                history_data = user.get("history", [])
                break
            
        for entry in reversed(history_data):
            disease = entry.get("disease", "Unknown")
            timestamp = entry.get("timestamp", "")[:16].replace("T", " ")
            response = entry.get("response", "")
            confidence = entry.get("confidence_score", 0)
            
            entry_frame = Frame(scrollable_frame, bg=theme['button_bg'], pady=5, padx=5, highlightbackground=theme['fg'], highlightthickness=1)
            entry_frame.pack(fill=X, pady=5, padx=10)
            
            # Display the hisotry entry details in the entry frame
            Label(entry_frame, text=f"Timestamp: {timestamp}", font=(app_font.actual("family"), 10), bg=theme['button_bg'], fg=theme['button_fg']).pack(anchor=W)
            Label(entry_frame, text=f"Disease: {disease}", font=(app_font.actual("family"), 12, "bold"), bg=theme['button_bg'], fg=theme['button_fg']).pack(anchor=W)
            Label(entry_frame, text=f"Confidence: {confidence:.2%}", font=(app_font.actual("family"), 10), bg=theme['button_bg'], fg=theme['button_fg']).pack(anchor=W)
            Label(entry_frame, text=f"Response: {response}", font=(app_font.actual("family"), 10), bg=theme['button_bg'], fg=theme['button_fg'], wraplength=350, justify=LEFT).pack(anchor=W, pady=5)


    except (FileNotFoundError, json.JSONDecodeError):
        Label(scrollable_frame, text="No history found.", font=app_font, bg=theme['bg'], fg=theme['fg']).pack(pady=20)

def change_font_size(value): #function for changing font size
    app_font.configure(size=int(value))

def back_settings(): #function for going back from settings to main window
    settings_window.destroy()
    main_window.deiconify()

def create_settings_window():
    global settings_window
    # Create the settings window and hide the main window
    settings_window = Toplevel(main_window)
    settings_window.geometry("300x500")
    main_window.withdraw()

    # Create a slider for font size adjustment
    label = Label(settings_window, text="Font size:", font=app_font)
    label.pack()

    slider = Scale(settings_window, from_=10, to=30,
                   orient=HORIZONTAL, command=change_font_size)
    slider.set(app_font['size'])
    slider.pack()
    # create the back button
    back_button = Button(settings_window, text="Back", font=app_font, command=back_settings)
    back_button.pack()
    # create the theme toggle button
    theme_button = Button(settings_window, text = "Toggle Dark mode", font=app_font, command=toggle_theme)
    theme_button.pack()
    # create the accuracy toggle button
    accuracy_button = Button(settings_window, text = "Toggle Accuracy", font=app_font, command=toggle_accuracy)
    accuracy_button.pack()
    apply_theme()  # Apply the initial theme to the settings window

def main(username):
    username=username
    global main_window, app_font, index
    # Create the main window
    main_window = Tk()
    main_window.geometry("300x500")

    # Set the application font
    app_font = font.Font(size=20)
    # Create the settings button
    settings_button = Button(main_window, text="Settings",
                             font=app_font, command=create_settings_window)
    settings_button.pack()

    # Create the list of messages to rotate through
    messages = ["Check the soil before you pour", "Lift the pot",
                 "Water in the morning", "Bottom watering trick",
                 "Don't let them sit in water", "Indicator Plant method",
                 "Water the soil, not the leaves", "Match light to the plant",
                 "Rotate for even growth", "Clean the leaves",
                 "Move away from drafts", "Bright, indirect light is key",
                 "Prune for health", "Check for pests",
                 "Boost humidity", "Fertilize wisely", "Repot when necessary",
                 "Use the right soil mix", "Patience is a virtue",
                 "Plant care is self-care", "Enjoy the process"]
    
    label = Label(main_window, text="", font=app_font)
    label.pack()

    # Create a canvas to display the webcam feed
    canvas = Canvas(main_window, width=280, height=280,)
    canvas.pack()
    # Set up the webcam feed and update the canvas with the video stream
    def update_frame():
      ret, frame = cap.read()
      frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
      image = Image.fromarray(frame)
      photo = ImageTk.PhotoImage(image=image)
      canvas.create_image(140, 140, image=photo, anchor=CENTER)
      canvas.image = photo
      main_window.after(50, update_frame)
    # Initialize the webcam feed
    cap = cv2.VideoCapture(0)
    update_frame()
    # Set the resolution of the webcam feed
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 280)


    index = 0
    def rotate_messages():
        global index
        label.config(text=messages[index])
        index = (index + 1) % len(messages)
        main_window.after(3000, rotate_messages)

    def run_analysis():
        #if we import main_backend at the top, it will run the model as soon as we import it, which is not what we want
        # We only want to run the model when the user clicks the analyse button so we import it here instead
        import main_backend
        # Capture a single frame for analysis
        ret, frame = cap.read()
        if ret:
            cv2.imwrite("temp_capture.jpg", frame)
            # Pass the path of the captured image to the backend
            full_response = main_backend.run_model("temp_capture.jpg", accuracy, username)
            create_information_window(full_response)

       
    # Create the analyse button
    analyse_button = Button(main_window, text="Analyse",
                             font=app_font, command=run_analysis)
    analyse_button.pack()
    # Create the history button
    History_button = Button(main_window, text="History",
                             font=app_font, command=lambda: create_history_window(username))
    History_button.pack()

    rotate_messages()

    apply_theme()  # Apply the initial theme to the main window
    main_window.mainloop()

def login():
    # Create the login window
    login_window = Tk()
    login_window.geometry("300x200")
    login_window.title("Login")
    # Create the login form
    label = Label(login_window, text="Enter your username:")
    label.pack(pady=10)
    username_entry = Entry(login_window)
    username_entry.pack()

    label = Label(login_window, text="Enter your password:")
    label.pack(pady=10)
    password_entry = Entry(login_window, show="*")
    password_entry.pack()

    def attempt_login():
        # Get the entered username and password
        username = username_entry.get()
        password = password_entry.get()
        # Check if the username and password are valid
        with open('users.json', 'r') as f:
            users = json.load(f)
        
        for user in users:
            if str(user['username']) == username and user['password'] == password:
                login_window.destroy()
                main(username)
                return
        
        error_label.config(text="Invalid username or password. Please try again.")

    error_label = Label(login_window, text="", fg="red")
    error_label.pack()
    login_button = Button(login_window, text="Login", command=attempt_login)
    login_button.pack(pady=10)

    while not main_window:
        login_window.update()
    
if __name__ == "__main__":
    login()