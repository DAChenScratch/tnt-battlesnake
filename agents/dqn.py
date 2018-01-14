import random
import math
import numpy as np
import tensorflow as tf

from . import Agent


class DQNAgent(Agent):
    '''
    DQN Agent that uses epsilon-greedy for exploration.
    '''

    steps = 0
    epsilon = 0

    def __init__(self, brain, memory, summary_writer, input_shape, num_actions, GAMMA=0.99, EPSILON_MAX=1, EPSILON_MIN=0.01, LAMBDA=0.001, batch_size=64):
        self.brain = brain
        self.memory = memory
        self.summary_writer = summary_writer
        self.input_shape = input_shape
        self.num_actions = num_actions
        self.EPSILON_MAX = EPSILON_MAX
        self.EPSILON_MIN = EPSILON_MIN
        self.LAMBDA = LAMBDA
        self.GAMMA = GAMMA
        self.epsilon = EPSILON_MAX
        self.batch_size = batch_size

    def act(self, state):
        if random.random() < self.epsilon:
            return random.randint(0, self.num_actions - 1)
        else:
            return np.argmax(self.brain.predict(state[np.newaxis, ...]))

    def observe(self, observation):
        self.memory.add(observation)
        self.steps += 1
        self.epsilon = self.EPSILON_MIN + (self.EPSILON_MAX - self.EPSILON_MIN) * math.exp(-self.LAMBDA * self.steps)

    def replay(self):
        batch = self.memory.sample(self.batch_size)

        no_state = np.zeros(self.input_shape)
        next_states = np.array([(no_state if observation[3] is None else observation[3])
                                for observation in batch])
        states = np.array([observation[0] for observation in batch])

        q_values = self.brain.predict(states)
        q_values_next = self.brain.predict(next_states)

        x = np.zeros((len(batch), self.input_shape[0], self.input_shape[1], self.input_shape[2]))
        y = np.zeros((len(batch), self.num_actions))
        errors = np.zeros(len(batch))
        q_value_estimates = np.zeros(len(batch))
        for i, observation in enumerate(batch):
            state, action, reward, next_state = observation[0], observation[1], observation[2], observation[3]

            target = q_values[i]
            target_old = target[action]
            if next_state is None:
                target[action] = reward
            else:
                target[action] = reward + self.GAMMA * np.amax(q_values_next[i])

            x[i] = state
            y[i] = target
            errors[i] = abs(target_old - target[action])
            q_value_estimates[i] = target[action]

        history = self.brain.train(x, y, len(batch))
        loss = history.history['loss']
        return loss, np.mean(q_value_estimates)
        # TODO: Update memory (https://github.com/fkluger/tnt-battlesnake/issues/1)
