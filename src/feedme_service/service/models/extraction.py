# import standard modules
import os

# import project related modules
from src.feedme_service.settings import asr_model


class SpeechExtraction:

    def __init__(self):
        self.model = asr_model

    def extract(self, filename: str) -> str:
        output = asr_model.transcribe_file( # "output.wav")
            os.path.join(os.getcwd(), "tmp", filename)
        )
        return output
