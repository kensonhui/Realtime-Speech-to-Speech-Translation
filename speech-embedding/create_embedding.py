import torchaudio
import torch
from speechbrain.pretrained import EncoderClassifier

# file_paths = ['spk2_snt1.wav', 'spk2_snt2.wav', 'spk2_snt3.wav', 'spk2_snt4.wav', 'spk2_snt5.wav']
# file_paths = ['spk1_snt1.wav', 'spk1_snt2.wav', 'spk1_snt3.wav', 'spk1_snt4.wav', 'spk1_snt5.wav']

file_paths = ['i_hate_men.wav']
classifier = EncoderClassifier.from_hparams(source="speechbrain/spkrec-ecapa-voxceleb", savedir="pretrained_models/spkrec-xvect-voxceleb")
all_embeddings = []

for file_path in file_paths:
    signal, fs = torchaudio.load(file_path)
    embedding = classifier.encode_batch(signal)
    all_embeddings.append(embedding)

combined_embedding = torch.mean(torch.stack(all_embeddings), dim=0)

torch.save(combined_embedding, 'kenson_embeddings.pt')
print(combined_embedding.shape)
