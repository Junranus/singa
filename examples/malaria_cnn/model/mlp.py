
from singa import layer
from singa import model
from singa import tensor
from singa import opt
from singa import device
import argparse
import numpy as np

np_dtype = {"float16": np.float16, "float32": np.float32}

singa_dtype = {"float16": tensor.float16, "float32": tensor.float32}


class MLP(model.Model):

    def __init__(self, perceptron_size=100, num_classes=10):
        super(MLP, self).__init__()
        self.num_classes = num_classes
        self.dimension = 2

        self.relu = layer.ReLU()
        self.linear1 = layer.Linear(perceptron_size)
        self.linear2 = layer.Linear(num_classes)
        self.softmax_cross_entropy = layer.SoftMaxCrossEntropy()

    def forward(self, inputs):
        y = self.linear1(inputs)
        y = self.relu(y)
        y = self.linear2(y)
        return y

    def train_one_batch(self, x, y, dist_option, spars):
        out = self.forward(x)
        loss = self.softmax_cross_entropy(out, y)

        if dist_option == 'plain':
            self.optimizer(loss)
        elif dist_option == 'half':
            self.optimizer.backward_and_update_half(loss)
        elif dist_option == 'partialUpdate':
            self.optimizer.backward_and_partial_update(loss)
        elif dist_option == 'sparseTopK':
            self.optimizer.backward_and_sparse_update(loss,
                                                      topK=True,
                                                      spars=spars)
        elif dist_option == 'sparseThreshold':
            self.optimizer.backward_and_sparse_update(loss,
                                                      topK=False,
                                                      spars=spars)
        return out, loss

    def set_optimizer(self, optimizer):
        self.optimizer = optimizer


def create_model(**kwargs):
    """Constructs a CNN model.

    Returns:
        The created CNN model.
    """
    model = MLP(**kwargs)

    return model


__all__ = ['MLP', 'create_model']