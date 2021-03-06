import librosa
import soundfile
import os, glob, pickle
import numpy as np
import matplotlib.pyplot as plt
from tensorflow.keras.layers import Input
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import BatchNormalization
from tensorflow.keras.layers import LeakyReLU
from tensorflow.keras.models import Model
from tensorflow.keras.utils import plot_model
from sklearn.model_selection import train_test_split

def extract_feature(file_name, mfcc, chroma, mel):
    with soundfile.SoundFile(file_name) as sound_file:
        X = sound_file.read(dtype="float32")
        sample_rate=sound_file.samplerate
        if chroma:
            stft=np.abs(librosa.stft(X))
        result=np.array([])
        if mfcc:
            mfccs=np.mean(librosa.feature.mfcc(y=X, sr=sample_rate, n_mfcc=40).T, axis=0)
            result=np.hstack((result, mfccs))
        if chroma:
            chroma=np.mean(librosa.feature.chroma_stft(S=stft, sr=sample_rate).T,axis=0)
            result=np.hstack((result, chroma))
        if mel:
            mel=np.mean(librosa.feature.melspectrogram(X, sr=sample_rate).T,axis=0)
            result=np.hstack((result, mel))
    return result
emotions={
  '01':'neutral',
  '02':'calm',
  '03':'happy',
  '04':'sad',
  '05':'angry',
  '06':'fearful',
  '07':'disgust',
  '08':'surprised'
}
observed_emotions=['calm', 'happy', 'sad' ,'angry']
def load_data(ts):
    x,y=[],[]
    for file in glob.glob("F:\\python\\dl programs\\SP\\DATA\\Actor_*\\*.wav"):
        file_name=os.path.basename(file)
        emotion=emotions[file_name.split("-")[2]]
        print(emotion)
        if emotion in observed_emotions:
            feature=extract_feature(file, mfcc=True, chroma=True, mel=True)
            x.append(feature)
            y.append(emotion)
    y=label_encoder(y)
    return train_test_split(np.array(x), y, test_size=ts ,random_state=9)

def label_encoder(y):
    from sklearn.preprocessing import LabelEncoder
    le=LabelEncoder()
    y=le.fit_transform(y)
    return y
def Mod(X_train, X_test, y_train, y_test,n_inputs):
    # define encoder
    visible = Input(shape=(n_inputs,))
   # encoder level 1
    e = Dense(n_inputs)(visible)
    e = BatchNormalization()(e)
    e = LeakyReLU()(e)
    # encoder level 2
    e = Dense(n_inputs//2)(e)
    e = BatchNormalization()(e)
    e = LeakyReLU()(e)
    # encoder level 3
    e = Dense(n_inputs//4)(e)
    e = BatchNormalization()(e)
    e = LeakyReLU()(e)
    # bottleneck
    n_bottleneck = n_inputs//6
    bottleneck = Dense(n_bottleneck)(e)
    # define decoder, level 1
    d = Dense(n_inputs//4)(bottleneck)
    d = BatchNormalization()(d)
    d = LeakyReLU()(d)
    # decoder level 2
    d = Dense(n_inputs//2)(d)
    d = BatchNormalization()(d)
    d = LeakyReLU()(d)
    # decoder level 3
    d = Dense(n_inputs)(d)
    d = BatchNormalization()(d)
    d = LeakyReLU()(d)
    # output layer
    output = Dense(n_inputs, activation='linear')(d)
    # define autoencoder model
    model = Model(inputs=visible, outputs=output)
    model.compile(metrics=['accuracy'],optimizer='adam', loss='mse',)
    #plot_model(model, 'autoencoder_no_compress.png', show_shapes=True)
    history = model.fit(X_train, X_train, epochs=5000, batch_size=1600, verbose=2, validation_data=(X_test,X_test))
    plt.plot(history.history['accuracy'], label='train')
    plt.plot(history.history['val_accuracy'], label='test')
    plt.xlabel('Epochs--->')
    plt.ylabel('Accuracy--->')
    plt.title('Simple AutoEncoder Results (Layers:3)')
    plt.legend()
    plt.savefig("AE-5-3.png")
    model.save('AE-5-3-autoencoder.h5')
    encoder = Model(inputs=visible, outputs=bottleneck)
    #plot_model(encoder, 'encoder_no_compress.png', show_shapes=True)
    # save the encoder to file
    encoder.save('AE-5-3-encoder.h5')
    
ts=0.25
n_inputs=180
load_data(ts)
X, X_val, Y, y_val=load_data(ts)
print('Train', X.shape, Y.shape, 'Test', X_val.shape, y_val.shape)
Mod(X, X_val, Y, y_val,n_inputs)
