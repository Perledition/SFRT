import os
import torch
import json
import pandas as pd
import torch.nn as nn
import torch.optim as optim
from model.LSTM import LSTMTagger
from utils import tag_to_ix, ix_to_tag, prepare_sequence

# ftg = FoodTextGenerator()
# ftg.create(n=1000)

def train_ner():
    df = pd.read_csv(os.path.join(
        os.getcwd(),
        "datagenerator",
        "output",
        "2023-01-07",
        "train.csv"
    ), sep=";")

    sentences = df.sentences.tolist()
    tags = df.tags.tolist()

    training_data = list()
    for i in range(len(sentences)):
        training_data.append(
            (sentences[i].split(" "), tags[i].split(" "))
        )

    word_to_ix = {}
    # For each words-list (sentence) and tags-list in each tuple of training_data
    for sent, tags in training_data:
        for word in sent:
            if word not in word_to_ix:  # word has not been assigned an index yet
                word_to_ix[word] = len(word_to_ix)  # Assign each word with a unique index

    with open(os.path.join(os.getcwd(), "word_to_ix.json"), "w") as word_ix_file:
        json.dump(word_to_ix, word_ix_file)

    EMBEDDING_DIM = 64
    HIDDEN_DIM = 64

    model = LSTMTagger(
        EMBEDDING_DIM,
        HIDDEN_DIM,
        len(word_to_ix),
        len(tag_to_ix)
    )

    loss_function = nn.NLLLoss()
    optimizer = optim.SGD(model.parameters(), lr=.1)

    # See what the scores are before training
    # Note that element i, j of the output is the score for tag j for ward i
    # Here we don't need to train, so the code is wrapped in torch.no_grad()
    with torch.no_grad():
        inputs = prepare_sequence(training_data[0][0], word_to_ix)
        tag_scores = model(inputs)
        # print(tag_scores)

    for epoch in range(50):
        for sentence, tags in training_data:
            # Step 1. Remember that pytorch accumulates gradients
            # we need to clear them out before each instance
            model.zero_grad()

            # Step 2. Get our inputs ready for the network, that is, turn them into
            # Tensors of word indices
            sentence_in = prepare_sequence(sentence, word_to_ix)
            targets = prepare_sequence(tags, tag_to_ix)

            # Step 3. Run our forward pass.
            tag_scores = model.forward(sentence_in)

            # Step 4. Compute the loss gradients, and update the parameters by
            # calling optimizer.step()
            loss = loss_function(tag_scores, targets)
            loss.backward()
            optimizer.step()
        print(f'epoch {epoch}: loss: {loss}')

    torch.save(model.state_dict(), os.path.join(os.getcwd(), "model", "output", "lstm.pth"))

