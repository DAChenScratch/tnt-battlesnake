import random
import math
import numpy as np
from . import Agent


class DQNAgent(Agent):
    '''
    DQN Agent that uses epsilon-greedy for exploration.
    '''

    steps = 0
    epsilon = 0

    def __init__(self, brain, memory, input_shape, num_actions, GAMMA=0.99, EPSILON_MAX=1, EPSILON_MIN=0.01, LAMBDA=0.001, batch_size=64):
        self.brain = brain
        self.memory = memory
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

        states = np.array([observation[0] for observation in batch])

        q_values = self.brain.predict(states)

        x = np.zeros((len(batch), self.input_shape[0], self.input_shape[1], self.input_shape[2]))
        y = np.zeros((len(batch), self.num_actions))
        for i, observation in enumerate(batch):
            state, action, reward, next_state = observation[0], observation[1], observation[2], observation[3]

            target = q_values[i]
            if next_state is None:
                target[action] = reward
            else:
                no_state = np.zeros(self.input_shape)
                next_states = np.array([(no_state if observation[3] is None else observation[3])
                                        for observation in batch])
                q_values_next = self.brain.predict(next_states)
                target[action] = reward + self.GAMMA * np.amax(q_values_next[i])

            x[i] = state
            y[i] = target

        self.brain.train(x, y, self.batch_size)