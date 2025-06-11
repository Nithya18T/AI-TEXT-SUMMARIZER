import tkinter as tk
from tkinter import messagebox, scrolledtext, filedialog
from transformers import pipeline
from fpdf import FPDF
import re
import yake
import textstat
import pyttsx3

# Pipelines
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
sentiment_analyzer = pipeline("sentiment-analysis")
ner = pipeline("ner", aggregation_strategy="simple")

# Initialize text-to-speech engine
tts_engine = pyttsx3.init()

# GUI setup
root = tk.Tk()
root.title("AI Text Summarizer")
root.geometry("1000x850")

font_label = ("Arial", 14)
font_text = ("Arial", 12)

# Utility to chunk text into ~max_chunk_size words chunks
def chunk_text(text, max_chunk_size=1000):
    words = text.split()
    for i in range(0, len(words), max_chunk_size):
        yield ' '.join(words[i:i + max_chunk_size])

# Update word count and other stats
def update_word_count(event=None):
    text = text_input.get("1.0", tk.END)
    words = text.split()
    chars = len(text)
    sentences = len(re.findall(r'[.!?]+', text))
    reading_time = round(len(words) / 200, 2)
    word_count_var.set(f"Words: {len(words)} | Sentences: {sentences} | Chars: {chars} | Est. Read Time: {reading_time} min")

# Summarize text safely with chunking and length adjustments
def summarize_text():
    input_text = text_input.get("1.0", tk.END).strip()
    min_len = min_length_var.get()
    max_len = max_length_var.get()

    if len(input_text.split()) < 30:
        messagebox.showwarning("Too Short", "Please enter at least 30 words.")
        return
    if min_len <= 0 or max_len <= 0 or min_len > max_len:
        messagebox.showwarning("Invalid Length", "Please ensure valid min and max length values.")
        return
    if max_len > 1000:
        messagebox.showwarning("Max Length Too Large", "Please enter max length <= 1000 per chunk.")
        return

    summarize_button.config(state=tk.DISABLED)
    root.update()

    try:
        summaries = []
        for chunk in chunk_text(input_text, max_chunk_size=1000):
            chunk_words = chunk.split()
            # Adjust min and max lengths for chunk size
            chunk_min_len = min(min_len, len(chunk_words))
            chunk_max_len = min(max_len, len(chunk_words))
            if chunk_min_len == 0 or chunk_max_len == 0:
                continue  # Skip empty chunk
            # Summarize chunk safely
            try:
                summary = summarizer(chunk, max_length=chunk_max_len, min_length=chunk_min_len, do_sample=False)
                summaries.append(summary[0]['summary_text'])
            except Exception:
                # fallback: just use chunk if summarization fails
                summaries.append(chunk)
        final_summary = ' '.join(summaries)
        output_summary.delete("1.0", tk.END)
        output_summary.insert(tk.END, final_summary)
    except Exception as e:
        messagebox.showerror("Error", str(e))
    finally:
        summarize_button.config(state=tk.NORMAL)

# Speak out the summary text
def speak_summary():
    summary = output_summary.get("1.0", tk.END).strip()
    if not summary:
        messagebox.showinfo("Empty Summary", "There is no summary to speak.")
        return
    tts_engine.say(summary)
    tts_engine.runAndWait()

# Analyze sentiment
def analyze_sentiment():
    text = text_input.get("1.0", tk.END).strip()
    if not text:
        messagebox.showinfo("Empty Text", "Please enter some text to analyze.")
        return
    result = sentiment_analyzer(text[:512])[0]
    messagebox.showinfo("Sentiment Analysis", f"Sentiment: {result['label']} (Score: {round(result['score'], 2)})")

# Extract named entities
def extract_entities():
    text = text_input.get("1.0", tk.END).strip()
    if not text:
        messagebox.showinfo("Empty Text", "Enter text to extract entities.")
        return
    entities = ner(text[:512])
    entity_summary = "\n".join(f"{e['entity_group']}: {e['word']} (Score: {round(e['score'], 2)})" for e in entities)
    messagebox.showinfo("Named Entities", entity_summary or "No entities found.")

# Extract keywords using YAKE
def extract_keywords():
    text = text_input.get("1.0", tk.END).strip()
    if not text:
        messagebox.showinfo("Empty Text", "Enter text to extract keywords.")
        return
    kw_extractor = yake.KeywordExtractor(top=10, stopwords=None)
    keywords = kw_extractor.extract_keywords(text)
    result = "\n".join(f"{kw[0]} (score: {round(kw[1], 3)})" for kw in keywords)
    messagebox.showinfo("Extracted Keywords", result)

# Readability score
def readability_score():
    text = text_input.get("1.0", tk.END).strip()
    if not text:
        messagebox.showinfo("Empty Text", "Enter text to analyze readability.")
        return
    score = textstat.flesch_reading_ease(text)
    grade = textstat.text_standard(text)
    messagebox.showinfo("Readability Score", f"Flesch Score: {score:.2f}\nReading Level: {grade}")

