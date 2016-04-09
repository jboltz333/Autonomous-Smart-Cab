import random
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator

# RULES:
# 1. No stopping at green unless have to
# 2. As you get closer, more reward (closer == distance)
# 3. Higher penalty as steps increase
# 4. High penalty for accident
# 5. Reward for successful right on red
# 6. Reward for successful left on green

# Take action
# Recieve immediate reward
# Observe new state
# Update table entry for Q^(s,a) as follows:
# Q(s,a) = r + & * max@' * Q^(s',a')
# s = s'

#   EXAMPLE: 
# Set all states to 0
# Available actions: a12, a14 Chose a12
# reward = 1
# Available actions: a21, a25, a23 Update Q(s1, a12): Q(s1, a12) = r + .5 * max(Q(s2,a21), Q(s2,a25), Q(s2,a23)) = 1
# Available actions: a21, a25, a23 Chose a23
# reward = 1
# Available actions: a32, a36 Update Q(s1, a12): Q(s2, a23) = r + .5 * max(Q(s3,a32), Q(s3,a36)) = 1	

"""
 1. The idea here is that the agent should learn to follow the next_waypoint 
    whenever traffic allows it to, without you telling it anything about how 
    the traffic laws work.
 2. Write some methods to keep track of the agent's performance
"""
"""
Explore more at beginning
Exploit more near end

 1. Make very optimistic assumptions about the result of taking an action you haven't tried yet. 
    (For example, initialize all "unknown" Q values to something higher than the highest cumulative reward your cab could earn in reality.)
 2. Decay epsilon over time, so that initial action selection is more random and eventual action selection is closer to optimal.
 3. If you decay epsilon, you can scale it by a constant (0 < c < 1)
"""
"""
 Q-learning method 1:
1) Sense the environment (see what changes naturally occur in the environment)
2) Take an action - get a reward
3) Sense the environment (see what changes the action has on the environment)
4) Update the Q-table
5) Repeat 

Q-learning method 2:
1) Sense the environment (see what changes occur naturally in the environment) - store it as state 0
2) Take an action/reward - store as action 0 & reward 0

In the next iteration
1) Sense environment (see what changes occur naturally and from an action)
2) Update the Q-table
3) Take an action - get a reward
4) Repeat
"""

class LearningAgent(Agent):
	"""An agent that learns to drive in the smartcab world."""

	counter = 0
	
	def __init__(self, env):
		super(LearningAgent, self).__init__(env)  			# sets self.env = env, state = None, next_waypoint = None, and a default color
		self.color = 'red'  								# override color
		self.planner = RoutePlanner(self.env, self)  		# simple route planner to get next_waypoint
        # TODO: Initialize any additional variables here
		self.counter = 0
		
	def reset(self, destination=None):
		self.planner.route_to(destination)
        # TODO: Prepare for a new trip; 
		#		reset any variables here, if required
		
	def update(self, t):
        # Gather inputs
		self.next_waypoint = self.planner.next_waypoint()  	# from route planner, also displayed by simulator
		inputs = self.env.sense(self)
		deadline = self.env.get_deadline(self)

        # TODO: Update state
		if self.counter == 0:
			# Initialize q-value table
			self.counter = 1
		
		updated = self.update_state(self.next_waypoint, inputs, deadline)
		
		choice = self.lookup_actions(updated)
		
        # TODO: Select action according to your policy
		action = choice

        # Execute action and get reward
		reward = self.env.act(self, action)
		
		# TODO: Learn policy based on state, action, reward
		print "LearningAgent.update(): deadline = {}, inputs = {}, action = {}, reward = {}".format(deadline, inputs, action, reward)  # [debug]
		
		self.update_policy(updated, action, reward)
		
		
	def update_state(self, next_waypoint, inputs, deadline):
		left = inputs['left']
		oncoming = inputs['oncoming']
		right = inputs['right']
		light = inputs['light']
		
		if right == None and left == None:
			cross_traffic = False
		else:
			cross_traffic = True
		
		if deadline <= 10:
			anarchy_time = True
		else:
			anarchy_time = False
		
		state = [light, oncoming, cross_traffic, next_waypoint, anarchy_time]
		
		return updated_state
		
		
	def lookup_actions(self, state):
			
		light = state[0]
		oncoming = state[1]
		cross_traffic = state[2]
		next_waypoint = state[3]
		anarchy_time = state[4]
			
		tuple_state = (('light': light), ('oncoming': oncoming), ('cross_traffic': cross_traffic), 
				       ('next_waypoint': next_waypoint), ('anarchy_time': anarchy_time))
					  
		q_vals = self.q_values(tuple_state)			  
		
			
	def update_policy(self, state, action, reward):
		# ...
	
	def q_values(self, state, action=None):
		# ...


def run():
    """Run the agent for a finite number of trials."""

    # Set up environment and agent
    e = Environment()  									# create environment (also adds some dummy traffic)
    a = e.create_agent(LearningAgent)  					# create agent
    e.set_primary_agent(a, enforce_deadline=True)  		# set agent to track

    # Now simulate it
    sim = Simulator(e, update_delay=0.3)  				# reduce update_delay to speed up simulation
    sim.run(n_trials=10)  								# press Esc or close pygame window to quit


if __name__ == '__main__':
    run()
