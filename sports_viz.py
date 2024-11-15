import tkinter as tk
from tkinter import ttk, messagebox
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class PlayerStatsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Player Search")
        self.root.geometry("400x150")
        self.root.configure(bg="#F0F0F0")

        # Bind the window close event to a custom function
        self.root.protocol("WM_DELETE_WINDOW", self.close_application)
        
        self.create_main_ui()

    def create_main_ui(self):
        custom_font = ("Helvetica", 12)
        
        frame = tk.Frame(self.root, bg="#F0F0F0")
        frame.pack(expand=True)

        label = tk.Label(frame, text="Player:", font=custom_font, bg="#F0F0F0", fg="#333333")
        label.grid(row=0, column=0, padx=(0, 10))

        self.entry = tk.Entry(frame, width=20, font=custom_font, highlightbackground="#CCCCCC", highlightthickness=1, relief="flat")
        self.entry.grid(row=0, column=1, padx=(0, 10))
        self.entry.insert(0, "Enter player name")
        self.entry.bind("<FocusIn>", self.on_entry_click)
        self.entry.focus_set()

        self.search_button = tk.Button(frame, text="Search", font=custom_font, command=self.find_player_stats, bg="#E0E0E0", fg="#333333", relief="flat", padx=10, pady=5)
        self.search_button.grid(row=0, column=2)
        self.search_button.bind("<Enter>", self.on_enter)
        self.search_button.bind("<Leave>", self.on_leave)
        self.root.bind('<Return>', lambda event: self.find_player_stats())

    def on_entry_click(self, event):
        if self.entry.get() == "Enter player name":
            self.entry.delete(0, "end")
    
    def on_enter(self, event):
        self.search_button.config(bg="#333333", fg="#FFFFFF")

    def on_leave(self, event):
        self.search_button.config(bg="#E0E0E0", fg="#333333")

    def find_player_stats(self):
        player_name = self.entry.get().strip()
        player = player_name.split()
        
        if len(player) == 2:
            url = f"https://www.statmuse.com/nba/ask/{player[0].lower()}-{player[1].lower()}-last-25-games"
            try:
                response = requests.get(url)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                table = soup.find('table')
                
                if table:
                    headers = [th.get_text().strip() for th in table.find_all('th')]
                    rows = [[td.get_text().strip() for td in tr.find_all('td')] for tr in table.find_all('tr')[1:]]
                    df = pd.DataFrame(rows, columns=headers)
                    df = df.iloc[:len(df)-2,2:]  # Drop the bottom two rows
                    df = df.iloc[::-1].reset_index(drop=True)  # Reverse for recent games
                    df.iloc[:,0] = df.iloc[0,0].split()[0]+' '+df.iloc[0,0].split()[1]  # Clean player name column
                    df.iloc[:, 5:] = df.iloc[:, 5:].apply(pd.to_numeric, errors='coerce')  # Convert stat columns to numeric
                    print(df)
                    self.open_new_window(df)
                else:
                    messagebox.showerror("Data Error", "Could not find a data table for the player.")
            except requests.exceptions.RequestException as e:
                messagebox.showerror("Connection Error", f"Failed to retrieve data: {e}")
        else:
            messagebox.showerror("Input Error", "Please enter a full name (First Last).")

    def open_new_window(self, df):
        self.root.withdraw()
        new_root = tk.Toplevel(self.root)
        new_root.title("Player Performance")
        new_root.geometry("800x850")

        # Bind the second window's close event to a custom function
        new_root.protocol("WM_DELETE_WINDOW", self.close_application)
        
        DisplayStats(new_root, df)

    def close_application(self):
        self.root.quit()  # Quit the Tkinter main loop
        self.root.destroy()  # Destroy the Tkinter root window

