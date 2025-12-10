# app.py
import customtkinter as ctk
import tkinter as tk
from tkinter import scrolledtext, messagebox
from typing import Dict, List, Tuple

# Custom files import karein
from ai_core import initialize_gemini_client, get_gemini_response, MODE_INSTRUCTIONS
from data_manager import save_history, CHAT_HISTORY

# --- CONFIGURATION AND GLOBAL SETUP ---
ctk.set_appearance_mode("Dark") 
ctk.set_default_color_theme("green") 

# --- Styling Variables ---
BG_MAIN = '#1a1a1a'       
BG_SIDEBAR = '#262626'    
COLOR_ACCENT = '#4CAF50'  

# Global UI state (chat_history ab data_manager se aayega)
current_chat_id: str | None = None
chat_counter: int = 1
current_mode: str = list(MODE_INSTRUCTIONS.keys())[0]

# --- 2. MAIN APPLICATION CLASS ---
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Instance variables (Global variables ko data_manager se link karna)
        global chat_counter, current_mode
        self.chat_history = CHAT_HISTORY # data_manager.CHAT_HISTORY se history load hogi
        self.chat_counter = len(self.chat_history) + 1 # Load kiye hue chats ke baad se counter shuru hoga
        self.current_mode = current_mode
        
        # --- API Client Initialization ---
        self.client = initialize_gemini_client() # ai_core se client initialize hoga
        
        self._setup_ui()
        
        # Agar history empty hai toh naya chat shuru karo, warna history load karo
        if not self.chat_history:
             self.start_new_chat()
        else:
             self.update_sidebar()
             # Last chat ko load karne ke liye
             last_chat_title = list(self.chat_history.keys())[-1]
             self.load_chat(last_chat_title)


    def _setup_ui(self):
        # ... (Same UI Setup as before - rows 2, 3, 4, 5 updated to include mode selector) ...
        self.title("📚 Student GPT - Final UI")
        self.geometry("1000x700")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.sidebar_frame = ctk.CTkFrame(self, width=250, corner_radius=0, fg_color=BG_SIDEBAR)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Student GPT", 
                                       font=ctk.CTkFont(size=20, weight="bold"), text_color=COLOR_ACCENT)
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.sidebar_button_1 = ctk.CTkButton(self.sidebar_frame, text="+ New Chat",
                                              command=self.start_new_chat, fg_color=COLOR_ACCENT,
                                              hover_color="#3c763d", font=ctk.CTkFont(size=13, weight="bold"))
        self.sidebar_button_1.grid(row=1, column=0, padx=20, pady=(10, 20), sticky="ew")

        # --- Mode Selector ---
        self.mode_label = ctk.CTkLabel(self.sidebar_frame, text="Choose Mode:", 
                                       font=ctk.CTkFont(size=10), text_color="#999999")
        self.mode_label.grid(row=2, column=0, padx=20, pady=(20, 0), sticky="w")
        
        self.mode_optionmenu = ctk.CTkOptionMenu(self.sidebar_frame, 
            values=list(MODE_INSTRUCTIONS.keys()),
            command=self.mode_change_handler, 
            fg_color="#3c3c3c", button_color=COLOR_ACCENT, dropdown_fg_color="#3c3c3c"
        )
        self.mode_optionmenu.set(self.current_mode) 
        self.mode_optionmenu.grid(row=3, column=0, padx=20, pady=(5, 10), sticky="ew")

        # Chat History Label (Row 4)
        self.history_label = ctk.CTkLabel(self.sidebar_frame, text="--- Chat History ---",
                                           font=ctk.CTkFont(size=10), text_color="#999999")
        self.history_label.grid(row=4, column=0, padx=20, pady=(10, 0), sticky="w") 
        
        # History Scrollable Frame (Row 5 - Expanding)
        self.history_scroll_frame = ctk.CTkScrollableFrame(self.sidebar_frame, label_text="", 
                                                           fg_color=BG_SIDEBAR, scrollbar_button_color=COLOR_ACCENT)
        self.history_scroll_frame.grid(row=5, column=0, padx=10, pady=(5, 10), sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(5, weight=1) 

        # --- Main Chat Area Frame (Right) ---
        self.main_chat_frame = ctk.CTkFrame(self, fg_color=BG_MAIN)
        self.main_chat_frame.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        self.main_chat_frame.grid_rowconfigure(0, weight=1)
        self.main_chat_frame.grid_columnconfigure(0, weight=1)

        # Output Area (Chat Display)
        self.output_area = scrolledtext.ScrolledText(self.main_chat_frame, wrap=tk.WORD, font=("Arial", 11), 
                                                     bg=BG_MAIN, fg='white', bd=0, relief=tk.FLAT,
                                                     padx=20, pady=20, highlightthickness=0)
        self.output_area.grid(row=0, column=0, sticky="nsew", padx=20, pady=(20, 10))
        self.output_area.tag_config('user_tag', font=("Arial", 11, "bold"), foreground='#FFFFFF')
        self.output_area.config(state=tk.DISABLED)

        # Input Frame and Entry
        self.input_frame = ctk.CTkFrame(self.main_chat_frame, fg_color=BG_MAIN)
        self.input_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 20))
        self.input_frame.grid_columnconfigure(0, weight=1)

        self.input_entry = scrolledtext.ScrolledText(self.input_frame, wrap=tk.WORD, height=3, 
                                                     font=("Arial", 10), bg='#3c3c3c', fg='white', 
                                                     bd=0, relief=tk.FLAT, padx=15, pady=15, highlightthickness=0)
        self.input_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10), pady=10)
        
        self.input_entry.bind('<Control-Return>', self.submit_question)
        self.input_entry.bind('<Command-Return>', self.submit_question) 
        self.input_entry.bind('<Return>', self.submit_question) 

        self.send_button = ctk.CTkButton(self.input_frame, text="Send", command=self.submit_question, 
                                         fg_color=COLOR_ACCENT, hover_color="#3c763d", 
                                         font=ctk.CTkFont(size=12, weight="bold"), width=80, height=50)
        self.send_button.grid(row=0, column=1, sticky="e", pady=10)


    # --- 3. CLASS METHODS FOR FUNCTIONALITY ---
    
    def mode_change_handler(self, new_mode_title: str):
        """Jab user mode badalta hai."""
        self.current_mode = new_mode_title 
        self.start_new_chat()
        messagebox.showinfo("Mode Changed", f"Student GPT mode successfully changed to: {new_mode_title}")

    def start_new_chat(self, event=None):
        """Naya chat shuru karta hai."""
        global current_chat_id 
        
        chat_title = f"New Chat {self.chat_counter}"
        self.chat_counter += 1
        current_chat_id = chat_title # Global ID update
        self.chat_history[current_chat_id] = []
        
        self.output_area.config(state=tk.NORMAL)
        self.output_area.delete("1.0", tk.END)
        self.output_area.insert(tk.END, f"--- Starting {chat_title} (Mode: {self.current_mode})---\n\n"
                               "Hello! I am Student GPT. Ask me anything about your studies!\n")
        self.output_area.config(state=tk.DISABLED)
        
        self.input_entry.delete("1.0", tk.END)
        self.update_sidebar()
        self.title(f"📚 Student GPT - {chat_title} ({self.current_mode})")

    def load_chat(self, chat_title: str):
        """Sidebar se chat chune jaane par us history ko load karta hai."""
        global current_chat_id
        if chat_title == current_chat_id:
            return
            
        current_chat_id = chat_title
        
        self.output_area.config(state=tk.NORMAL)
        self.output_area.delete("1.0", tk.END)
        
        for user_msg, bot_msg in self.chat_history[current_chat_id]:
            self.output_area.insert(tk.END, f"👤 **You:** {user_msg}\n", 'user_tag')
            self.output_area.insert(tk.END, bot_msg + "\n\n")
            
        self.output_area.config(state=tk.DISABLED)
        self.input_entry.delete("1.0", tk.END)
        self.title(f"📚 Student GPT - {chat_title} ({self.current_mode})")
        
    def update_sidebar(self):
        """Chat history scrollframe ko update karta hai."""
        for widget in self.history_scroll_frame.winfo_children():
            widget.destroy()

        titles = list(self.chat_history.keys())
        
        for title in titles:
            btn = ctk.CTkButton(self.history_scroll_frame, text=title, fg_color="transparent", 
                                text_color="white", hover_color="#3c3c3c", anchor="w",
                                corner_radius=5, command=lambda t=title: self.load_chat(t))
            btn.pack(fill="x", padx=5, pady=2)

    def submit_question(self, event=None):
        """Submit logic: Gemini API call aur history save karna."""
        global current_chat_id 
        
        user_query = self.input_entry.get("1.0", tk.END).strip()
        
        is_submission_key = event and event.keysym == 'Return' and (event.state & 0x4 or event.state & 0x8)

        if not user_query:
            if event and event.keysym == 'Return':
                return 'break'
            messagebox.showwarning("Warning", "Please enter your question first.")
            return
            
        if current_chat_id is None:
            self.start_new_chat()
            
        if not self.client:
             messagebox.showerror("API Error", "Gemini Client initialize nahi hua hai. Key set karein.")
             return 

        self.input_entry.delete("1.0", tk.END)
        
        # Output area mein user ka sawal aur Loading message
        self.output_area.config(state=tk.NORMAL)
        self.output_area.insert(tk.END, f"👤 **You:** {user_query}\n", 'user_tag')
        self.output_area.insert(tk.END, "🤖 **Student GPT:** *Generating response...*\n")
        self.output_area.config(state=tk.DISABLED)
        self.output_area.see(tk.END)
        
        # --- GEMINI CALL ---
        current_chat_history = self.chat_history.get(current_chat_id, [])
        
        bot_response = get_gemini_response(
            self.client, 
            current_chat_history, 
            user_query, 
            self.current_mode 
        )
        
        # Last line (loading message) ko delete karke naya response dalna
        self.output_area.config(state=tk.NORMAL)
        self.output_area.delete('end-2l', 'end')
        
        self.output_area.insert(tk.END, bot_response + "\n\n")
        self.output_area.config(state=tk.DISABLED)
        self.output_area.see(tk.END)
        
        # Chat history update karna aur save karna
        self.chat_history[current_chat_id].append((user_query, bot_response))
        save_history(self.chat_history) # History save ho gayi!
        
        # Title update karna
        if len(self.chat_history[current_chat_id]) == 1 and "New Chat" in current_chat_id:
            new_title = user_query[:25].replace('\n', ' ') + '...' if len(user_query) > 25 else user_query
            old_title = current_chat_id
            current_chat_id = new_title 
            self.chat_history[new_title] = self.chat_history.pop(old_title)
            
            # Global current_chat_id ko bhi naye title se update karna
            self.update_sidebar()
            self.title(f"📚 Student GPT - {new_title} ({self.current_mode})")
        
        if event and is_submission_key:
            return 'break'

# --- 4. START THE APPLICATION ---
if __name__ == "__main__":
    app = App()
    app.mainloop()