import unittest, os
import keras
import numpy as np


class Test_test_cnn_classifier(unittest.TestCase):

    def test_conv_layer_creation(self):
        """test for creation and running convolutional layer with keras"""
        import data_helpers
        model = Test_test_cnn_classifier.createConv2DLayer(data_helpers.max_sent_len, 300, 3)
        input = Test_test_cnn_classifier.createTempInput(data_helpers.max_sent_len, 300)
        output = model.predict(np.array([input]))
        print(output)

    def test_conv_layer_merged(self):
        """test for creation and running several merged convolution2d layers with keras"""
        import data_helpers
        model = Test_test_cnn_classifier.createMergedConv2DLayer(data_helpers.max_sent_len, 300, [3, 4, 5])
        input = Test_test_cnn_classifier.createTempInput(data_helpers.max_sent_len, 300)
        output = model.predict(np.array([input]))
        print(output)

    def test_conv_layer_merged_train(self):
        """Test for training model for sentense classification with Keras"""
        import data_helpers

        # Prepare word2vec model
        wvmodel = data_helpers.load_google_model()

        model = Test_test_cnn_classifier.createMergedConv2DLayer(data_helpers.max_sent_len, data_helpers.wordvec_len, [2, 3, 4, 5, 6])
        x, y = Test_test_cnn_classifier.createTrainInput(wvmodel)

        model.fit(x, y, batch_size=32,
                  nb_epoch=80,
                  validation_split=0.1, verbose=2)

        json_string = model.to_json()

        filePath = os.path.dirname(os.path.abspath(__file__))

        open(os.path.join(filePath, "Data", 'my_model_architecture.json'), 'w').write(json_string)
        model.save_weights(os.path.join(filePath, "Data", 'my_model_weights.h5'))
        output = model.predict(x)

        for i in range(len(y)):
            print(str(output[i]) + "  " + str(y[i]))

    def test_wvmodel_loaded_correctly(self):
        """Test for training model for sentense classification with Keras"""
        import data_helpers
         
        test_cnn = Test_test_cnn_classifier

        # Prepare word2vec model
        wvmodel = data_helpers.load_google_model()
        
        # load data
        x_all, y_all = test_cnn.createTrainInput(wvmodel, 300)
        xv_all, yv_all = test_cnn.createVerificationInput(wvmodel, 300)
        # delete model
        del wvmodel

        # calc reasonable elements in train set
        notNullCount = 0
        flattenx = x_all.flatten()
        for x in flattenx:
            notNullCount += 1
        # check train input is not empty
        self.assertNotEqual(notNullCount, 0)

        # calc reasonable elements in verification set
        flattenxv = xv_all.flatten()
        notNullCount = 0
        for x in flattenx:
            notNullCount += 1
        # check verification input is not empty
        self.assertNotEqual(notNullCount, 0)


    def test_conv_layer_merged_train_mult(self):
        """Test for training model for sentense classification with Keras"""
        import data_helpers

        test_cnn = Test_test_cnn_classifier

        # Prepare word2vec model
        wvmodel = data_helpers.load_google_model()
        x_all, y_all = test_cnn.createTrainInput(wvmodel, 300)
       
        xv_all, yv_all = test_cnn.createVerificationInput(wvmodel, 300)
        del wvmodel

        filePath = os.path.dirname(os.path.abspath(__file__))
        ptnnPath = os.path.join(filePath, "Data", "PreTrainedModels")

        # Define data params for training
        lengths = [(i + 1) * 20 + 160 for i in range(5)]
        nEpochs = [(i + 1) * 20 + 80 for i in range(2)]
        n_grams_set = [[2,3,4,5], [2,3,4,5,6]]#, [2,3,4,5,6,7]]

        # Do training in cycle
        for n_grams in n_grams_set:
            for nEpoch in nEpochs:
                for vecLen in lengths:
                    # Create training and verification sets
                    x = data_helpers.word2vec_dataset_to_len(x_all, vecLen)
                    y = y_all
                    xv = data_helpers.word2vec_dataset_to_len(xv_all, vecLen)
                    yv = yv_all

                    # Create NN
                    model = test_cnn.createMergedConv2DLayer(data_helpers.max_sent_len, vecLen, n_grams)
                    
                    # Train NN
                    model.fit(x, y, batch_size=32,
                              nb_epoch=nEpoch,
                              validation_split=0.1, verbose=2)

                    # Convert model structure into json
                    json_string = model.to_json()

                    # Save model structure
                    netName = test_cnn.netName(n_grams, vecLen, nEpoch)
                    open(os.path.join(ptnnPath, netName + ".json"), 'w').write(json_string)
                    
                    # Save model weights
                    model.save_weights(os.path.join(ptnnPath, netName + ".h5"))

    def test_load_and_verify_conv_net(self):
        import data_helpers

        # Prepare word2vec model
        wvmodel = data_helpers.load_google_model()

        preTrainedNets = ["CNN_2_3_4_5_6_7_80_Carpeting",
                          "CNN_2_3_4_5_6_80_Carpeting",
                          "CNN_2_3_4_80_Carpeting",
                          "CNN_2_3_4_40_Carpeting",
                          "CNN_2_3_4_20_Carpeting"]
        x, y = Test_test_cnn_classifier.createVerificationInput(wvmodel)

        Test_test_cnn_classifier.RunSequenceOfPreTrainedNetworksOnSameInput(preTrainedNets, x, y)

    def test_load_and_verify_conv_net_40(self):
        import data_helpers

        # Prepare word2vec model
        wvmodel = data_helpers.load_google_model()

        preTrainedNets = ["CNN_2_3_4_5_6_40_80_Carpeting_gpu",
                          "CNN_2_3_4_5_6_40_100_Carpeting_gpu",
                          "CNN_2_3_4_5_6_40_80_Carpeting_cpu"]
        x, y = Test_test_cnn_classifier.createVerificationInput(wvmodel, 40)

        Test_test_cnn_classifier.RunSequenceOfPreTrainedNetworksOnSameInput(preTrainedNets, x, y)

    def test_load_and_verify_conv_net_50(self):
        import data_helpers

        # Prepare word2vec model
        wvmodel = data_helpers.load_google_model()

        preTrainedNets = [
                          "CNN_2_3_4_5_6_50_80_Carpeting_gpu",
                          "CNN_2_3_4_5_6_50_100_Carpeting_gpu",
                          "CNN_2_3_4_5_6_50_80_Carpeting_cpu"]
        x, y = Test_test_cnn_classifier.createVerificationInput(wvmodel, 50)

        Test_test_cnn_classifier.RunSequenceOfPreTrainedNetworksOnSameInput(preTrainedNets, x, y)

    def netName(n_grams, wvlen, epochs):
        name = "CNN_"
        for n in n_grams:
            name += str(n) + "_"
        name += str(wvlen) + "_" + str(epochs) + "_Carpeting_CW"
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

    
    def createConv2DLayer(inputLen, inputElementLen, filterLen):
        from keras.models import Sequential, Graph
        from keras.layers.core import Dense, Dropout, Activation, Flatten, Merge, Reshape
        from keras.layers.embeddings import Embedding
        from keras.layers.convolutional import Convolution2D, MaxPooling2D

        input = Test_test_cnn_classifier.createTempInput(inputLen, inputElementLen)
        
        model = Sequential()

        model.add(Convolution2D(150, filterLen, inputElementLen, input_shape=(1, inputLen, inputElementLen)))
        model.add(MaxPooling2D(pool_size=(inputLen - filterLen + 1, 1)))
        model.add(Flatten())

        model.compile(loss='binary_crossentropy', optimizer='rmsprop', class_mode='binary')
        return model

    def createMergedConv2DLayer(inputLen, inputElementLen, filterLens):
        from keras.models import Sequential, Graph
        from keras.layers.core import Dense, Dropout, Activation, Flatten, Merge
        from keras.layers.convolutional import Convolution2D, MaxPooling2D

        graph = Graph()
        graph.add_input(name='input', input_shape=(1, inputLen, inputElementLen))
        for filterLen in filterLens:
            conv = Convolution2D(150, filterLen, inputElementLen, input_shape=(1, inputLen, inputElementLen))
            pool = MaxPooling2D(pool_size=(inputLen - filterLen + 1, 1))
            flatten = Flatten()
            graph.add_node(conv, name='conv-%s' % filterLen, input='input')
            graph.add_node(pool, name='maxpool-%s' % filterLen, input='conv-%s' % filterLen)
            graph.add_node(flatten, name='flatten-%s' % filterLen, input='maxpool-%s' % filterLen)
           
        if len(filterLens) > 1:
            graph.add_output(name='output',
                             inputs=['flatten-%s' % filterLen for filterLen in filterLens],
                             merge_mode='concat')
        model = Sequential()
        model.add(Dropout(0.25, input_shape=(1, inputLen, inputElementLen)))
        model.add(graph)
        model.add(Dense(150))
        model.add(Dropout(0.5))
        model.add(Activation('relu'))
        model.add(Dense(1))
        model.add(Activation('sigmoid'))
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
            rwv = np.reshape(wv, (1, wv.shape[0], wv.shape[1]))
            xx.append(rwv)
        
        x_shuffled = np.array(xx)
        shape = x_shuffled.shape
        x_shuffled = np.reshape(x_shuffled, newshape=(shape[0], 1, data_helpers.max_sent_len, wordveclen))
       
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
            rwv = np.reshape(wv, (1, wv.shape[0], wv.shape[1]))
            xx.append(rwv)
        
        x_shuffled = np.array(xx)
        shape = x_shuffled.shape
        x_shuffled = np.reshape(x_shuffled, newshape=(shape[0], 1, data_helpers.max_sent_len, vecLen))
       
        return (x_shuffled, y_shuffled)

    def createTempInput(maxWords, wordLen):
        import random
        res = []
        for i in range(maxWords):
            res.append(np.array([random.random() for j in range(wordLen)]))
        return np.array([np.array(res)])

if __name__ == '__main__':
    unittest.main()
