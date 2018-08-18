import numpy as np
from keras.layers import Input, Dense, Conv2D, UpSampling2D
from keras.layers import MaxPooling2D
from keras.utils import print_summary
from keras.models import Model
from keras.callbacks import TensorBoard
from sklearn.model_selection import train_test_split
import pickle
input_img = Input(shape=(7500,))
input_img_conv = Input(shape=(250, 250, 3))
encoding_dim = 1024


class SimpleCoder:
    def encoder(self):
        encoded = Dense(encoding_dim, activation='relu')(input_img)
        return encoded

    def decoder(self, encoded):
        decoded = Dense(187500, activation='sigmoid')(encoded)
        return decoded

class DeepCoder:
    def encoder(self):
        encoded = Dense(187500, activation='relu')(input_img)
        encoded = Dense(4086, activation='relu')(encoded)
        encoded = Dense(2048, activation='relu')(encoded)
        encoded = Dense(encoding_dim, activation='relu')(encoded)
        return encoded

    def decoder(self, encoded):
        decoded = Dense(2048, activation='relu')(encoded)
        decoded = Dense(4086, activation='relu')(decoded)
        decoded = Dense(187500, activation='sigmoid')(decoded)
        return decoded

class ConvCoder:
    def encoder(self):
        encoded = Conv2D(32, (3, 3), activation='relu', padding='same')(input_img_conv)
        encoded = MaxPooling2D((2, 2), padding='same')(encoded)
        encoded = Conv2D(16, (3, 3), activation='relu', padding='same')(encoded)
        return encoded

    def decoder(self, encoded):
        decoded = Conv2D(16, (3, 3), activation='relu', padding='same')(encoded)
        decoded = UpSampling2D((2, 2))(decoded)
        decoded = Conv2D(32, (3, 3), activation='relu', padding='same')(decoded)
        decoded = Conv2D(3, (3, 3), activation='sigmoid', padding='same')(decoded)
        return decoded


def loadFromPickle():
    with open("features", "rb") as f:
        features = np.array(pickle.load(f))

    return features


class AutoEncoder:
    def getData(self):

        features = loadFromPickle()
        features = features.astype('float32') / 255.
        x_train, x_test = train_test_split(features, random_state=0,
                                                            test_size=0.1)
        x_train = x_train.reshape((len(x_train), np.prod(x_train.shape[1:])))
        x_test = x_test.reshape((len(x_test), np.prod(x_test.shape[1:])))
        return x_train, x_test

    def getAutoEncoder(self, BaseCoder):
        encoded = BaseCoder.encoder(self)
        decoded = BaseCoder.decoder(self, encoded)
        if id(BaseCoder) == id(ConvCoder):
            autoencoder = Model(input_img_conv, decoded)
        else:
            autoencoder = Model(input_img, decoded)
        return autoencoder

    def printSummary(self, autoencoder):
        print_summary(autoencoder)

    def saveModel(self, autoencoder, name):
        autoencoder.save(name)

    def trainModel(self, baseCoder, name):
        x_train, x_test = AutoEncoder.getData(self)
        if id(baseCoder) == id(ConvCoder):
            x_train = np.reshape(x_train, (len(x_train), 250, 250, 3))
            x_test = np.reshape(x_test, (len(x_test), 250, 250, 3))

        autoencoder = AutoEncoder.getAutoEncoder(self, baseCoder)
        autoencoder.compile(optimizer='adadelta', loss='binary_crossentropy')
        AutoEncoder.printSummary(self, autoencoder)
        autoencoder.fit(x_train, x_train, epochs=3, batch_size=64, shuffle=True,
                        validation_data=(x_test, x_test),
                        callbacks=[TensorBoard(log_dir=name)], verbose=1)
        AutoEncoder.saveModel(self, autoencoder, name + '.h5')

    def main(self):
        #AutoEncoder.trainModel(self, baseCoder=SimpleCoder, name='Simple_Autoencoder_face')
        #AutoEncoder.trainModel(self, baseCoder=DeepCoder, name='Deep_Autoencoder_face')
        AutoEncoder.trainModel(self, baseCoder=ConvCoder, name='Convolutional_Autoencoder_face')


if __name__ == '__main__':
    AutoEncoder.main(AutoEncoder)
