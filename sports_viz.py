import tkinter as tk
from tkinter import ttk 
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from matplotlib.figure import Figure 
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

def build_colors(data_series, line=0):
    red='red'
    green='green'
    colors = []
    for i in data_series:
        if i < line: colors.append(red)
        else: colors.append(green)
        
    return colors

def find_player_stats():
    player_name = entry.get()  # Get the text from the entry widget
    player = player_name.split()
    
    # Check if there are exactly two names provided (first and last)
    if len(player) == 2:
        # Format URL with player's first and last name in lowercase
        url = f"https://www.statmuse.com/nba/ask/{player[0].lower()}-{player[1].lower()}-last-25-games"
    else: 
        print("Name in unexpected format")  
    # Send the request and get the page content
    response = requests.get(url)
    # Parse the page content with BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')
    # Find the table in the page (assuming the table has a specific class or id)
    table = soup.find('table')  # Example: table class

    # Extract table headers (column names)
    headers = [th.get_text().strip() for th in table.find_all('th')]
    # Extract table rows (data for each game)
    rows = []
    for tr in table.find_all('tr')[1:]:  # Skip the header row
        td = tr.find_all('td')
        row = [cell.get_text().strip() for cell in td]
        rows.append(row)
    # Convert to DataFrame
    df = pd.DataFrame(rows, columns = headers)
    games_total = len(df)
    df = df.iloc[:games_total-2,2:]
    df.iloc[:,0] = df.iloc[0,0].split()[0] +' ' + df.iloc[0,0].split()[1]
    df.iloc[:, 5:] = df.iloc[:, 5:].apply(pd.to_numeric, errors='coerce')
    print(df)
    root.destroy()  # Close the tkinter window
    open_new_window(df)  # Open the new blank window
    
