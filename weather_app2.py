import tkinter as tk
from tkinter import messagebox
import requests
from datetime import datetime
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Replace with your OpenWeatherMap API key
API_KEY = "92a41c0bcde2aeac77ecc378edd80712"
HISTORY_FILE = "history.txt"
MAX_HISTORY = 5

class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🌦️ Smart Weather Forecast")
        self.root.geometry("600x600")
        self.root.resizable(True, True)

        # Theme settings
        self.theme = "light"
        self.light_theme = {
            "bg": "#ecf0f1",
            "frame": "#ffffff",
            "fg": "#2c3e50",
            "button": "#2980b9",
            "entry_bg": "#ffffff"
        }
        self.dark_theme = {
            "bg": "#2c3e50",
            "frame": "#34495e",
            "fg": "#ecf0f1",
            "button": "#16a085",
            "entry_bg": "#bdc3c7"
        }

        self.temp_history = {}  # City: Temp mapping for plotting
        self.setup_gui()
        self.load_history()

    def setup_gui(self):
        self.apply_theme()

        # Title
        self.title_label = tk.Label(self.root, text="🌤️ Weather App", font=("Helvetica", 24, "bold"), bg=self.theme_colors["bg"], fg=self.theme_colors["fg"])
        self.title_label.pack(pady=10)

        # Input
        self.input_frame = tk.Frame(self.root, bg=self.theme_colors["bg"])
        self.input_frame.pack()

        tk.Label(self.input_frame, text="Enter City:", font=("Helvetica", 14), bg=self.theme_colors["bg"], fg=self.theme_colors["fg"]).grid(row=0, column=0, padx=10)
        self.city_entry = tk.Entry(self.input_frame, font=("Helvetica", 14), width=25, bg=self.theme_colors["entry_bg"], fg=self.theme_colors["fg"])
        self.city_entry.grid(row=0, column=1)

        self.search_button = tk.Button(self.root, text="🔍 Get Weather", font=("Helvetica", 12), command=self.get_weather, bg=self.theme_colors["button"], fg="white")
        self.search_button.pack(pady=10)

        # Results
        self.result_frame = tk.Frame(self.root, bg=self.theme_colors["frame"], bd=2, relief="groove")
        self.result_frame.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

        self.weather_text = tk.Label(self.result_frame, text="", font=("Helvetica", 14), bg=self.theme_colors["frame"], fg=self.theme_colors["fg"], justify="left", anchor="nw")
        self.weather_text.pack(padx=10, pady=10, anchor="w")

        # Suggestions
        self.suggestion_label = tk.Label(self.root, text="", font=("Helvetica", 12, "italic"), bg=self.theme_colors["bg"], fg="green")
        self.suggestion_label.pack()

        # Recent cities
        self.history_label = tk.Label(self.root, text="Recent Cities:", font=("Helvetica", 12, "bold"), bg=self.theme_colors["bg"], fg=self.theme_colors["fg"])
        self.history_label.pack(pady=(10, 0))

        self.history_text = tk.Label(self.root, text="", font=("Helvetica", 12), bg=self.theme_colors["bg"], fg=self.theme_colors["fg"])
        self.history_text.pack()

        # Theme and chart buttons
        button_frame = tk.Frame(self.root, bg=self.theme_colors["bg"])
        button_frame.pack(pady=10)

        self.toggle_button = tk.Button(button_frame, text="🌗 Toggle Theme", command=self.toggle_theme, bg=self.theme_colors["button"], fg="white")
        self.toggle_button.grid(row=0, column=0, padx=5)

        self.chart_button = tk.Button(button_frame, text="📊 Show Temp Chart", command=self.show_chart, bg=self.theme_colors["button"], fg="white")
        self.chart_button.grid(row=0, column=1, padx=5)

    def apply_theme(self):
        self.theme_colors = self.light_theme if self.theme == "light" else self.dark_theme
        self.root.configure(bg=self.theme_colors["bg"])

    def update_theme_widgets(self):
        self.apply_theme()
        widgets = [
            self.root, self.title_label, self.input_frame, self.search_button,
            self.result_frame, self.weather_text, self.history_label,
            self.history_text, self.toggle_button
        ]

        for widget in widgets:
            try:
                widget.configure(bg=self.theme_colors["bg"])
                if "fg" in widget.configure():  # Apply fg only if supported
                    widget.configure(fg=self.theme_colors["fg"])
            except Exception as e:
                print(f"Could not configure widget: {e}")

        self.city_entry.configure(bg=self.theme_colors["entry_bg"], fg=self.theme_colors["fg"])
        self.search_button.configure(bg=self.theme_colors["button"])
        self.toggle_button.configure(bg=self.theme_colors["button"])


    def toggle_theme(self):
        self.theme = "dark" if self.theme == "light" else "light"
        self.update_theme_widgets()

    def smart_suggestion(self, weather):
        suggestions = {
            "clear": "🌞 It's clear outside. Great day to be outdoors!",
            "cloud": "☁️ Cloudy skies. You might want a light jacket.",
            "rain": "🌧️ Don't forget your umbrella!",
            "storm": "⛈️ Stay indoors and stay safe.",
            "snow": "❄️ Dress warmly, it's snowing!",
            "mist": "🌫️ Drive carefully in the mist."
        }
        for key in suggestions:
            if key in weather.lower():
                return suggestions[key]
        return "🌈 Have a nice day!"

    def weather_theme_switch(self, weather):
        if "clear" in weather.lower():
            self.theme = "light"
        elif "rain" in weather.lower() or "storm" in weather.lower():
            self.theme = "dark"
        self.update_theme_widgets()

    def get_weather(self):
        city = self.city_entry.get().strip()
        if not city:
            messagebox.showwarning("Input Error", "Please enter a city name.")
            return
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
            response = requests.get(url)
            data = response.json()
            if data["cod"] != 200:
                raise Exception(data.get("message", "City not found"))

            weather = data["weather"][0]["description"].title()
            temp = data["main"]["temp"]
            humidity = data["main"]["humidity"]
            wind = data["wind"]["speed"]
            dt = datetime.now().strftime("%d %b %Y %I:%M %p")

            result = f"📍 City: {city.title()}\n🕒 Time: {dt}\n\n" \
                     f"🌡️ Temperature: {temp}°C\n💧 Humidity: {humidity}%\n" \
                     f"🌬️ Wind Speed: {wind} m/s\n🌥️ Condition: {weather}"
            self.weather_text.config(text=result)
            self.temp_history[city.title()] = temp
            self.suggestion_label.config(text=self.smart_suggestion(weather))
            self.weather_theme_switch(weather)

            self.save_history(city.title())
            self.load_history()
            self.temp_history[city.title()] = temp

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def save_history(self, city):
        history = []
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r") as f:
                history = [line.strip() for line in f.readlines()]

        if city in history:
            history.remove(city)
        history.insert(0, city)
        history = history[:MAX_HISTORY]

        with open(HISTORY_FILE, "w") as f:
            for item in history:
                f.write(item + "\n")

    def load_history(self):
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r") as f:
                cities = [line.strip() for line in f.readlines()]
                self.history_text.config(text=", ".join(cities))
        else:
            self.history_text.config(text="No history yet.")

    def show_chart(self):
        valid_data = {city: temp for city, temp in self.temp_history.items() if isinstance(temp, (int, float))}
    
        if not valid_data:
            messagebox.showinfo("No Data", "No valid temperature data available to display.")
            return

        chart_win = tk.Toplevel(self.root)
        chart_win.title("📊 Temperature Chart")
        chart_win.geometry("500x400")

        fig, ax = plt.subplots(figsize=(5, 3.5))
        cities = list(valid_data.keys())
        temps = list(valid_data.values())

        ax.bar(cities, temps, color='skyblue')
        ax.set_title("Temperature in Recent Cities")
        ax.set_ylabel("Temperature (°C)")
        ax.set_xlabel("City")

        chart = FigureCanvasTkAgg(fig, master=chart_win)
        chart.draw()
        chart.get_tk_widget().pack()


# Run the app
if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherApp(root)
    root.mainloop()
