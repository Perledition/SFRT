
# import standard modules
import os
from io import StringIO

# import third party modules
import pandas as pd
from fastapi import APIRouter, HTTPException, File, UploadFile, Request

# import project related modules
from feedme_service.settings import templates
from feedme_service.ner.predict import predict
from feedme_service.ner.utils import correct_spelling, convert_text_to_number
from feedme_service.service.models.extraction import SpeechExtraction
from pydub import AudioSegment


router = APIRouter(
    prefix="/api/v1/record",
    tags=["record"],
)


@router.post("/voicemail")
def upload(request: Request, file: UploadFile = File(...)):
    # file_type = file.filename.split(".")[-1].lower()
    file_name = ".".join(file.filename.split(".")[:-1]).lower()

    # webm_path = os.path.join(os.getcwd(), "tmp", file.filename)
    wav_path = os.path.join(os.getcwd(), "tmp", f'{file_name}.wav')

    webm_file = AudioSegment.from_file(file.file, format="webm")
    webm_file.export(wav_path, format="wav")

    se = SpeechExtraction()
    extract = se.extract(wav_path)

    print("voice", extract)
    print("corrected", correct_spelling(extract))
    extract = correct_spelling(extract)
    extract = convert_text_to_number(extract)
    extract = predict(extract)

    try:
        os.remove(wav_path)
    except Exception as e:
        print('remove wav', e)
        pass

    return {"extract": extract.to_html(index=False)}