# Save summary to txt file
def save_summary():
    summary_text = output_summary.get("1.0", tk.END).strip()
    if not summary_text:
        messagebox.showinfo("Nothing to Save", "No summary to save.")
        return
    filepath = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
    if filepath:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(summary_text)
        messagebox.showinfo("Saved", "Summary saved successfully!")

# Save summary as PDF
def save_as_pdf():
    summary = output_summary.get("1.0", tk.END).strip()
    if not summary:
        messagebox.showinfo("Empty", "No summary to save.")
        return
    filepath = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
    if filepath:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        for line in summary.split('\n'):
            pdf.multi_cell(0, 10, line)
        pdf.output(filepath)
        messagebox.showinfo("Saved", "PDF saved successfully.")

# Clear input and output
def clear_all():
    text_input.delete("1.0", tk.END)
    output_summary.delete("1.0", tk.END)
    update_word_count()

# Load text file into input
def load_text_file():
    filepath = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
    if filepath:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            text_input.delete("1.0", tk.END)
            text_input.insert(tk.END, content)
            update_word_count()

# Copy summary to clipboard
def copy_summary():
    summary_text = output_summary.get("1.0", tk.END).strip()
    if summary_text:
        root.clipboard_clear()
        root.clipboard_append(summary_text)
        messagebox.showinfo("Copied", "Summary copied to clipboard!")

# Widgets
word_count_var = tk.StringVar(value="Words: 0 | Sentences: 0 | Chars: 0 | Est. Read Time: 0 min")

# Input
tk.Label(root, text="Enter Text to Summarize:", font=font_label).pack(pady=10)
text_input = scrolledtext.ScrolledText(root, height=10, wrap=tk.WORD, font=font_text)
text_input.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
text_input.bind("<KeyRelease>", update_word_count)

# Stats
tk.Label(root, textvariable=word_count_var, font=("Arial", 10), fg="gray").pack(anchor='e', padx=12)

# Length Controls
length_frame = tk.Frame(root)
length_frame.pack(pady=10)
tk.Label(length_frame, text="Min Length:", font=("Arial", 12)).pack(side=tk.LEFT)
min_length_var = tk.IntVar(value=30)
tk.Entry(length_frame, textvariable=min_length_var, width=5).pack(side=tk.LEFT, padx=5)
tk.Label(length_frame, text="Max Length:", font=("Arial", 12)).pack(side=tk.LEFT, padx=10)
max_length_var = tk.IntVar(value=130)
tk.Entry(length_frame, textvariable=max_length_var, width=5).pack(side=tk.LEFT)

# Buttons Frame
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

summarize_button = tk.Button(button_frame, text="Summarize", command=summarize_text, font=font_text, bg="#c4f0c5", width=15)
summarize_button.pack(side=tk.LEFT, padx=5)

tk.Button(button_frame, text="Speak Summary", command=speak_summary, font=font_text, bg="#d1f0ff", width=15).pack(side=tk.LEFT, padx=5)
tk.Button(button_frame, text="Analyze Sentiment", command=analyze_sentiment, font=font_text, bg="#ffcccc", width=15).pack(side=tk.LEFT, padx=5)
tk.Button(button_frame, text="Extract Entities", command=extract_entities, font=font_text, bg="#ffdfba", width=15).pack(side=tk.LEFT, padx=5)
tk.Button(button_frame, text="Extract Keywords", command=extract_keywords, font=font_text, bg="#d4eaff", width=15).pack(side=tk.LEFT, padx=5)
tk.Button(button_frame, text="Readability Score", command=readability_score, font=font_text, bg="#e0d4ff", width=15).pack(side=tk.LEFT, padx=5)

# Second Buttons Frame
button_frame2 = tk.Frame(root)
button_frame2.pack(pady=10)

tk.Button(button_frame2, text="Save Summary", command=save_summary, font=font_text, bg="#b2d9ff", width=15).pack(side=tk.LEFT, padx=5)
tk.Button(button_frame2, text="Save as PDF", command=save_as_pdf, font=font_text, bg="#f7d6e0", width=15).pack(side=tk.LEFT, padx=5)
tk.Button(button_frame2, text="Clear All", command=clear_all, font=font_text, bg="#f0f0f0", width=15).pack(side=tk.LEFT, padx=5)
tk.Button(button_frame2, text="Load Text File", command=load_text_file, font=font_text, bg="#d1ffd6", width=15).pack(side=tk.LEFT, padx=5)
tk.Button(button_frame2, text="Copy Summary", command=copy_summary, font=font_text, bg="#fff4b2", width=15).pack(side=tk.LEFT, padx=5)

# Output summary
tk.Label(root, text="Summary Output:", font=font_label).pack(pady=10)
output_summary = scrolledtext.ScrolledText(root, height=10, wrap=tk.WORD, font=font_text)
output_summary.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

root.mainloop()