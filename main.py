import logging
import traceback
from gui import InterviewAssistantGUI
from ai_service import AIService
from audio_service import AudioService

# Setup logging
logging.basicConfig(filename='app.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

if __name__ == "__main__":
    try:
        # Initialize Services
        ai_service = AIService()
        
        # Initialize GUI with injected services
        # We pass AudioService class or factory so GUI can instantiate it with callbacks
        app = InterviewAssistantGUI(ai_service, AudioService)
        
        app.mainloop()
        
    except Exception as e:
        logging.critical("App crashed!", exc_info=True)
        with open("error_log.txt", "w") as f:
            f.write(traceback.format_exc())
        print("App crashed! Check error_log.txt")
