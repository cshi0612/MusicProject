import tkinter as tk
import os
from datetime import date

from pydub import AudioSegment
from pydub.playback import _play_with_simpleaudio
import re

from tracker import Tracker
from ai_methods import prediction
from database import Database

global playback
playback = None
global duration
duration = 1
global current_genre
global tracker
global start
start = False

tracker = Tracker()
db = Database()

genreDic = {}
music_folder = "./Music"
for genre in os.listdir(music_folder):
    if genre == '.DS_Store':
        continue  # Skip to the next iteration
    if os.path.isdir(os.path.join(music_folder, genre)):  # Check if it's a directory
        genreDic[genre] = [file for file in os.listdir(os.path.join(music_folder, genre)) if file != '.DS_Store']

root1 = tk.Tk()
root1.geometry('800x600')
root1.title('Music Player')
root1.configure(bg='#FFAD66')
frame1 = tk.Frame(root1, bg='#FFAD66')

font_label = ('Verdana', 10)
font_text = ('Verdana', 10)

l1 = tk.Label(frame1, text="Word Count:", font=font_label, bg='#FFAD66')
l1.grid(column=0, row=0, pady=10)

l2 = tk.Label(frame1, text="Words Per Min:", font=font_label, bg='#FFAD66')
l2.grid(column=0, row=1, pady=10)

l3 = tk.Label(frame1, text="# of Typos:", font=font_label, bg='#FFAD66')
l3.grid(column=2, row=0, pady=10)

l5 = tk.Label(frame1, text="0", font=font_text, bg='#FFAD66')
l5.grid(column=1, row=0, pady=10, padx=5)

l6 = tk.Label(frame1, text="0", font=font_text, bg='#FFAD66')
l6.grid(column=3, row=0, pady=10, padx=5)

l4 = tk.Label(frame1, text="Efficiency:", font=font_label, bg='#FFAD66')
l4.grid(column=2, row=1, pady=10)

l7 = tk.Label(frame1, text="0", font=font_text, bg='#FFAD66')
l7.grid(column=3, row=1, pady=10, padx=5)

l8 = tk.Label(frame1, text="0", font=font_text, bg='#FFAD66')
l8.grid(column=1, row=1, pady=10, padx=5)

frame1.grid(column=0, row=0, padx=20, pady=20)

frame2 = tk.Frame(root1, bg='#FFAD66')
textBox = tk.Text(frame2, height=20, width=40, font=font_text, wrap="word")
textBox.grid(row=0, column=0, padx=20, sticky="nesw")

frame2.grid(column=0, row=1, padx=20, pady=20)

frame3 = tk.Frame(frame2, bg='#FFAD66')

counter = 0


def is_playing():
    return playback and playback.is_playing()


def clear_textbox():
    textBox.delete("1.0", "end")


def playMusic(genre, song):
    global current_music
    global current_genre
    global playback
    global duration

    current_music = song
    current_genre = genre

    if playback and playback.is_playing():
        playback.stop()

    audio_path = music_folder + "/" + genre + "/" + song
    if not os.path.isfile(audio_path):
        print(f'File not found: {audio_path}')
    else:
        # pass
        audio = AudioSegment.from_file(audio_path)

    duration = audio.duration_seconds
    playback = _play_with_simpleaudio(audio)
    print(duration)
    clear_textbox()


def calculate_n_words_per_min():
    global duration
    # remove all punctuations before finding possible misspelled words
    # in other words, get all the text
    textInput = str(textBox.get("1.0", "end-1c"))
    textInput = re.sub(r'[^\w\s]', '', textInput)
    words = textInput.split()
    words = [i for i in words if i]

    words_per_min = len(words) // (duration / 60)
    return words_per_min, words


def create_history_window():
    # Create a new window
    history_window = tk.Toplevel(root1)
    history_window.title("History")

    # Get data from the database
    data = db.read_data()

    # Create Labels for each column
    labels = ["date", "Number of pauses", "Total time of pause", "backspaces",
              "num_typos", "song", "song_duration", "genre", "wpm", "num_words", "efficiency"]

    # Create a frame for the header
    header_frame = tk.Frame(history_window)
    header_frame.grid(row=0, column=0)

    # Create header labels
    for i, label in enumerate(labels):
        header_label = tk.Label(header_frame, text=label, font=("Arial", 14, "bold"), bd=2, relief='solid')
        header_label.grid(row=0, column=i, sticky="nsew")

    # Display data in the window
    for i, doc in enumerate(data):
        # Use a different background color for every second row to improve readability
        if i % 2 == 0:
            bg_color = 'white'
        else:
            bg_color = 'light grey'

        # Create a new frame for each row, to allow for background color and border
        row_frame = tk.Frame(history_window, bg=bg_color, bd=2, relief='solid')
        row_frame.grid(row=i + 1, column=0, sticky="nsew", padx=5, pady=5)  # padding around each row

        for j, label in enumerate(labels):
            label_text = doc.get(label, 'N/A')
            data_label = tk.Label(row_frame, text=label_text, bg=bg_color)
            data_label.grid(row=0, column=j, sticky="nsew")


