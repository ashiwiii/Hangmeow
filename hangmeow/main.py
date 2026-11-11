import tkinter as tk
import random
from PIL import Image, ImageTk
import pygame


# === Initialize Window and Audio ===
root = tk.Tk()
root.title("HangMeow")
root.configure(bg="#ffe0ae")
root.resizable(False, False)  # Prevent window resizing


# Initialize pygame mixer for background music and sound effects with error handling
pygame.mixer.init()
try:
    pygame.mixer.music.load("bgmusic.mp3")
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)
except pygame.error as e:
    print(f"Warning: Could not load music - {e}. Continuing without music.")
# Load click sound for key presses
try:
    click_sound = pygame.mixer.Sound("kb.wav")
except pygame.error as e:
    print(f"Warning: Could not load click sound - {e}")
    click_sound = None
# Load win sound
try:
    win_sound = pygame.mixer.Sound("win.wav")
except pygame.error as e:
    print(f"Warning: Could not load win sound - {e}")
    win_sound = None
# Load game over sound
try:
    gameover_sound = pygame.mixer.Sound("gameover.wav")
except pygame.error as e:
    print(f"Warning: Could not load game over sound - {e}")
    gameover_sound = None
# Load sound effect for image change
try:
    meow_sound = pygame.mixer.Sound("meow.wav")
except pygame.error as e:
    print(f"warning: Could not load meow sound - {e}")
    meow_sound = None


# === Word Banks ===
easy_words = [
    {"word": "BIT", "hint": "Smallest data unit in a computer"},
    {"word": "ROM", "hint": "Non-volatile memory"},
    {"word": "RAM", "hint": "Volatile memory"},
    {"word": "BYTE", "hint": "Group of 8 bits"},
    {"word": "IDE", "hint": "Software for Coding"},
    {"word": "CODE", "hint": "Instructions for a computer"}]

medium_words = [
    {"word": "PYTHON", "hint": "A popular programming language"},
    {"word": "ARRAY", "hint": "Data structure that holds multiple items"},
    {"word": "INPUT", "hint": "What the user provides"},
    {"word": "DEBUG", "hint": "Fixing code errors"},
    {"word": "SYNTAX", "hint": "Grammar rules of programming"},
    {"word": "RETURN", "hint": "Used to exit a function with a value"}
]

hard_words = [
    {"word": "COMPUTER", "hint": "An electronic machine"},
    {"word": "DATABASE", "hint": "Structured storage for information"},
    {"word": "CODING", "hint": "Writing software instructions"},
    {"word": "PROGRAMMING", "hint": "Process of developing applications"},
    {"word": "VARIABLE", "hint": "A named storage for data"}
]

word_banks = {"easy": easy_words, "medium": medium_words, "hard": hard_words}


# === Game State ===
word = ""
guessed_letters = set()
incorrect_guesses = 0
max_incorrect_guesses = 5
try:
    cat_images = [ImageTk.PhotoImage(Image.open(f"miming{i}.png").resize((200, 200))) for i in range(max_incorrect_guesses + 1)]
except FileNotFoundError as e:
    print(f"Warning: Could not load cat images - {e}. Using placeholder.")
    cat_images = [tk.Label(root, text="Image Missing", bg="#ffe0ae") for _ in range(max_incorrect_guesses + 1)]
current_cat_image = None
cat_image_label = tk.Label(root, bg="#ffe0ae")
word_display_label = None
keyboard_frame = None
letter_buttons = {}
current_level_frame = None
game_over = False
streaks = {"easy": 0, "medium": 0, "hard": 0}
current_level = None
streak_label = None
game_started = False


# === Utility Functions ===
def load_image(filename, size=(200, 200)):
    try:
        img = Image.open(filename)
        img = img.resize(size)
        return ImageTk.PhotoImage(img)
    except FileNotFoundError:
        print(f"Error: {filename} not found. Using placeholder.")
        return None


def show_start_screen():
    start_frame.tkraise()
    level_select_frame.tkraise()


