#-*- coding: utf-8 -*-
from __future__ import division
import os
import time
import tensorflow as tf
import numpy as np
import vgg16
from ops import *
from utils import *

class transfer_model(object):
    model_name = "transfer_model"     # name for checkpoint

    def __init__(self, sess, epoch, batch_size, dataset_name, checkpoint_dir, result_dir, log_dir, learning_rate = 0.0002):
        self.sess = sess
        self.dataset_name = dataset_name
        self.checkpoint_dir = checkpoint_dir
        self.result_dir = result_dir
        self.log_dir = log_dir
        self.epoch = epoch
        self.batch_size = batch_size
        
        # if dataset_name == 'BLSD':
        self.label_dim = 8

        # parameters
        self.input_height = 224
        self.input_width = 224
        self.output_height = 224
        self.output_width = 224
        self.c_dim = 3

        # train
        self.learning_rate = learning_rate
        
        # get number of batches for a single epoch
        #self.num_batches = len(self.data_X) // self.batch_size ?????
        self.num_batches = 0

    def classifier(self, x, is_training=True, reuse=False):
        # Arichitecture : VGG16(CONV7x7x512_P-FC4096_BR-FC4097_BR-FC[label_dim]-softmax)
        with tf.variable_scope("classifier", reuse=reuse):
            net = tf.nn.relu(bn(linear(x, 4096, scope='fc1'), is_training=is_training, scope='bn1'))
            net = tf.nn.relu(bn(linear(x, 4096, scope='fc2'), is_training=is_training, scope='bn2'))
            out = linear(x, self.label_dim, scope='fc3')
        return out
        
    def build_model(self):
        # some parameters
        image_dims = [self.input_height, self.input_width, self.c_dim]
        bs = self.batch_size

        """ Graph Input """
        # images
        self.inputs = tf.placeholder(tf.float32, [bs] + image_dims, name='input_images')

        # labels
        self.labels = tf.placeholder(tf.float32, [bs, self.label_dim], name='label')

        """ Loss Function """

        # get prob of vgg_pool5
        vgg = vgg16.Vgg16()
        vgg.build(self.inputs)
        logits = self.classifier(vgg.pool5, is_training=True, reuse=False)
        prob = tf.nn.softmax(logits)
        # 
        self.loss = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=logits, labels=self.labels))

        """ Training """
        # divide trainable variables into a group for D and a group for G
        vars = tf.trainable_variables()

        # optimizer
        self.optim = tf.train.AdamOptimizer(self.learning_rate, beta1=self.beta1) \
                      .minimize(self.d_loss, var_list=vars)

        """" Testing """
        # for test
        test_logits = self.classifier(self.inputs, is_training=False, reuse=True)
        self.test_prob = tf.nn.softmax(test_logits)

        """ Summary """
        self.sum = tf.summary.scalar("d_loss_real", d_loss_real)

    def train(self):

        # initialize all variables
        tf.global_variables_initializer().run()

        # saver to save model
        self.saver = tf.train.Saver()

        # summary writer
        self.writer = tf.summary.FileWriter(self.log_dir + '/' + self.model_name, self.sess.graph)

        # restore check-point if it exits
        could_load, checkpoint_counter = self.load(self.checkpoint_dir)
        if could_load:
            start_epoch = (int)(checkpoint_counter / self.num_batches)
            start_batch_id = checkpoint_counter - start_epoch * self.num_batches
            counter = checkpoint_counter
            print(" [*] Load SUCCESS")
        else:
            start_epoch = 0
            start_batch_id = 0
            counter = 1
            print(" [!] Load failed...")

        # loop for epoch
        start_time = time.time()
        for epoch in range(start_epoch, self.epoch):

            # get batch data
            for idx in range(start_batch_id, self.num_batches):
                ''' TODO: add data'''
                batch_images = self.data_X[idx*self.batch_size:(idx+1)*self.batch_size]
                batch_z = np.random.uniform(-1, 1, [self.batch_size, self.z_dim]).astype(np.float32)

                # update network
                _, summary_str, loss = self.sess.run([self.optim, self.sum, self.loss],
                                               feed_dict={self.inputs: batch_images, self.z: batch_z})
                self.writer.add_summary(summary_str, counter)

                # display training status
                counter += 1
                print("Epoch: [%2d] [%4d/%4d] time: %4.4f, loss: %.8f" \
                      % (epoch, idx, self.num_batches, time.time() - start_time, loss))

                # # save training results for every 300 steps
                # if np.mod(counter, 300) == 0:
                #     samples = self.sess.run(self.fake_images, feed_dict={self.z: self.sample_z})
                #     tot_num_samples = min(self.sample_num, self.batch_size)
                #     manifold_h = int(np.floor(np.sqrt(tot_num_samples)))
                #     manifold_w = int(np.floor(np.sqrt(tot_num_samples)))
                #     save_images(samples[:manifold_h * manifold_w, :, :, :], [manifold_h, manifold_w],
                #                 './' + check_folder(self.result_dir + '/' + self.model_dir) + '/' + self.model_name + '_train_{:02d}_{:04d}.png'.format(
                #                     epoch, idx))

            # After an epoch, start_batch_id is set to zero
            # non-zero value is only for the first epoch after loading pre-trained model
            start_batch_id = 0

            # save model
            self.save(self.checkpoint_dir, counter)


        # save model for final step
        self.save(self.checkpoint_dir, counter)

    @property
    def model_dir(self):
        return "{}_{}_{}".format(
            self.model_name, self.dataset_name,
            self.batch_size)

    def save(self, checkpoint_dir, step):
        checkpoint_dir = os.path.join(checkpoint_dir, self.model_dir, self.model_name)

        if not os.path.exists(checkpoint_dir):
            os.makedirs(checkpoint_dir)

        self.saver.save(self.sess,os.path.join(checkpoint_dir, self.model_name+'.model'), global_step=step)

    def load(self, checkpoint_dir):
        import re
        print(" [*] Reading checkpoints...")
        checkpoint_dir = os.path.join(checkpoint_dir, self.model_dir, self.model_name)

        ckpt = tf.train.get_checkpoint_state(checkpoint_dir)
        if ckpt and ckpt.model_checkpoint_path:
            ckpt_name = os.path.basename(ckpt.model_checkpoint_path)
            self.saver.restore(self.sess, os.path.join(checkpoint_dir, ckpt_name))
            counter = int(next(re.finditer("(\d+)(?!.*\d)",ckpt_name)).group(0))
            print(" [*] Success to read {}".format(ckpt_name))
            return True, counter
        else:
            print(" [*] Failed to find a checkpoint")
            return False, 0