def check_event():
    global current_music
    global current_genre
    global duration
    global start

    # The user has just clicked the song and barely started
    if is_playing() and not start:
        start = True
    # The song has ended, so we need to check everything one last time + efficiency
    if not is_playing() and start:
        wpm, words = calculate_n_words_per_min()
        l5.config(text=str(len(words)))
        l8.config(text=str(wpm))
        num_typos = tracker.get_n_typos(words)
        l6.config(text=str(num_typos))
        textInput = str(textBox.get("1.0", "end-1c"))
        efficient = prediction(textInput)
        l7.config(text=str(efficient))
        if tracker.user_has_typed():
            user_info = tracker.get_pauses()
        else:
            user_info = {'Number of pauses': 1, 'Total time of pause': duration}
        user_info['backspaces'] = tracker.get_n_backspace()
        user_info['num_typos'] = num_typos
        user_info['song'] = current_music
        user_info['song_duration'] = duration
        user_info['genre'] = current_genre
        user_info['wpm'] = wpm
        user_info['num_words'] = str(len(words))
        user_info['date'] = str(date.today())
        user_info['efficiency'] = efficient
        # print(user_info)
        db.add_data(user_info)
        print(db.read_data())
        start = False

    root1.after(100, check_event)


for genre in genreDic:
    genre_label = tk.Label(frame3, text=genre)
    genre_label.grid(row=2 * counter, column=0)
    # Create a frame for the canvas with non-zero row&column weights
    frame_canvas = tk.Frame(frame3)
    frame_canvas.grid(row=2 * counter + 1, column=0)
    frame_canvas.grid_rowconfigure(0, weight=1)
    frame_canvas.grid_columnconfigure(0, weight=1)
    # Set grid_propagate to False to allow 5-by-5 buttons resizing later
    frame_canvas.grid_propagate(False)

    # Add a canvas in that frame
    canvas = tk.Canvas(frame_canvas, bg="yellow")
    canvas.grid(row=0, column=0, sticky="news")

    # Link a scrollbar to the canvas
    vsb = tk.Scrollbar(frame_canvas, orient="vertical", command=canvas.yview)
    vsb.grid(row=0, column=1, sticky='ns')
    canvas.configure(yscrollcommand=vsb.set)

    # Create a frame to contain the buttons
    frame_buttons = tk.Frame(canvas, bg="blue")
    canvas.create_window((0, 0), window=frame_buttons, anchor='nw')
    current_music = None
    # Add 9-by-5 buttons to the frame
    buttons = [tk.Button() for i in range(len(genreDic[genre]))]
    counter2 = 0

    # Makes each song a button
    for i in genreDic[genre]:
        def action(x=genre, song=i):
            return playMusic(x, song)


        buttons[counter2] = tk.Button(frame_buttons, text=(f"{i}"), command=action)
        buttons[counter2].grid(row=counter2, column=0, sticky='news')
        counter2 += 1

    # Update buttons frames idle tasks to let tkinter calculate buttons sizes
    frame_buttons.update_idletasks()

    n_rows_per_genre = 2
    column_width = buttons[0].winfo_width()
    first_n_rows_height = sum([buttons[i].winfo_height() for i in range(0, n_rows_per_genre)])
    frame_canvas.config(width=column_width + vsb.winfo_width(),
                        height=first_n_rows_height)

    # Set the canvas scrolling region
    canvas.config(scrollregion=canvas.bbox("all"))
    counter += 1
frame3.grid(row=0, column=1)
buttonPop = tk.Button(frame3, text="POP")

history_button = tk.Button(frame1, text="History", command=create_history_window)
history_button.grid(column=0, row=2, columnspan=4, padx=10, pady=10)

root1.after(100, check_event)
root1.mainloop()
