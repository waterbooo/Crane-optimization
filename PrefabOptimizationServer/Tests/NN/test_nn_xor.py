import unittest
from sklearn import datasets

class Test_test_nn_xor(unittest.TestCase):
    #def test_pybrain(self):
    #    from pybrain.tools.shortcuts import buildNetwork
    #    from pybrain.datasets import SupervisedDataSet
    #    from pybrain.supervised.trainers import BackpropTrainer
    #    from pybrain import structure
        
    #    import datetime
    #    timeStart = datetime.datetime.now()
    #    net = buildNetwork(2, 5, 1, hiddenclass=structure.SigmoidLayer, outclass=structure.SigmoidLayer)
    #    ds = SupervisedDataSet(2, 1)
    #    X, y = datasets.make_moons(200, noise=0.20)
    #    for i in range(len(X)):
    #        ds.addSample((X[i][0], X[i][1]), (y[i],))
    #    trainer = BackpropTrainer(net, ds)
    #    err = 1.0
    #    while err > 0.05:
    #        err = trainer.train()
    #        trainer.trainUntilConvergence
    #        print(err)
    #    timeEnd = datetime.datetime.now()
    #    print("time elapsed: " + str(timeEnd - timeStart))
    #    err = 0.0
    #    sqrErr = 0.0
    #    for i in range(len(y)):
    #        out = net.activate(X[i])
    #        if out != y[i]:
    #            print(str(i+1) + ": exp - " + str(y[i]) + " act - " + str(out))
    #            sqrErr += pow((out - y[i]), 2.0)
    #    err = pow(sqrErr, 0.5) / 200
    #    print(err)

    def test_keras(self):
        from keras.models import Sequential
        from keras.layers.core import Dense, Activation
        import datetime
        timeStart = datetime.datetime.now()
        model = Sequential()
        model.add(Dense(5, input_dim=2, init="normal"))
        model.add(Activation("sigmoid"))
        model.add(Dense(1))
        model.add(Activation("sigmoid"))
        model.compile(optimizer='rmsprop', loss='binary_crossentropy',
              metrics=['accuracy'])
        X, y = datasets.make_moons(200, noise=0.20)
        hist = model.fit(X, y, nb_epoch=500)
        timeEnd = datetime.datetime.now()
        print("time elapsed: " + str(timeEnd - timeStart))
        out = model.predict(X)
        err = 0.0
        sqrErr = 0.0
        for i in range(len(y)):
            if out[i][0] != y[i]:
                print(str(i+1) + ": exp - " + str(y[i]) + " act - " + str(out[i][0]))
                sqrErr += pow((out[i][0] - y[i]), 2.0)
        err = pow(sqrErr, 0.5) / 200
        print(err)

    def test_neurolab(self):
        from neurolab import net
        import neurolab as nl
        import numpy as np
        import datetime
        timeStart = datetime.datetime.now()
        net = net.newff([[-np.Infinity, np.Infinity], [-np.Infinity, np.Infinity]], [5, 1], transf=[nl.trans.LogSig()] * 2)
        X, y = datasets.make_moons(200, noise=0.20)
        tar = y.reshape(200, 1)
        net.trainf = nl.train.train_bfgs
        
        net.train(X, tar, epochs=500, show=100, goal=0.02)
        timeEnd = datetime.datetime.now()
        print("time elapsed: " + str(timeEnd - timeStart))
        out = net.sim(X)
        err = 0.0
        sqrErr = 0.0
        for i in range(len(y)):
            if y[i] != out[i][0]:
                print(str(i+1) + ": exp - " + str(y[i]) + " act - " + str(out[i][0]))
                sqrErr += pow((out[i][0] - y[i]), 2.0)
        err = pow(sqrErr, 0.5) / 200
        print(err)

    def test_pure_theano(self):
        import numpy as np
        import theano
        import theano.tensor as T

        # Generate a dataset
        np.random.seed(0)
        train_X, train_y = datasets.make_moons(200, noise=0.20)
        train_y_onehot = np.eye(2)[train_y]
 
        # Size definitions
        num_examples = len(train_X) # training set size
        nn_input_dim = 2 # input layer dimensionality
        nn_output_dim = 2 # output layer dimensionality
        nn_hdim = 5 # hiden layer dimensionality
 
        # Gradient descent parameters (I picked these by hand)
        epsilon = 0.01 # learning rate for gradient descent
        reg_lambda = 0.01 # regularization strength 
 
        # Our data vectors
        X = T.matrix('X') # matrix of doubles
        y = T.lvector('y') # vector of int64
 
        # Shared variables with initial values. We need to learn these.
        W1 = theano.shared(np.random.randn(nn_input_dim, nn_hdim), name='W1')
        b1 = theano.shared(np.zeros(nn_hdim), name='b1')
        W2 = theano.shared(np.random.randn(nn_hdim, nn_output_dim), name='W2')
        b2 = theano.shared(np.zeros(nn_output_dim), name='b2')
 
        # Forward propagation
        z1 = X.dot(W1) + b1
        a1 = T.tanh(z1)
        z2 = a1.dot(W2) + b2
        y_hat = T.nnet.softmax(z2)
 
        # The regularization term (optional)
        loss_reg = 1./num_examples * reg_lambda/2 * (T.sum(T.sqr(W1)) + T.sum(T.sqr(W2))) 
        # the loss function we want to optimize
        loss = T.nnet.categorical_crossentropy(y_hat, y).mean() + loss_reg
        # Returns a class prediction
        prediction = T.argmax(y_hat, axis=1)
 
        # Gradients
        dW2 = T.grad(loss, W2)
        db2 = T.grad(loss, b2)
        dW1 = T.grad(loss, W1)
        db1 = T.grad(loss, b1)
 
        # Theano functions that can be called from our Python code
        forward_prop = theano.function([X], y_hat)
        calculate_loss = theano.function([X, y], loss)
        predict = theano.function([X], prediction)
 
        # GPU NOTE: Removed the input values to avoid copying data to the GPU.
        gradient_step = theano.function(
            [X, y],
            updates=((W2, W2 - epsilon * dW2),
                     (W1, W1 - epsilon * dW1),
                     (b2, b2 - epsilon * db2),
                     (b1, b1 - epsilon * db1)))
 
        def build_model(num_passes=500, print_loss=False):
     
            # Re-Initialize the parameters to random values. We need to learn these.
            # (Needed in case we call this function multiple times)
            np.random.seed(0)
            W1.set_value(np.random.randn(nn_input_dim, nn_hdim) / np.sqrt(nn_input_dim))
            b1.set_value(np.zeros(nn_hdim))
            W2.set_value(np.random.randn(nn_hdim, nn_output_dim) / np.sqrt(nn_hdim))
            b2.set_value(np.zeros(nn_output_dim))
     
            # Gradient descent. For each batch...
            for i in range(num_passes):
                # This will update our parameters W2, b2, W1 and b1!
                gradient_step(train_X, train_y)
         
                # Optionally print the loss.
                # This is expensive because it uses the whole dataset, so we don't want to do it too often.
                if print_loss and i % 10 == 0:
                    print ("Loss after iteration %i: %f", i, calculate_loss(train_X, train_y))

        # Build a model with a 3-dimensional hidden layer
        build_model(print_loss=True)

    def test_cnn_keras(self):
        from keras.datasets import imdb
        print('Loading data...')
        (X_train, y_train), (X_test, y_test) = imdb.load_data(nb_words=5000,
                                                              test_split=0.2)
        print("Loaded")

if __name__ == '__main__':
    unittest.main()