def start_game(level_name, frame, cat_label, word_label, streak_lab):
    global word, guessed_letters, incorrect_guesses, current_level_frame, cat_image_label, word_display_label, game_over, streaks, current_level, streak_label, game_started
    selected = random.choice(word_banks[level_name.lower()])
    word = selected["word"]
    hint = selected["hint"]
    if level_name.lower() == "easy":
        hint_label_easy.config(text=f"Hint: {hint}")
    elif level_name.lower() == "medium":
        hint_label_med.config(text=f"Hint: {hint}")
    elif level_name.lower() == "hard":
        hint_label_hard.config(text=f"Hint: {hint}")
    guessed_letters = set()
    incorrect_guesses = 0
    current_level = level_name.lower()
    current_level_frame = frame
    cat_image_label = cat_label
    word_display_label = word_label
    streak_label = streak_lab
    game_over = False
    game_started = False
    update_streak_display()
    reset_keyboard()
    update_word_display()
    update_cat_image(incorrect_guesses)
    frame.tkraise()


def update_word_display():
    global game_over, streaks, current_level, game_started
    if word_display_label:
        display = " ".join([letter if letter in guessed_letters else "_" for letter in word])
        word_display_label.config(text=display)
        if "_" not in display and not game_over:
            game_over = True
            streaks[current_level] += 1
            update_streak_display()
            game_over_screen(f"You Win! The word was: {word}", is_win=True)
        elif incorrect_guesses >= max_incorrect_guesses and not game_over:
            game_over = True
            streaks[current_level] = 0
            update_streak_display()
            game_over_screen(f"Game Over! The word was: {word}", is_win=False)


def guess_letter(letter):
    global incorrect_guesses, game_started
    if click_sound:
        click_sound.play()

    if letter not in guessed_letters and word_display_label:
        game_started = True
        guessed_letters.add(letter)
        letter_buttons[letter].config(bg="gray")
        if letter not in word:
            incorrect_guesses += 1
            update_cat_image(incorrect_guesses)
        update_word_display()


def update_cat_image(incorrect_count):
    global current_cat_image, game_over
    if cat_image_label and 0 <= incorrect_count <= max_incorrect_guesses:
        if isinstance(cat_images[incorrect_count], ImageTk.PhotoImage):
            current_cat_image = cat_images[incorrect_count]
            cat_image_label.config(image=current_cat_image)
        else:
            cat_image_label.config(text="Image Missing")
    if meow_sound:
        meow_sound.play()