class DisplayStats:
    def __init__(self, root, df):
        self.root = root
        self.df = df
        self.create_ui()

    def create_ui(self):
        frame = tk.Frame(self.root)
        frame.pack(anchor="nw", padx=20, pady=20)

        title_label = tk.Label(frame, text="Averages over Last 25 Games:", font=("Helvetica", 12, "bold"))
        title_label.grid(row=0, column=0, sticky="w", pady=5, padx=5)

        avg_pts_25 = np.mean(pd.to_numeric(self.df.iloc[:, 6], errors="coerce"))
        avg_reb_25 = np.mean(pd.to_numeric(self.df.iloc[:, 7], errors="coerce"))
        avg_ast_25 = np.mean(pd.to_numeric(self.df.iloc[:, 8], errors="coerce"))

        stats = [("Points", avg_pts_25), ("Rebounds", avg_reb_25), ("Assists", avg_ast_25)]
        for i, (stat_name, avg_val) in enumerate(stats):
            label = tk.Label(frame, text=f"{stat_name}: {avg_val:.2f}", font=("Helvetica", 12), bg="gray", fg="white", padx=25, pady=5, relief="solid", bd=2, width=8, height=2)
            label.grid(row=i + 1, column=0, sticky="w", pady=5, padx=50)

        self.create_game_selection_buttons()
        self.create_plots()

        # Ensure button is added only once after window layout is completed
        self.root.after(100, self.add_return_button)

    def add_return_button(self):
        # Create and position the button after layout
        return_button = tk.Button(self.root, text="Return to Search", font=("Helvetica", 12), command=self.return_to_search, bg="#E0E0E0", fg="#333333", relief="flat", padx=10, pady=5)

        # Position the button at the bottom-right of the window
        return_button.place(relx=1.0, rely=1.0, x=-10, y=-10, anchor="se")

    def return_to_search(self):
        self.root.destroy()  # Close the new window
        root.deiconify()  # Reopen the main window

    def create_game_selection_buttons(self):
        box = tk.Frame(self.root)
        box.pack(fill='x')
        game_label = tk.Label(box, text="Games Select:", font=("Helvetica", 12), padx=25, pady=5, width=8, height=2)
        game_label.grid(row=0, column=0, pady=5, padx=20)

        for i in range(5, 30, 5):
            btn = tk.Button(box, text=str(i), bg="#E0E0E0", fg="#333333", relief="flat", padx=10, pady=5, width=8, height=2,
                            command=lambda n=i: self.update_plots(n))
            btn.grid(row=0, column=i//5, pady=5, padx=20)

    def create_plots(self):
        self.tabControl = ttk.Notebook(self.root)
        self.tabControl.pack(expand=1, fill="both",padx=20,pady=20)
        self.stat_tabs = ['Points', 'Rebounds', 'Assists']
        self.stats = ['PTS', 'REB', 'AST']

        self.plots = {}
        for stat in self.stats:
            tab = ttk.Frame(self.tabControl)
            fig = Figure(figsize=(6,4), dpi=100)
            plot = fig.add_subplot(111)
            canvas = FigureCanvasTkAgg(fig, master=tab)
            canvas.get_tk_widget().pack(padx=20,pady=20)
            self.tabControl.add(tab, text=stat)
            self.plots[stat] = (plot, canvas)

        self.update_plots(25)

    def update_plots(self, num_games):
        for i, stat in enumerate(self.stats):
            plot, canvas = self.plots[stat]
            plot.clear()

            stat_series = pd.to_numeric(self.df[stat][:num_games], errors="coerce").dropna()
            avg = self.df[stat][:25].mean()
            colors = ['red' if val < avg else 'green' for val in stat_series]
            names = range(1, len(stat_series) + 1)

            plot.bar(names, stat_series, color=colors)
            plot.set_title(f"{self.stat_tabs[i]} (Last {num_games} Games)")
            plot.axhline(avg, color='black', linestyle='dotted')
            canvas.draw()


root = tk.Tk()
app = PlayerStatsApp(root)
root.mainloop()