def open_new_window(df):
    new_root = tk.Tk()
    new_root.title("Player Performance")
    new_root.geometry("800x800")

    # Create a frame to hold the content
    frame = tk.Frame(new_root)
    frame.pack(anchor="nw", padx=20, pady=20)

    # Add a label to the new window to verify it's opening
    title_label = tk.Label(frame, text="Averages over Last 25 Games:", font=("Helvetica", 12, "bold"))
    title_label.grid(row=0, column=0, sticky="w", pady=5, padx=5)

    #Choose padx for all 
    xpad = 50
    # Calculate averages for each column
    avg_pts_25 = np.mean(df.iloc[:, 6])
    label_pts = tk.Label(
        frame, 
        text=f"Points: {avg_pts_25:.2f}", 
        font=("Helvetica", 12), 
        bg="gray",  # Gray background for the box
        fg="white",    # White text color
        padx=25,       # Padding inside the box
        pady=5,       # Padding inside the box
        relief="solid", # Border around the box
        bd=2,          # Border width
        width=8,      # Set a fixed width for all boxes
        height=2       # Set a fixed height for all boxes
    )
    label_pts.grid(row=1, column=0, sticky="w", pady=5, padx=xpad)

    avg_reb_25 = np.mean(df.iloc[:, 7])
    label_reb = tk.Label(
        frame, 
        text=f"Rebounds: {avg_reb_25:.2f}", 
        font=("Helvetica", 12), 
        bg="gray",  # Gray background for the box
        fg="white",    # White text color
        padx=25,       # Padding inside the box
        pady=5,       # Padding inside the box
        relief="solid", # Border around the box
        bd=2,          # Border width
        width=8,      # Set a fixed width for all boxes
        height=2       # Set a fixed height for all boxes
    )
    label_reb.grid(row=2, column=0, sticky="w", pady=5, padx=xpad)

    avg_ast_25 = np.mean(df.iloc[:, 8])
    label_ast = tk.Label(
        frame, 
        text=f"Assists: {avg_ast_25:.2f}", 
        font=("Helvetica", 12), 
        bg="gray",  # Gray background for the box
        fg="white",    # White text color
        padx=25,       # Padding inside the box
        pady=5,       # Padding inside the box
        relief="solid", # Border around the box
        bd=2,          # Border width
        width=8,      # Set a fixed width for all boxes
        height=2       # Set a fixed height for all boxes
    )
    label_ast.grid(row=3, column=0, sticky="w", pady=5, padx=xpad)
    
    # this whole section really should be its own class that accepts the df and can handle the graphs
    # for now im jsut making what it looks like. will create a class later. The num games thing wont work rn
    box = tk.Frame(new_root)
    box.pack(fill='x')
    gameLbl = tk.Label(
        box, 
        text="Games Select:", 
        font=("Helvetica", 12), 
        padx=25,       # Padding inside the box
        pady=5,       # Padding inside the box
        width=8,      # Set a fixed width for all boxes
        height=2       # Set a fixed height for all boxes
    ) 
    gameLbl.grid(row=0, column=0, pady=5, padx=20)
    for i in range(5,30,5):
        btn = tk.Button(box, text=str(i), bg="#E0E0E0", fg="#333333", relief="flat", padx=10, pady=5, width=8, height=2)
        btn.grid(row=0, column=i//5, pady=5, padx=20)

    stat_plots = add_plots(new_root, df) # link these plot objects to a button command that swaps to different num of games
    # Start the main loop for the new window
    new_root.mainloop()

def add_plots(root, df):
    tabControl = ttk.Notebook(root) 
    stat_tabs = ['Points', 'Assists', 'Rebounds']
    stats = ['PTS', 'REB', 'AST']
    stat_plots = []
    for i in range(len(stats)):
        fig = Figure(figsize = (10,9), dpi = 100) 
        stat_plot = ttk.Frame(tabControl) 
        tabControl.add(stat_plot, text=stat_tabs[i])
        tabControl.pack(expand = 1, fill ="both") 
        # adding the subplot 
        pp = fig.add_subplot(111)  
        
        stat_series = df[stats[i]]
        avg = stat_series.mean()
        colors = build_colors(stat_series, avg)

        names = range(1,len(stat_series)+1)
        # plotting the graph 
        pp.bar(names, stat_series, color=colors) 
        pp.set_ylabel(stat_tabs[i], fontsize=10)
        pp.axhline(avg, color='black', ls='dotted')
  
        # creating the Tkinter canvas 
        # containing the Matplotlib figure 
        canvas = FigureCanvasTkAgg(fig, master=stat_plot)   
        canvas.draw() 
    
        # placing the canvas on the Tkinter window 
        canvas.get_tk_widget().pack() 
        stat_plots.append(pp)
        
    return stat_plots
    
# Create the main window
root = tk.Tk()
root.title("Player Search")
root.geometry("400x150")
root.configure(bg="#F0F0F0")  # Light grey background for a modern feel

# Use a custom font and add some styling
custom_font = ("Helvetica", 12)

# Frame for styling and positioning, centered vertically and horizontally
frame = tk.Frame(root, bg="#F0F0F0")
frame.pack(expand=True)  # Center the frame in the window

# Label with modern font and color
label = tk.Label(frame, text="Player:", font=custom_font, bg="#F0F0F0", fg="#333333")
label.grid(row=0, column=0, padx=(0, 10))

# Entry field with modern style
entry = tk.Entry(frame, width=20, font=custom_font, highlightbackground="#CCCCCC", highlightthickness=1, relief="flat")
entry.grid(row=0, column=1, padx=(0, 10))
entry.focus_set()  # Automatically focus on entry

# Placeholder text for entry
entry.insert(0, "Enter player name")
def on_entry_click(event):
    if entry.get() == "Enter player name":
        entry.delete(0, "end")  # Clear the placeholder text
entry.bind("<FocusIn>", on_entry_click)

# Modern, rounded search button with hover effect
def on_enter(event):
    search_button.config(bg="#333333", fg="#FFFFFF")

def on_leave(event):
    search_button.config(bg="#E0E0E0", fg="#333333")

search_button = tk.Button(frame, text="Search", font=custom_font, command=find_player_stats, bg="#E0E0E0", fg="#333333", relief="flat", padx=10, pady=5)
search_button.grid(row=0, column=2)
search_button.bind("<Enter>", on_enter)
search_button.bind("<Leave>", on_leave)

# Bind "Enter" key to initiate search
root.bind('<Return>', lambda event: find_player_stats())

# Run the application
root.mainloop()
