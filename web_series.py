import pandas as pd
import matplotlib.pyplot as plt
from tkinter import Tk, Label, Button, StringVar, ttk, Canvas, Frame, Scrollbar
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# --- Loading our dataset ---
data = pd.read_csv("webseries_cleaned.csv")

# --- main window ---
root = Tk()
root.title("Web Series Analysis Dashboard")
root.geometry("1500x700")
root.configure(bg="#f0f4f7")

# Dropdown options for charts
chart_options = [
    "Ratings Distribution",
    "Number of WebSeries on Each OTT Platform",
    "Netflix vs Other Platforms Ratings Distribution",
    "Genre Distribution",
    "Top Performers",
    "Director Analysis",
    "Rating vs Genre",
    "Platform vs Genre"
]

selected_chart = StringVar()
selected_chart.set(chart_options[0])

Label(root, text="📊 Select a Chart:", font=("Arial", 14, "bold"), bg="#f0f4f7").pack(pady=10)

dropdown = ttk.Combobox(root, textvariable=selected_chart, values=chart_options, state="readonly", font=("Arial", 12))
dropdown.pack(pady=5)

# Container for scrollable chart area
container = Frame(root, bg="#f0f4f7")
container.pack(fill='both', expand=True)

# Scrollable canvas
canvas = Canvas(container, bg="#f0f4f7")
canvas.pack(side="left", fill="both", expand=True)

scrollbar = Scrollbar(container, orient="vertical", command=canvas.yview)
scrollbar.pack(side="right", fill="y")

canvas.configure(yscrollcommand=scrollbar.set)

plot_frame = Frame(canvas, bg="#f0f4f7")
canvas.create_window((0, 0), window=plot_frame, anchor="nw")

def on_frame_configure(event):
    canvas.configure(scrollregion=canvas.bbox("all"))

plot_frame.bind("<Configure>", on_frame_configure)

def plot_chart():
    for widget in plot_frame.winfo_children():
        widget.destroy()  # Clear previous chart

    # Adjust figure size dynamically based on window width
    fig_width = max(root.winfo_width() / 100, 10)
    fig_height = 6  # Default height
    choice = selected_chart.get()

    # For Platform vs Genre, we need slightly taller figure
    if choice == "Platform vs Genre":
        fig_height = 7

    fig, ax = plt.subplots(figsize=(fig_width, fig_height))

    if choice == "Ratings Distribution":
        ax.hist(data['ratings'], bins=10, color='skyblue', edgecolor='black')
        ax.set_title('Ratings Distribution of WEBSeries')
        ax.set_xlabel('Ratings')
        ax.set_ylabel('Frequency')

    elif choice == "Number of WebSeries on Each OTT Platform":
        platform_counts = data['ott_platform'].value_counts()
        platform_counts.plot(kind='bar', color='skyblue', ax=ax)
        ax.set_title('Number of WEBSeries on Each OTT Platform')
        ax.set_xlabel('OTT Platform')
        ax.set_ylabel('Number of TV Series')
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')

    elif choice == "Netflix vs Other Platforms Ratings Distribution":
        netflix_series = data[data['ott_platform'] == 'Netflix']
        other_series = data[data['ott_platform'] != 'Netflix']
        ax.hist(netflix_series['ratings'], bins=10, color='red', alpha=0.5, label='Netflix')
        ax.hist(other_series['ratings'], bins=10, color='blue', alpha=0.5, label='Other Platforms')
        ax.set_title('Ratings Distribution: Netflix vs Other Platforms')
        ax.set_xlabel('Ratings')
        ax.set_ylabel('Frequency')
        ax.legend()

    elif choice == "Genre Distribution":
        genre_counts = data['genre'].value_counts()
        genre_counts.plot(kind='bar', color='skyblue', ax=ax)
        ax.set_title('Genre Distribution of WEBSeries')
        ax.set_xlabel('Genre')
        ax.set_ylabel('Number of WEBSeries')
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')

    elif choice == "Top Performers":
        performers = data['performers'].str.split(', ', expand=True).stack()
        top_performers = performers.value_counts().head(10)
        top_performers.plot(kind='bar', color='skyblue', ax=ax)
        ax.set_title('Top Performers in TV Series')
        ax.set_xlabel('Performer')
        ax.set_ylabel('Number of Appearances')
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')

    elif choice == "Director Analysis":
        directors = data['director_name'].str.split(', ', expand=True).stack()
        director_counts = directors.value_counts().head(10)
        director_counts.plot(kind='bar', color='skyblue', ax=ax)
        ax.set_title('Top Directors of TV Series')
        ax.set_xlabel('Director')
        ax.set_ylabel('Number of TV Series')
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')

    elif choice == "Rating vs Genre":
        ax.scatter(data['ratings'], data['genre'], color='green', alpha=0.6)
        ax.set_title('Rating vs. Genre')
        ax.set_xlabel('Ratings')
        ax.set_ylabel('Genre')
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')

    elif choice == "Platform vs Genre":
        platform_genre_counts = data.groupby(['ott_platform', 'genre']).size().unstack(fill_value=0)
        platform_genre_counts.plot(kind='bar', stacked=True, cmap='tab20', ax=ax)
        ax.set_title('Platform vs. Genre')
        ax.set_xlabel('OTT Platform', labelpad=20)
        ax.set_ylabel('Number of TV Series')
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')

    fig.tight_layout()  # <-- This ensures nothing gets cut off

    canvas_plot = FigureCanvasTkAgg(fig, master=plot_frame)
    canvas_plot.draw()
    canvas_plot.get_tk_widget().pack(fill='both', expand=True, pady=10)


# Put the button at the bottom
Button(root, text="Show Chart", command=plot_chart,
       font=("Arial", 12, "bold"), bg="#007acc", fg="white").pack(side="bottom", pady=15)

root.mainloop()

