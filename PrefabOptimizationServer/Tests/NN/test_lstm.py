import unittest, os, keras, requests
import numpy as np
import data_helpers

class Test_lstm(unittest.TestCase):
    def test_lstm_train_mult(self):
        """Test for training lstm model for sentense classification with Keras"""
        import data_helpers

        # Prepare word2vec model
        wvmodel = data_helpers.load_google_model()
        x_all, y_all = Test_lstm.createTrainInput(wvmodel, 300)
       
        xv_all, yv_all = Test_lstm.createVerificationInput(wvmodel, 300)
        del wvmodel

        filePath = os.path.dirname(os.path.abspath(__file__))
        ptnnPath = os.path.join(filePath, "Data", "PreTrainedModels")

        # Define data params for training
        lengths = [160, 200]
        nEpochs = [i * 100 + 400 for i in range(6)]
        numHidden = [50, 100]

        # Do training in cycle
        for nEpoch in nEpochs:
            for vecLen in lengths:
                for nh in numHidden:
                    # Create training and verification sets
                    x = data_helpers.word2vec_dataset_to_len2D(x_all, vecLen)
                    y = y_all
                    xv = data_helpers.word2vec_dataset_to_len2D(xv_all, vecLen)
                    yv = yv_all

                    # Create NN
                    model = Test_lstm.createLSTMNetwork(data_helpers.max_sent_len, vecLen, nh)
                    
                    # Train NN
                    model.fit(x, y, batch_size=32,
                                nb_epoch=nEpoch,
                                validation_split=0.1, verbose=2)

                    # Convert model structure into json
                    json_string = model.to_json()

                    # Save model structure
                    netName = Test_lstm.netName(vecLen, nEpoch, nh)
                    open(os.path.join(ptnnPath, netName + ".json"), 'w').write(json_string)
                    
                    # Save model weights
                    model.save_weights(os.path.join(ptnnPath, netName + ".h5"))

    def createLSTMNetwork(inputLen, inputElementLen, hiddenLen = 150):
        """
        Creates LSTM-layer based neural network for sentence classifiation
        Input of network has shape: (N samples X Maximum length of sentence X Number of elements in words word2vec representation)
        """
        from keras.models import Sequential
        from keras.layers import Dense, Dropout, Activation
        from keras.layers import LSTM

        model = Sequential()
        model.add(Dropout(0.25, input_shape=(inputLen, inputElementLen)))
        model.add(LSTM(hiddenLen, dropout_U=0.2, dropout_W=0.2))
        model.add(Dense(1))
        model.add(Activation("sigmoid"))

        model.compile(loss='binary_crossentropy', optimizer='rmsprop', class_mode='binary')
        return model

    def __GetWordSequenceVec(sentence):
        word2vec_service_url = "http://50.112.12.33:8000/"
        single_word_wv_path = "getwordvec"
        multiple_words_wv_path = "getwordvecs"

        # Pre-process sentence to be a vector of words and padding symbols
        sent = data_helpers.clean_str(sentence.strip())
        sent = sent.split(" ")

        # Post a request to word2vec service
        headers = {'content-type': 'application/json'}
        wordVecs = requests.post(word2vec_service_url + multiple_words_wv_path, data = json.dumps({"words": sent}), headers=headers)
        tol = 0.00000001

        # Imitialize result with zeros
        sent_vec = np.zeros(len(wordVecs[0]))

        # Iterate through obtained wordvecs
        if len(wordVecs) > 0:
            numw = 0
            for wv in wordVecs:
                # Skip unknown words
                if np.linalg.norm(wv) < tol:
                    continue
                
                # Add known words to vec
                try:
                    sent_vec = np.add(sent_vec, np.array(wv))
                    numw += 1
                except:
                    pass

            # Normalize and return vector for the case of 2 and more words
            if numw > 1:
                return sent_vec / np.sqrt(sent_vec.dot(sent_vec))
        return sent_vec

    def createCLSTMNetwork(inputLen, inputElementLen, hiddenLen = 150):
        """
        Creates LSTM-layer based neural network for sentence classifiation with taking into account context
        Input of network has shape: (N samples X Maximum length of sentence X 2*Number of elements in words word2vec representation)
        Here in addition to wor2vec representation of the word each vector has word sequence to vec representation of context
        Network differs from LSTM just having extended input
        """
        from keras.models import Sequential
        from keras.layers import Dense, Dropout, Activation
        from keras.layers import LSTM

        model = Sequential()
        model.add(Dropout(0.25, input_shape=(inputLen, inputElementLen * 2)))
        model.add(LSTM(hiddenLen, dropout_U=0.2, dropout_W=0.2))
        model.add(Dense(1))
        model.add(Activation("sigmoid"))

        model.compile(loss='binary_crossentropy', optimizer='rmsprop', class_mode='binary')
        return model

    def createTrainInput(wvmodel, wordveclen = 20):
        import data_helpers

        ## Load data
        print("Loading data...")
        x, y = data_helpers.load_data()
        print(x)
        print(y)

        ## Shuffle data
        shuffle_indices = np.random.permutation(np.arange(len(y)))
        shuffle_indices = np.array([int(i) for i in shuffle_indices])
        x_shuffled = x[shuffle_indices]
        y_shuffled = y[shuffle_indices].argmax(axis=1)
        xx = []
        for sen in x_shuffled:
            wv = data_helpers.sentence_to_wor2vec_len(sen, wvmodel, wordveclen)
            xx.append(wv)
        
        x_shuffled = np.array(xx)
       
        return (x_shuffled, y_shuffled)

    def createVerificationInput(wvmodel, vecLen=20):
        import data_helpers

        ## Load data
        print("Loading data...")
        x, y = data_helpers.load_verification_data("verification_instructions.txt", "verification_non_instructions.txt")

        x_shuffled = x
        y_shuffled = y.argmax(axis=1)
        xx = []
        for sen in x_shuffled:
            wv = data_helpers.sentence_to_wor2vec_len(sen, wvmodel, vecLen)
            xx.append(wv)
        
        x_shuffled = np.array(xx)
       
        return (x_shuffled, y_shuffled)

    def netName(wvlen, epochs, nh=150):
        name = "LSTM_"
        name += str(wvlen) + "_" + str(epochs) + "_" + str(nh) + "_Carpeting_CW"
        return name

    def RunSequenceOfPreTrainedNetworksOnSameInput(nns, x, y):
        filePath = os.path.dirname(os.path.abspath(__file__))
        preTrainedNets = nns
        ptnnPath = os.path.join(filePath, "Data", "PreTrainedModels")
        numPos = np.sum(y)
        for ptnn in preTrainedNets:
            with open(os.path.join(ptnnPath, ptnn + ".json"), "r") as dataFile:
                dataFile.seek(0, 0)
                data = dataFile.read()
                model = keras.models.model_from_json(data)
                model.load_weights(os.path.join(ptnnPath, ptnn + ".h5"))
                model.compile(loss='binary_crossentropy', optimizer='rmsprop', class_mode='binary')

                output = model.predict(x)
                wrongs = 0
                pnWrongs = ([], []) 
                for i in range(len(y)):
                    #print(str(output[i][0]) + "  " + str(y[i]))
                    if abs(y[i] - output[i][0]) > 0.5:
                        wrongs += 1
                        if y[i] == 1:
                            pnWrongs[0].append(i+1)
                        else:
                            pnWrongs[1].append(i+1 - numPos)
                print(ptnn + ": wrong " + str(wrongs) + ", percent: " + str(wrongs * 100.0 / len(x)))
                print("wrong positives: " + str(pnWrongs[0]) + ", wrong negatives: " + str(pnWrongs[1]))
                del model

    @unittest.skip("Enable to use as tests generator")
    def test_gen_lstm_verifications(self):
        # Define data params for training
        lengths = [160, 200]
        nEpochs = [i * 100 + 400 for i in range(6)]
        numHidden = [50, 100]

        # Do training in cycle
        for nEpoch in nEpochs:
            for vecLen in lengths:
                for nh in numHidden:
                    # Get model name
                    netName = Test_lstm.netName(vecLen, nEpoch, nh)

                    print("    def test_lstm_run_single_" + netName + "(self):")
                    print("        wvmodel = data_helpers.load_google_model()")
                    print("        xv, yv = Test_lstm.createVerificationInput(wvmodel, " + str(vecLen) + ")")
                    print("        del wvmodel")
                    print("        Test_lstm.RunSequenceOfPreTrainedNetworksOnSameInput([\"" + netName + "\"], xv, yv)")
                    print("\n")

if __name__ == '__main__':
    unittest.main()
