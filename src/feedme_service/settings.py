# import standard modules
import os
import json

# import third party modules
import torch
from dotenv import load_dotenv
from fastapi.templating import Jinja2Templates
from speechbrain.pretrained import EncoderDecoderASR

# import project related modules
from feedme_service.ner.model.LSTM import LSTMTagger
from feedme_service.ner.utils import tag_to_ix, ix_to_tag


load_dotenv()
template_path = os.path.join(os.getcwd(), "src/feedme_service/service/templates")
templates = Jinja2Templates(directory=template_path)

asr_model = EncoderDecoderASR.from_hparams(
    source="jfreiwa/asr-crdnn-german",
    savedir="pretrained_models/asr-crdnn-german"
)


word_to_ix = json.load(open(os.path.join(os.getcwd(), "src/feedme_service/ner", "word_to_ix.json"), "r"))

ner_model = LSTMTagger(
    64,
    64,
    len(word_to_ix),
    len(tag_to_ix)
)
ner_model.load_state_dict(
    torch.load(os.path.join(os.getcwd(), "src/feedme_service/ner/model/output", "lstm.pth"))
)