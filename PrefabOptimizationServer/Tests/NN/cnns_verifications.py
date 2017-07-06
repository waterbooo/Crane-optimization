import unittest, os, sys, keras
import data_helpers
import numpy as np

class Test_cnns_verifications(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.wvmodel = data_helpers.load_google_model()
    
    @classmethod
    def tearDownClass(cls):
        del cls.wvmodel
        
    def RunVerificationForLen(length, xv_all, yv_all):
        filePath = os.path.dirname(os.path.abspath(__file__))
        ptnnPath = os.path.join(filePath, "Data", "PreTrainedModels")

        # Define data params for training
        lengths = [length]
        nEpochs = [(i + 1) * 20 + 60 for i in range(2)]
        n_grams_set = [[2,3,4,5], [2,3,4,5,6], [2,3,4,5,6,7]]

        # Do training in cycle
        for n_grams in n_grams_set:
            for nEpoch in nEpochs:
                for vecLen in lengths:
                    print("before training")
                    # Create verification set
                    xv = data_helpers.word2vec_dataset_to_len(xv_all, vecLen)
                    print(xv.shape)
                    yv = yv_all

                    print((n_grams, vecLen, nEpoch))

                    # Get model name
                    netName = Test_cnns_verifications.netName(n_grams, vecLen, nEpoch)

                    # Verify model accuracy
                    Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput([netName], xv, yv)

    def createVerificationInput(wvmodel, vecLen):
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

    # Uncomment to use as tests generator
    #def test_gen_cnn_verifications(self):
    #    # Define data params for training
    #    lengths = [(i + 1) * 20 + 160 for i in range(5)]
    #    nEpochs = [(i + 1) * 20 + 80 for i in range(2)]
    #    n_grams_set = [[2,3,4,5], [2,3,4,5,6]]#, [2,3,4,5,6,7]]

    #    # Do training in cycle
    #    for n_grams in n_grams_set:
    #        for nEpoch in nEpochs:
    #            for vecLen in lengths:
    #                # Get model name
    #                netName = Test_cnns_verifications.netName(n_grams, vecLen, nEpoch)

    #                print("def test_conv_layer_merged_run_single_" + netName + "(self):")
    #                print("    xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, " + str(vecLen) + ")")
    #                print("    Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput([\"" + netName + "\"], xv, yv)")
    #                print("  \n")

    def test_conv_layer_merged_run_single_CNN_2_3_4_5_20_80_Carpeting(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 20)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_20_80_Carpeting"], xv, yv)
  
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_40_80_Carpeting(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 40)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_40_80_Carpeting"], xv, yv)
  
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_60_80_Carpeting(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 60)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_60_80_Carpeting"], xv, yv)
  
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_80_80_Carpeting(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 80)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_80_80_Carpeting"], xv, yv)
  
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_100_80_Carpeting(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 100)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_100_80_Carpeting"], xv, yv)
  
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_120_80_Carpeting(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 120)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_120_80_Carpeting"], xv, yv)
  
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_140_80_Carpeting(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 140)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_140_80_Carpeting"], xv, yv)
  
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_160_80_Carpeting(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 160)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_160_80_Carpeting"], xv, yv)
  
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_180_80_Carpeting(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 180)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_180_80_Carpeting"], xv, yv)
  
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_200_80_Carpeting(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 200)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_200_80_Carpeting"], xv, yv)
  
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_220_80_Carpeting(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 220)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_220_80_Carpeting"], xv, yv)
  
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_240_80_Carpeting(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 240)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_240_80_Carpeting"], xv, yv)
  
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_260_80_Carpeting(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 260)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_260_80_Carpeting"], xv, yv)
  
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_280_80_Carpeting(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 280)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_280_80_Carpeting"], xv, yv)
  
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_300_80_Carpeting(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 300)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_300_80_Carpeting"], xv, yv)
  
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_20_100_Carpeting(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 20)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_20_100_Carpeting"], xv, yv)
  
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_40_100_Carpeting(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 40)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_40_100_Carpeting"], xv, yv)
  
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_60_100_Carpeting(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 60)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_60_100_Carpeting"], xv, yv)
  
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_80_100_Carpeting(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 80)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_80_100_Carpeting"], xv, yv)
  
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_100_100_Carpeting(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 100)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_100_100_Carpeting"], xv, yv)
  
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_120_100_Carpeting(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 120)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_120_100_Carpeting"], xv, yv)
  
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_140_100_Carpeting(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 140)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_140_100_Carpeting"], xv, yv)
  
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_160_100_Carpeting(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 160)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_160_100_Carpeting"], xv, yv)
  
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_180_100_Carpeting(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 180)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_180_100_Carpeting"], xv, yv)
  
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_200_100_Carpeting(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 200)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_200_100_Carpeting"], xv, yv)
  
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_220_100_Carpeting(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 220)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_220_100_Carpeting"], xv, yv)
  
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_240_100_Carpeting(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 240)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_240_100_Carpeting"], xv, yv)
  
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_260_100_Carpeting(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 260)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_260_100_Carpeting"], xv, yv)
  
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_280_100_Carpeting(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 280)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_280_100_Carpeting"], xv, yv)
  
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_300_100_Carpeting(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 300)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_300_100_Carpeting"], xv, yv)
  
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_6_20_80_Carpeting(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 20)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_6_20_80_Carpeting"], xv, yv)
  
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_6_40_80_Carpeting(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 40)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_6_40_80_Carpeting"], xv, yv)
  
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_6_60_80_Carpeting(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 60)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_6_60_80_Carpeting"], xv, yv)
  
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_6_80_80_Carpeting(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 80)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_6_80_80_Carpeting"], xv, yv)
  
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_6_100_80_Carpeting(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 100)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_6_100_80_Carpeting"], xv, yv)
  
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_6_120_80_Carpeting(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 120)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_6_120_80_Carpeting"], xv, yv)
  
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_6_140_80_Carpeting(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 140)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_6_140_80_Carpeting"], xv, yv)
  
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_6_160_80_Carpeting(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 160)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_6_160_80_Carpeting"], xv, yv)
  
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_6_180_80_Carpeting(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 180)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_6_180_80_Carpeting"], xv, yv)
  
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_6_200_80_Carpeting(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 200)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_6_200_80_Carpeting"], xv, yv)
  
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_6_220_80_Carpeting(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 220)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_6_220_80_Carpeting"], xv, yv)
  
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_6_240_80_Carpeting(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 240)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_6_240_80_Carpeting"], xv, yv)
  
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_6_260_80_Carpeting(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 260)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_6_260_80_Carpeting"], xv, yv)
  
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_6_280_80_Carpeting(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 280)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_6_280_80_Carpeting"], xv, yv)
  
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_6_300_80_Carpeting(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 300)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_6_300_80_Carpeting"], xv, yv)
  
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_6_20_100_Carpeting(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 20)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_6_20_100_Carpeting"], xv, yv)
  
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_6_40_100_Carpeting(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 40)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_6_40_100_Carpeting"], xv, yv)
  
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_6_60_100_Carpeting(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 60)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_6_60_100_Carpeting"], xv, yv)
  
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_6_80_100_Carpeting(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 80)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_6_80_100_Carpeting"], xv, yv)
  
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_6_100_100_Carpeting(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 100)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_6_100_100_Carpeting"], xv, yv)
  
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_6_120_100_Carpeting(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 120)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_6_120_100_Carpeting"], xv, yv)
  
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_6_140_100_Carpeting(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 140)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_6_140_100_Carpeting"], xv, yv)
  
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_6_160_100_Carpeting(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 160)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_6_160_100_Carpeting"], xv, yv)
  
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_6_180_100_Carpeting(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 180)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_6_180_100_Carpeting"], xv, yv)
  
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_6_200_100_Carpeting(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 200)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_6_200_100_Carpeting"], xv, yv)
  
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_6_220_100_Carpeting(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 220)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_6_220_100_Carpeting"], xv, yv)
  
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_6_240_100_Carpeting(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 240)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_6_240_100_Carpeting"], xv, yv)
  
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_6_260_100_Carpeting(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 260)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_6_260_100_Carpeting"], xv, yv)
  
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_6_280_100_Carpeting(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 280)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_6_280_100_Carpeting"], xv, yv)
  
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_6_300_100_Carpeting(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 300)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_6_300_100_Carpeting"], xv, yv)
  
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_6_7_20_80_Carpeting(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 20)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_6_7_20_80_Carpeting"], xv, yv)
  
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_6_7_40_80_Carpeting(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 40)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_6_7_40_80_Carpeting"], xv, yv)
  
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_6_7_60_80_Carpeting(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 60)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_6_7_60_80_Carpeting"], xv, yv)
  
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_6_7_80_80_Carpeting(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 80)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_6_7_80_80_Carpeting"], xv, yv)
  
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_6_7_100_80_Carpeting(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 100)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_6_7_100_80_Carpeting"], xv, yv)
  
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_6_7_120_80_Carpeting(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 120)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_6_7_120_80_Carpeting"], xv, yv)
  
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_6_7_140_80_Carpeting(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 140)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_6_7_140_80_Carpeting"], xv, yv)
  
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_6_7_160_80_Carpeting(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 160)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_6_7_160_80_Carpeting"], xv, yv)
  
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_6_7_180_80_Carpeting(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 180)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_6_7_180_80_Carpeting"], xv, yv)
  
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_6_7_200_80_Carpeting(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 200)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_6_7_200_80_Carpeting"], xv, yv)
  
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_6_7_220_80_Carpeting(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 220)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_6_7_220_80_Carpeting"], xv, yv)
  
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_6_7_240_80_Carpeting(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 240)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_6_7_240_80_Carpeting"], xv, yv)
  
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_6_7_260_80_Carpeting(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 260)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_6_7_260_80_Carpeting"], xv, yv)
  
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_6_7_280_80_Carpeting(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 280)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_6_7_280_80_Carpeting"], xv, yv)
  
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_6_7_300_80_Carpeting(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 300)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_6_7_300_80_Carpeting"], xv, yv)
  
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_6_7_20_100_Carpeting(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 20)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_6_7_20_100_Carpeting"], xv, yv)
  
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_6_7_40_100_Carpeting(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 40)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_6_7_40_100_Carpeting"], xv, yv)
  
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_6_7_60_100_Carpeting(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 60)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_6_7_60_100_Carpeting"], xv, yv)
  
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_6_7_80_100_Carpeting(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 80)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_6_7_80_100_Carpeting"], xv, yv)
  
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_6_7_100_100_Carpeting(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 100)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_6_7_100_100_Carpeting"], xv, yv)
  
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_6_7_120_100_Carpeting(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 120)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_6_7_120_100_Carpeting"], xv, yv)
  
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_6_7_140_100_Carpeting(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 140)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_6_7_140_100_Carpeting"], xv, yv)
  
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_6_7_160_100_Carpeting(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 160)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_6_7_160_100_Carpeting"], xv, yv)
  
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_6_7_180_100_Carpeting(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 180)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_6_7_180_100_Carpeting"], xv, yv)
  
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_6_7_200_100_Carpeting(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 200)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_6_7_200_100_Carpeting"], xv, yv)
  
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_6_7_220_100_Carpeting(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 220)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_6_7_220_100_Carpeting"], xv, yv)
  
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_6_7_240_100_Carpeting(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 240)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_6_7_240_100_Carpeting"], xv, yv)
  
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_6_7_260_100_Carpeting(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 260)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_6_7_260_100_Carpeting"], xv, yv)
  
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_6_7_280_100_Carpeting(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 280)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_6_7_280_100_Carpeting"], xv, yv)
  
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_6_7_300_100_Carpeting(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 300)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_6_7_300_100_Carpeting"], xv, yv)

    def test_conv_layer_merged_run_single_CNN_2_3_4_5_180_100_Carpeting_CW(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 180)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_180_100_Carpeting_CW"], xv, yv)
      
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_200_100_Carpeting_CW(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 200)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_200_100_Carpeting_CW"], xv, yv)
      
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_220_100_Carpeting_CW(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 220)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_220_100_Carpeting_CW"], xv, yv)
      
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_240_100_Carpeting_CW(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 240)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_240_100_Carpeting_CW"], xv, yv)
      
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_260_100_Carpeting_CW(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 260)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_260_100_Carpeting_CW"], xv, yv)
      
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_180_120_Carpeting_CW(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 180)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_180_120_Carpeting_CW"], xv, yv)
      
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_200_120_Carpeting_CW(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 200)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_200_120_Carpeting_CW"], xv, yv)
      
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_220_120_Carpeting_CW(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 220)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_220_120_Carpeting_CW"], xv, yv)
      
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_240_120_Carpeting_CW(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 240)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_240_120_Carpeting_CW"], xv, yv)
      
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_260_120_Carpeting_CW(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 260)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_260_120_Carpeting_CW"], xv, yv)
      
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_6_180_100_Carpeting_CW(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 180)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_6_180_100_Carpeting_CW"], xv, yv)
      
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_6_200_100_Carpeting_CW(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 200)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_6_200_100_Carpeting_CW"], xv, yv)
      
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_6_220_100_Carpeting_CW(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 220)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_6_220_100_Carpeting_CW"], xv, yv)
      
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_6_240_100_Carpeting_CW(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 240)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_6_240_100_Carpeting_CW"], xv, yv)
      
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_6_260_100_Carpeting_CW(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 260)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_6_260_100_Carpeting_CW"], xv, yv)
      
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_6_180_120_Carpeting_CW(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 180)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_6_180_120_Carpeting_CW"], xv, yv)
      
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_6_200_120_Carpeting_CW(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 200)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_6_200_120_Carpeting_CW"], xv, yv)
      
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_6_220_120_Carpeting_CW(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 220)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_6_220_120_Carpeting_CW"], xv, yv)
      
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_6_240_120_Carpeting_CW(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 240)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_6_240_120_Carpeting_CW"], xv, yv)
      
    def test_conv_layer_merged_run_single_CNN_2_3_4_5_6_260_120_Carpeting_CW(self):
        xv, yv = Test_cnns_verifications.createVerificationInput(self.wvmodel, 260)
        Test_cnns_verifications.RunSequenceOfPreTrainedNetworksOnSameInput(["CNN_2_3_4_5_6_260_120_Carpeting_CW"], xv, yv)


if __name__ == '__main__':
    unittest.main()