def create_keyboard(parent_frame):
    frame = tk.Frame(parent_frame, bg="#ffe0ae")
    qwerty_layout = [['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
                       ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
                            ['Z', 'X', 'C', 'V', 'B', 'N', 'M']]
    max_cols = 10
    for i, row in enumerate(qwerty_layout):
        start_padding = (max_cols - len(row)) // 2
        for j in range(start_padding):
            tk.Label(frame, width=3, height=1, bg="#ffe0ae").grid(row=i, column=j, padx=2, pady=2)
        for j, letter in enumerate(row):
            btn = tk.Button(frame, text=letter, width=4, height=2, bg="#4A2C2A", fg="white",
                            activebackground="#808080", command=lambda l=letter: guess_letter(l))
            btn.grid(row=i, column=start_padding + j, padx=3, pady=3)
            letter_buttons[letter] = btn
    frame.pack(pady=10, expand=True, fill="x")
    return frame


def reset_keyboard():
    for btn in letter_buttons.values():
        btn.config(bg="#4A2C2A")


def game_over_screen(message, is_win):
    if is_win:
        if win_sound:
            win_sound.play()
    else:
        if gameover_sound:
            gameover_sound.play()
    global current_level_frame
    if current_level_frame:
        game_over_frame = tk.Toplevel(root, bg="#ffe0ae")
        game_over_frame.transient(root)  # Centers the popup relative to the main window
        game_over_frame.title("Game Over")
        # Fixed size to fit content and avoid overlap
        game_over_frame.geometry("300x180")
        message_label = tk.Label(game_over_frame, text=message, bg="#ffe0ae", font=("Arial", 14), wraplength=260)
        message_label.pack(pady=20, padx=20)
        button_frame = tk.Frame(game_over_frame, bg="#ffe0ae")
        button_frame.pack(pady=10)
        if is_win:
            replay_button = tk.Button(button_frame, text="Continue", bg="#4A2C2A", fg="white", font=("Arial", 12),
                                    command=lambda: restart_game(current_level_frame, game_over_frame))
            replay_button.pack(side=tk.LEFT, padx=10)
        else:
            replay_button = tk.Button(button_frame, text="Replay", bg="#4A2C2A", fg="white", font=("Arial", 12),
                                    command=lambda: restart_game(current_level_frame, game_over_frame))
            replay_button.pack(side=tk.LEFT, padx=10)
        main_menu_button = tk.Button(button_frame, text="Main Menu", bg="#4A2C2A", fg="white", font=("Arial", 12),
                                    command=lambda: switch_to_main_menu(game_over_frame))
        main_menu_button.pack(side=tk.LEFT, padx=10)


def restart_game(level_frame, game_over_window):
    global word, guessed_letters, incorrect_guesses, cat_images, current_cat_image, game_over
    reset_game_state()
    try:
        cat_images = [ImageTk.PhotoImage(Image.open(f"miming{i}.png").resize((200, 200))) for i in range(max_incorrect_guesses + 1)]
    except FileNotFoundError as e:
        print(f"Warning: Could not reload cat images - {e}. Using placeholder.")
        cat_images = [tk.Label(root, text="Image Missing", bg="#ffe0ae") for _ in range(max_incorrect_guesses + 1)]
    update_cat_image(0)
    game_over = False
    if level_frame == easy_game_frame:
        start_game("easy", easy_game_frame, cat_image_label_easy, word_display_label_easy, streak_label_easy)
    elif level_frame == medium_game_frame:
        start_game("medium", medium_game_frame, cat_image_label_med, word_display_label_med, streak_label_med)
    elif level_frame == hard_game_frame:
        start_game("hard", hard_game_frame, cat_image_label_hard, word_display_label_hard, streak_label_hard)
    game_over_window.destroy()


def switch_to_main_menu(game_over_window=None):
    global current_level_frame, game_over, word, guessed_letters, incorrect_guesses
    for widget in root.winfo_children():
        if isinstance(widget, tk.Toplevel):
            widget.destroy()
    word = ""
    guessed_letters = set()
    incorrect_guesses = 0
    game_over = True
    if current_level_frame:
        update_cat_image(0)
    if not game_over and game_started:
        show_exit_confirmation()
    else:
        start_frame.tkraise()


def reset_game_state():
    global word, guessed_letters, incorrect_guesses
    word = ""
    guessed_letters = set()
    incorrect_guesses = 0
    reset_keyboard()
    if word_display_label:
        update_word_display()
    if cat_image_label:
        update_cat_image(0)


def update_streak_display():
    global streak_label, streaks, current_level
    if streak_label and current_level:
        streak_label.config(text=f"Streak: {streaks[current_level]}")


def show_exit_confirmation():
    global current_level_frame, game_started
    if not game_over and game_started and current_level_frame:
        confirm_frame = tk.Toplevel(root, bg="#ffe0ae")
        confirm_frame.transient(root)  # Centers the popup relative to the main window
        confirm_frame.title("Confirm Exit")
        # Fixed size to match content and avoid overlap
        confirm_frame.geometry("300x200")
        message_label = tk.Label(confirm_frame, text="You're halfway through the game. If you exit now, your streak will reset to zero. Proceed?", bg="#ffe0ae", font=("Arial", 12), wraplength=260)
        message_label.pack(pady=15, padx=20)
        button_frame = tk.Frame(confirm_frame, bg="#ffe0ae")
        button_frame.pack(pady=10)
        continue_button = tk.Button(button_frame, text="Continue Game", bg="#4A2C2A", fg="white", font=("Arial", 10), command=confirm_frame.destroy)
        continue_button.pack(side=tk.LEFT, padx=10)
        exit_button = tk.Button(button_frame, text="Go to Main Menu", bg="#4A2C2A", fg="white", font=("Arial", 10), command=lambda: confirm_reset(confirm_frame))
        exit_button.pack(side=tk.LEFT, padx=10)
    else:
        confirm_frame = tk.Toplevel(root, bg="#ffe0ae")
        confirm_frame.transient(root)  # Centers the popup relative to the main window
        confirm_frame.title("Confirm Exit")
        # Fixed size to match content and avoid overlap
        confirm_frame.geometry("300x150")
        message_label = tk.Label(confirm_frame, text="Go back to the main menu?", bg="#ffe0ae", font=("Arial", 12))
        message_label.pack(pady=15, padx=20)
        button_frame = tk.Frame(confirm_frame, bg="#ffe0ae")
        button_frame.pack(pady=10)
        continue_button = tk.Button(button_frame, text="Continue Game", bg="#4A2C2A", fg="white", font=("Arial", 10), command=confirm_frame.destroy)
        continue_button.pack(side=tk.LEFT, padx=10)
        exit_button = tk.Button(button_frame, text="Go to Main Menu", bg="#4A2C2A", fg="white", font=("Arial", 10), command=lambda: start_frame.tkraise())
        exit_button.pack(side=tk.LEFT, padx=10)


def confirm_reset(confirm_frame):
    global streaks, current_level
    if current_level and streaks:
        streaks[current_level] = 0
        update_streak_display()
    confirm_frame.destroy()
    switch_to_main_menu()


def show_reset_confirmation():
    confirm_frame = tk.Toplevel(root, bg="#ffe0ae")
    confirm_frame.transient(root)  # Centers the popup relative to the main window
    confirm_frame.title("Confirm Reset")
    # Fixed size to match content and avoid overlap
    confirm_frame.geometry("300x150")
    message_label = tk.Label(confirm_frame, text="Are you sure you want to reset the word and streak?", bg="#ffe0ae", font=("Arial", 12), wraplength=260)
    message_label.pack(pady=15, padx=20)
    button_frame = tk.Frame(confirm_frame, bg="#ffe0ae")
    button_frame.pack(pady=10)
    cancel_button = tk.Button(button_frame, text="Cancel", bg="#4A2C2A", fg="white", font=("Arial", 10), command=confirm_frame.destroy)
    cancel_button.pack(side=tk.LEFT, padx=10)
    reset_button = tk.Button(button_frame, text="Reset", bg="#4A2C2A", fg="white", font=("Arial", 10), command=lambda: confirm_reset_game(confirm_frame))
    reset_button.pack(side=tk.LEFT, padx=10)


def confirm_reset_game(confirm_frame):
    global word, guessed_letters, incorrect_guesses, streaks, current_level
    reset_game_state()
    if current_level and streaks:
        streaks[current_level] = 0
        update_streak_display()
    confirm_frame.destroy()


def handle_option_select(value, current_frame):
    if (value == "Level Select" or value == "Home Page") and not game_over and game_started:
        show_exit_confirmation()
    elif value == "Level Select":
        level_select_frame.tkraise()
    elif value == "Home Page":
        switch_to_main_menu()


# === Frame Definitions ===
start_frame = tk.Frame(root, bg="#ffe0ae")
menu_frame = tk.Frame(root, bg="#ffe0ae")
level_select_frame = tk.Frame(root, bg="#ffe0ae")
easy_game_frame = tk.Frame(root, bg="#ffe0ae")
medium_game_frame = tk.Frame(root, bg="#ffe0ae")
hard_game_frame = tk.Frame(root, bg="#ffe0ae")


for frame in (start_frame, menu_frame, level_select_frame, easy_game_frame, medium_game_frame, hard_game_frame):
    frame.grid(row=0, column=0, sticky='nsew')


# === Start Screen Setup ===
main_frame = tk.Frame(start_frame, bg="#ffe0ae")
main_frame.pack(expand=True)
title_label = tk.Label(main_frame, text="HangMeow", bg="#ffe0ae", fg="#4A2C2A", font=("Arial", 32))
title_label.pack(pady=20, expand=True)
meow_image_start = load_image("miming0.png")
if meow_image_start:
    imglabel_start = tk.Label(main_frame, image=meow_image_start, bg="#ffe0ae")
    imglabel_start.image = meow_image_start
    imglabel_start.pack(pady=20, expand=True)
else:
    imglabel_start = tk.Label(main_frame, text="Image Missing", bg="#ffe0ae", font=("Arial", 20))
    imglabel_start.pack(pady=20, expand=True)
desc_label = tk.Label(main_frame, text="Guess the right word before he turns into a loaf!", bg="#ffe0ae", font=("Arial", 16))
desc_label.pack(pady=10, expand=True)
start_button = tk.Button(main_frame, text="Start", width=15, height=2, bg="#4A2C2A", fg="white", font=("Arial", 14), command=show_start_screen)
start_button.pack(pady=30, expand=True)
# Volume Control Label
volume_label = tk.Label(main_frame, text="Music Volume", bg="#ffe0ae", font=("Arial", 12))
volume_label.pack(pady=(10, 0))
# Volume Slider (0 to 1.0)
def set_volume(val):
    pygame.mixer.music.set_volume(float(val))

volume_slider = tk.Scale(main_frame, from_=0, to=1, resolution=0.01,
    orient="horizontal", length=200, bg="#ffe0ae", troughcolor="#4A2C2A", fg="#4A2C2A", highlightthickness=0, command=set_volume)
volume_slider.set(0.5)  # Default volume at 50%
volume_slider.pack(pady=(0, 20))


# === Level Select Setup ===
level_main_frame = tk.Frame(level_select_frame, bg="#ffe0ae")
level_main_frame.pack(expand=True, fill="both")
level_label = tk.Label(level_main_frame, text="Select Game Mode", bg="#ffe0ae", fg="#4A2C2A", font=("Arial", 24))
level_label.pack(pady=50, expand=True)
button_frame = tk.Frame(level_main_frame, bg="#ffe0ae")
button_frame.pack(expand=True)
easbutton_level = tk.Button(button_frame, text="Easy", width=15, height=2, bg="#4A2C2A", fg="white", font=("Arial", 14),
                           command=lambda: start_game("easy", easy_game_frame, cat_image_label_easy, word_display_label_easy, streak_label_easy))
easbutton_level.pack(pady=15, side=tk.TOP, fill=tk.X)
medbutton_level = tk.Button(button_frame, text="Medium", width=15, height=2, bg="#4A2C2A", fg="white", font=("Arial", 14),
                           command=lambda: start_game("medium", medium_game_frame, cat_image_label_med, word_display_label_med, streak_label_med))
medbutton_level.pack(pady=15, side=tk.TOP, fill=tk.X)
harbutton_level = tk.Button(button_frame, text="Hard", width=15, height=2, bg="#4A2C2A", fg="white", font=("Arial", 14),
                           command=lambda: start_game("hard", hard_game_frame, cat_image_label_hard, word_display_label_hard, streak_label_hard))
harbutton_level.pack(pady=15, side=tk.TOP, fill=tk.X)


# === Easy Game Frame Setup ===
mode_box_easy = tk.Frame(easy_game_frame, bg="#4A2C2A", padx=10, pady=5)
mode_box_easy.pack(pady=10, expand=True)
easlabel = tk.Label(mode_box_easy, text="Easy mode", bg="#4A2C2A", fg="white", font=("Arial", 18))
easlabel.pack(expand=True)
cat_image_label_easy = tk.Label(easy_game_frame, bg="#ffe0ae")
cat_image_label_easy.pack(pady=10, expand=True)
word_display_label_easy = tk.Label(easy_game_frame, text="_ _ _", bg="#ffe0ae", fg="#4A2C2A", font=("Arial", 24))
word_display_label_easy.pack(pady=10, expand=True)
hint_label_easy = tk.Label(easy_game_frame, text="", bg="#ffe0ae", fg="#4A2C2A", font=("Arial", 16))
hint_label_easy.pack(pady=5)
streak_label_easy = tk.Label(easy_game_frame, text="Streak: 0", bg="#ffe0ae", fg="#4A2C2A", font=("Arial", 14))
streak_label_easy.pack(pady=10, expand=True)
keyboard_frame_easy = create_keyboard(easy_game_frame)
keyboard_frame_easy.pack(pady=10, expand=True, fill="x")
button_frame_easy = tk.Frame(easy_game_frame, bg="#ffe0ae")
button_frame_easy.pack(pady=10, expand=True)
options_var_easy = tk.StringVar(easy_game_frame)
options_var_easy.set("Options")
options_menu_easy = tk.OptionMenu(easy_game_frame, options_var_easy, "Level Select", "Home Page", command=lambda value: handle_option_select(value, easy_game_frame))
options_menu_easy.config(bg="#4A2C2A", fg="white", font=("Arial", 12))
options_menu_easy.pack(in_=button_frame_easy, side=tk.LEFT, padx=5, expand=True)
refresh_button_easy = tk.Button(easy_game_frame, text="Reset", width=10, height=1, bg="#4A2C2A", fg="white", font=("Arial", 12), command=show_reset_confirmation)
refresh_button_easy.pack(in_=button_frame_easy, side=tk.LEFT, padx=5, expand=True)


# === Medium Game Frame Setup ===
mode_box_med = tk.Frame(medium_game_frame, bg="#4A2C2A", padx=10, pady=5)
mode_box_med.pack(pady=10, expand=True)
medlabel = tk.Label(mode_box_med, text="Medium mode", bg="#4A2C2A", fg="white", font=("Arial", 18))
medlabel.pack(expand=True)
cat_image_label_med = tk.Label(medium_game_frame, bg="#ffe0ae")
cat_image_label_med.pack(pady=10, expand=True)
word_display_label_med = tk.Label(medium_game_frame, text="_ _ _ _ _ _", bg="#ffe0ae", fg="#4A2C2A", font=("Arial", 24))
word_display_label_med.pack(pady=10, expand=True)
hint_label_med = tk.Label(medium_game_frame, text="", bg="#ffe0ae", fg="#4A2C2A", font=("Arial", 16))
hint_label_med.pack(pady=5)
streak_label_med = tk.Label(medium_game_frame, text="Streak: 0", bg="#ffe0ae", fg="#4A2C2A", font=("Arial", 14))
streak_label_med.pack(pady=10, expand=True)
keyboard_frame_med = create_keyboard(medium_game_frame)
keyboard_frame_med.pack(pady=10, expand=True, fill="x")
button_frame_med = tk.Frame(medium_game_frame, bg="#ffe0ae")
button_frame_med.pack(pady=10, expand=True)
options_var_med = tk.StringVar(medium_game_frame)
options_var_med.set("Options")
options_menu_med = tk.OptionMenu(medium_game_frame, options_var_med, "Level Select", "Home Page", command=lambda value: handle_option_select(value, medium_game_frame))
options_menu_med.config(bg="#4A2C2A", fg="white", font=("Arial", 12))
options_menu_med.pack(in_=button_frame_med, side=tk.LEFT, padx=5, expand=True)
refresh_button_med = tk.Button(medium_game_frame, text="Reset", width=10, height=1, bg="#4A2C2A", fg="white", font=("Arial", 12), command=show_reset_confirmation)
refresh_button_med.pack(in_=button_frame_med, side=tk.LEFT, padx=5, expand=True)


# === Hard Game Frame Setup ===
mode_box_hard = tk.Frame(hard_game_frame, bg="#4A2C2A", padx=10, pady=5)
mode_box_hard.pack(pady=10, expand=True)
hardlabel = tk.Label(mode_box_hard, text="Hard mode", bg="#4A2C2A", fg="white", font=("Arial", 18))
hardlabel.pack(expand=True)
cat_image_label_hard = tk.Label(hard_game_frame, bg="#ffe0ae")
cat_image_label_hard.pack(pady=10, expand=True)
word_display_label_hard = tk.Label(hard_game_frame, text="_ _ _ _ _ _ _ _", bg="#ffe0ae", fg="#4A2C2A", font=("Arial", 24))
word_display_label_hard.pack(pady=10, expand=True)
hint_label_hard = tk.Label(hard_game_frame, text="", bg="#ffe0ae", fg="#4A2C2A", font=("Arial", 16))
hint_label_hard.pack(pady=5)
streak_label_hard = tk.Label(hard_game_frame, text="Streak: 0", bg="#ffe0ae", fg="#4A2C2A", font=("Arial", 14))
streak_label_hard.pack(pady=10, expand=True)
keyboard_frame_hard = create_keyboard(hard_game_frame)
keyboard_frame_hard.pack(pady=10, expand=True, fill="x")
button_frame_hard = tk.Frame(hard_game_frame, bg="#ffe0ae")
button_frame_hard.pack(pady=10, expand=True)
options_var_hard = tk.StringVar(hard_game_frame)
options_var_hard.set("Options")
options_menu_hard = tk.OptionMenu(hard_game_frame, options_var_hard, "Level Select", "Home Page", command=lambda value: handle_option_select(value, hard_game_frame))
options_menu_hard.config(bg="#4A2C2A", fg="white", font=("Arial", 12))
options_menu_hard.pack(in_=button_frame_hard, side=tk.LEFT, padx=5, expand=True)
refresh_button_hard = tk.Button(hard_game_frame, text="Reset", width=10, height=1, bg="#4A2C2A", fg="white", font=("Arial", 12), command=show_reset_confirmation)
refresh_button_hard.pack(in_=button_frame_hard, side=tk.LEFT, padx=5, expand=True)


# === Game Start and Loop ===
start_frame.tkraise()
root.update()
root.mainloop()

