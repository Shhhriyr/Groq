from groq import Groq
import getpass

def main():
    # دریافت API Key از کاربر (استفاده از getpass برای امنیت بیشتر)
    api_key = getpass.getpass("لطفاً API Key خود را وارد کنید: ")
    
    if not api_key:
        print("API Key نمی‌تواند خالی باشد.")
        return

    # لیست مدل‌های در دسترس
    models = {
        "1": "meta-llama/llama-4-maverick-17b-128e-instruct",
        "2": "meta-llama/llama-4-scout-17b-16e-instruct",
        "3": "qwen/qwen3-32b",
        "4": "moonshotai/kimi-k2-instruct-0905"
    }

    print("\nلطفاً مدل مورد نظر خود را انتخاب کنید:")
    for key, model_name in models.items():
        print(f"{key}. {model_name}")
    
    choice = input("\nشماره مدل (پیش‌فرض 1): ").strip() or "1"
    
    selected_model = models.get(choice)
    if not selected_model:
        print("انتخاب نامعتبر است. از مدل پیش‌فرض استفاده می‌شود.")
        selected_model = models["1"]

    try:
        # مقداردهی اولیه کلاینت Groq
        client = Groq(api_key=api_key)
        
        print(f"\n--- برنامه چت با Groq ({selected_model}) شروع شد ---")
        print("برای خروج 'exit' یا 'quit' را تایپ کنید.\n")

        while True:
            user_input = input("شما: ")
            
            if user_input.lower() in ['exit', 'quit']:
                break
            
            if not user_input.strip():
                continue

            # ایجاد درخواست چت
            completion = client.chat.completions.create(
                model=selected_model,
                messages=[
                    {
                        "role": "user",
                        "content": user_input
                    }
                ],
                temperature=1,
                max_completion_tokens=1024,
                top_p=1,
                stream=True,
                stop=None
            )

            print("Groq: ", end="", flush=True)
            for chunk in completion:
                content = chunk.choices[0].delta.content or ""
                print(content, end="", flush=True)
            print("\n")

    except Exception as e:
        print(f"خطایی رخ داد: {e}")

if __name__ == "__main__":
    main()
