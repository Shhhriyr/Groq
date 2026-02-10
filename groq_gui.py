import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from groq import Groq
import threading
import os
import base64
import requests
from pathlib import Path
from PIL import Image, ImageDraw

class GroqChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Groq AI Chat Pro")
        self.root.geometry("700x900")
        
        # تعریف رنگ‌های Groq (Black & Orange)
        self.colors = {
            "bg": "#000000",        # مشکی مطلق
            "fg": "#ffffff",        # سفید برای متون
            "secondary_bg": "#111111", # مشکی کمی روشن‌تر برای فریم‌ها
            "border": "#f55036",    # نارنجی Groq برای حاشیه‌ها
            "accent": "#f55036",    # نارنجی Groq برای دکمه‌ها و المان‌های تاکیدی
            "accent_fg": "#ffffff", # متن دکمه‌ها سفید
            "input_bg": "#1a1a1a"   # پس‌زمینه ورودی‌ها
        }

        self.root.configure(bg=self.colors["bg"])
        
        # تلاش برای بارگذاری آیکون
        try:
            if os.path.exists("favicon.ico"):
                self.root.iconbitmap("favicon.ico")
        except:
            pass

        # مدل‌های در دسترس (در ابتدا خالی، با Fetch پر می‌شود)
        self.models = []
        
        self.chat_history = []
        self.selected_image_path = None
        self.create_icon_if_missing()
        self.setup_styles()
        self.setup_ui()

    def create_icon_if_missing(self):
        """اگر آیکون وجود ندارد، یک آیکون ساده می‌سازد"""
        if not os.path.exists("favicon.ico"):
            try:
                # ایجاد یک تصویر کوچک 64x64 با پس‌زمینه تیره و حرف G سفید
                img = Image.new('RGB', (64, 64), color='#121212')
                d = ImageDraw.Draw(img)
                # رسم یک دایره ساده یا حرف G (بدون نیاز به فونت خاص)
                d.ellipse([10, 10, 54, 54], outline="#ffffff", width=3)
                d.text((22, 18), "G", fill="#ffffff") # استفاده از فونت پیش‌فرض
                img.save("favicon.ico")
            except:
                pass

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam') # استفاده از تم clam برای قابلیت شخصی‌سازی بیشتر

        # استایل فریم‌ها
        style.configure("TFrame", background=self.colors["bg"])
        style.configure("TLabelframe", background=self.colors["bg"], foreground=self.colors["fg"])
        style.configure("TLabelframe.Label", background=self.colors["bg"], foreground=self.colors["fg"], font=("Tahoma", 9, "bold"))

        # استایل دکمه‌ها
        style.configure("TButton", 
                        background=self.colors["accent"], 
                        foreground=self.colors["accent_fg"], 
                        borderwidth=0, 
                        focusthickness=0, 
                        padding=5)
        style.map("TButton", 
                  background=[('active', '#d43f2a'), ('pressed', '#b03423')],
                  foreground=[('active', '#ffffff')])

        # استایل ورودی‌ها و کمبوباکس
        style.configure("TEntry", fieldbackground=self.colors["input_bg"], foreground=self.colors["fg"], insertcolor=self.colors["fg"])
        
        # تنظیمات اختصاصی برای دراپ‌داون (Combobox)
        style.configure("TCombobox", 
                        fieldbackground=self.colors["input_bg"], 
                        foreground=self.colors["fg"],
                        background=self.colors["accent"])
        
        style.map("TCombobox",
                  fieldbackground=[('readonly', self.colors["input_bg"])],
                  foreground=[('readonly', self.colors["fg"])])
        
        # تنظیمات لیست بازشو (پاپ‌آپ)
        self.root.option_add("*TCombobox*Listbox.foreground", self.colors["fg"])
        self.root.option_add("*TCombobox*Listbox.background", self.colors["input_bg"])
        self.root.option_add("*TCombobox*Listbox.selectForeground", self.colors["accent_fg"])
        self.root.option_add("*TCombobox*Listbox.selectBackground", self.colors["accent"])
        
        # استایل چک‌باکس
        style.configure("TCheckbutton", background=self.colors["bg"], foreground=self.colors["fg"])

    def setup_ui(self):
        # Configuration Frame (Top)
        config_frame = ttk.LabelFrame(self.root, text=" Settings & Model ", padding=15)
        config_frame.pack(fill="x", padx=20, pady=10)

        # API Key
        ttk.Label(config_frame, text="Groq API Key:", background=self.colors["bg"]).grid(row=0, column=0, sticky="w", pady=5)
        self.api_key_entry = ttk.Entry(config_frame, show="*", width=40)
        self.api_key_entry.grid(row=0, column=1, padx=10, pady=5)

        self.paste_button = ttk.Button(config_frame, text="Paste", command=self.paste_api_key)
        self.paste_button.grid(row=0, column=2, padx=5, pady=5)

        self.fetch_button = ttk.Button(config_frame, text="Fetch Models", command=self.fetch_models)
        self.fetch_button.grid(row=0, column=3, padx=5, pady=5)

        # Model Selection Dropdown
        ttk.Label(config_frame, text="Select Model:", background=self.colors["bg"]).grid(row=1, column=0, sticky="w", pady=5)
        self.model_var = tk.StringVar(value=self.models[0] if self.models else "")
        self.model_dropdown = ttk.Combobox(config_frame, textvariable=self.model_var, values=self.models, state="readonly", width=47)
        self.model_dropdown.grid(row=1, column=1, columnspan=3, padx=10, pady=5, sticky="w")
        self.model_var.trace_add("write", lambda *args: self.update_media_buttons_visibility())
        
        # Memory Capability
        self.memory_var = tk.BooleanVar(value=True)
        self.memory_check = ttk.Checkbutton(config_frame, text="Enable Memory (Send last 3 message pairs)", variable=self.memory_var)
        self.memory_check.grid(row=2, column=1, columnspan=2, sticky="w", padx=10, pady=5)

        # System Prompt Frame
        system_frame = ttk.LabelFrame(self.root, text=" System Prompt (Always Sent) ", padding=15)
        system_frame.pack(fill="x", padx=20, pady=5)
        
        self.system_prompt_text = tk.Text(system_frame, height=3, font=("Tahoma", 9), 
                                        bg=self.colors["secondary_bg"], fg=self.colors["fg"],
                                        insertbackground=self.colors["fg"], relief="flat", padx=5, pady=5)
        self.system_prompt_text.pack(fill="x")
        self.system_prompt_text.insert(tk.END, "You are a helpful assistant.")

        # Chat Frame (Middle)
        chat_frame = ttk.LabelFrame(self.root, text=" Chat ", padding=15)
        chat_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.chat_display = scrolledtext.ScrolledText(chat_frame, wrap=tk.WORD, state="disabled", 
                                                    font=("Tahoma", 10), bg=self.colors["secondary_bg"], 
                                                    fg=self.colors["fg"], relief="flat", padx=10, pady=10)
        self.chat_display.pack(fill="both", expand=True)

        # Input Frame (Bottom)
        input_frame = ttk.Frame(self.root, padding=20)
        input_frame.pack(fill="x")

        self.user_input = tk.Entry(input_frame, font=("Tahoma", 11), 
                                  bg=self.colors["secondary_bg"], fg=self.colors["fg"],
                                  insertbackground=self.colors["fg"], relief="flat", bd=10)
        self.user_input.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.user_input.bind("<Return>", lambda e: self.send_message())

        self.send_button = ttk.Button(input_frame, text="Send", command=self.send_message)
        self.send_button.pack(side="right")
        
        self.clear_button = ttk.Button(input_frame, text="Clear History", command=self.clear_history)
        self.clear_button.pack(side="right", padx=10)

        self.image_button = ttk.Button(input_frame, text="Upload Image (Vision)", command=self.select_image)
        self.image_button.pack(side="right")

        # Initial media button visibility
        self.update_media_buttons_visibility()

    def update_media_buttons_visibility(self):
        selected_model = self.model_var.get().lower()
        
        # Vision support (Llama models)
        if "llama" in selected_model:
            self.image_button.pack(side="right")
        else:
            self.image_button.pack_forget()

    def select_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.webp")]
        )
        if file_path:
            self.selected_image_path = file_path
            self.append_to_chat("System", f"Image selected: {os.path.basename(file_path)}")

    def encode_image(self, image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def paste_api_key(self):
        try:
            clipboard_content = self.root.clipboard_get()
            self.api_key_entry.delete(0, tk.END)
            self.api_key_entry.insert(0, clipboard_content)
        except tk.TclError:
            messagebox.showwarning("Warning", "Clipboard is empty.")

    def fetch_models(self):
        api_key = self.api_key_entry.get().strip()
        if not api_key:
            messagebox.showerror("Error", "Please enter the API Key first.")
            return

        def do_fetch():
            try:
                url = "https://api.groq.com/openai/v1/models"
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    model_list = [model['id'] for model in data.get('data', [])]
                    # مرتب‌سازی مدل‌ها برای ظاهر بهتر
                    model_list.sort()
                    
                    if model_list:
                        self.models = model_list
                        self.root.after(0, self.update_dropdown_values)
                        self.append_to_chat("System", f"Successfully fetched {len(model_list)} models.")
                    else:
                        messagebox.showwarning("Warning", "No models found in the response.")
                else:
                    messagebox.showerror("Error", f"Failed to fetch models. Status: {response.status_code}")
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {str(e)}")

        threading.Thread(target=do_fetch, daemon=True).start()

    def update_dropdown_values(self):
        self.model_dropdown['values'] = self.models
        if self.models:
            self.model_var.set(self.models[0])
        self.update_media_buttons_visibility()

    def clear_history(self):
        self.chat_history = []
        self.chat_display.config(state="normal")
        self.chat_display.delete(1.0, tk.END)
        self.chat_display.config(state="disabled")
        self.append_to_chat("System", "Chat history cleared.")

    def append_to_chat(self, sender, message):
        self.chat_display.config(state="normal")
        self.chat_display.insert(tk.END, f"{sender}: {message}\n\n")
        self.chat_display.see(tk.END)
        self.chat_display.config(state="disabled")

    def send_message(self):
        api_key = self.api_key_entry.get().strip()
        user_text = self.user_input.get().strip()
        selected_model = self.model_var.get()
        system_prompt = self.system_prompt_text.get(1.0, tk.END).strip()

        if not api_key:
            messagebox.showerror("Error", "Please enter the API Key.")
            return

        if not selected_model:
            messagebox.showerror("Error", "Please fetch and select a model first.")
            return
        
        if not user_text and not self.selected_image_path:
            return

        if user_text:
            self.append_to_chat("You", user_text)
        elif self.selected_image_path:
            self.append_to_chat("You", "[Image Only]")

        self.user_input.delete(0, tk.END)
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        if self.memory_var.get():
            last_messages = self.chat_history[-6:] 
            messages.extend(last_messages)
        
        # Prepare message content (Text or Text + Image)
        if self.selected_image_path and "llama" in selected_model.lower():
            try:
                base64_image = self.encode_image(self.selected_image_path)
                content = []
                if user_text:
                    content.append({"type": "text", "text": user_text})
                
                content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                })
                self.selected_image_path = None # Reset after use
            except Exception as e:
                messagebox.showerror("Error", f"Error processing image: {str(e)}")
                return
        else:
            content = user_text
            if self.selected_image_path:
                self.append_to_chat("System", "Warning: This model does not support vision. Image was not sent.")
                self.selected_image_path = None

        messages.append({"role": "user", "content": content})
        
        # Save history
        history_content = user_text if isinstance(content, list) else content
        self.chat_history.append({"role": "user", "content": history_content})

        threading.Thread(target=self.get_groq_response, args=(api_key, selected_model, messages), daemon=True).start()

    def get_groq_response(self, api_key, model, messages):
        try:
            client = Groq(api_key=api_key)
            completion = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=1,
                max_completion_tokens=1024,
                top_p=1,
                stream=True,
                stop=None,
            )

            self.root.after(0, lambda: self.append_to_chat("Groq", ""))
            
            full_response = ""
            for chunk in completion:
                content = chunk.choices[0].delta.content or ""
                full_response += content
                self.root.after(0, self.update_last_message, content)
            
            self.chat_history.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"An error occurred: {str(e)}"))

    def update_last_message(self, new_content):
        self.chat_display.config(state="normal")
        self.chat_display.insert(tk.END, new_content)
        self.chat_display.see(tk.END)
        self.chat_display.config(state="disabled")

if __name__ == "__main__":
    root = tk.Tk()
    app = GroqChatApp(root)
    root.mainloop()
