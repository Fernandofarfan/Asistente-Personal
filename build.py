import PyInstaller.__main__
import customtkinter
import os

# Get customtkinter path to include its data files
ctk_path = os.path.dirname(customtkinter.__file__)

PyInstaller.__main__.run([
    'main.py',
    '--name=InterviewAssistant',
    '--onefile',
    '--noconsole',
    f'--add-data={ctk_path};customtkinter',
    '--hidden-import=google.generativeai',
    '--hidden-import=pyperclip',
    '--hidden-import=PIL',
    '--hidden-import=PIL._tkinter_finder',
    '--icon=NONE',  # Could add an icon here if we had one
    '--clean',
])
