import random
from math import exp
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator


class LearningAgent(Agent):
	"""An agent that learns to drive in the smartcab world."""

	start = True
	q_values = {}
	win = 0
	count = 0
	T = 110
	
	def __init__(self, env):
		super(LearningAgent, self).__init__(env)  			# sets self.env = env, state = None, next_waypoint = None, and a default color
		self.color = 'red'  								# override color
		self.planner = RoutePlanner(self.env, self)  		# simple route planner to get next_waypoint
        # TODO: Initialize any additional variables here
		
	def reset(self, destination=None):
		self.planner.route_to(destination)
        # TODO: Prepare for a new trip; 
		#		reset any variables here, if required
		
		#Avoiding a range limit that keeps happening around 99
		#due to the number being too large
		self.T = self.T/1.1
		self.count = self.count + 1 
		
	def update(self, t):
        # Gather inputs
		self.next_waypoint = self.planner.next_waypoint()  	# from route planner, also displayed by simulator
		inputs = self.env.sense(self)
		deadline = self.env.get_deadline(self)

        # TODO: Update state
		if self.start == True:
			self.q_values = self.initialize_qtable()
			self.start = False
		
		updated = self.update_state(self.next_waypoint, inputs, deadline)
		choice, max_action = self.lookup_actions(updated)
		
        # TODO: Select action according to your policy
		action = choice

        # Execute action and get reward
		reward = self.env.act(self, action)
		if reward == 12:
			self.win = self.win + 1
			print self.win

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
		
		return state
		
		
	def lookup_actions(self, state):
		action = ["left", "forward", "right", None]	
		q_vals_list = []
		random_list = []
		
		light = state[0]
		oncoming = state[1]
		cross_traffic = state[2]
		next_waypoint = state[3]
		anarchy_time = state[4]
		
		for each in action:	
			q_val_state = (('light', light), ('oncoming', oncoming), ('cross_traffic', cross_traffic),
						   ('next_waypoint', next_waypoint), ('anarchy_time', anarchy_time), each)
			q_vals = self.q_values[q_val_state]
			q_vals_list.append([q_vals, each])
		max_action = max(q_vals_list)
		
		if self.count < 90:
			#Boltmann method
			prob_list = []
			q_sum_exp = exp(q_vals_list[0][0]/self.T) + exp(q_vals_list[1][0]/self.T) +	exp(\
							q_vals_list[2][0]/self.T) + exp(q_vals_list[3][0]/self.T)
			for each in q_vals_list:
				boltzmann = exp(each[0]/self.T)/q_sum_exp
				prob_list.append([boltzmann, each[1]])
				
			a = [prob_list[0][0], prob_list[0][1]] 
			b = [prob_list[1][0], prob_list[1][1]] 
			c = [prob_list[2][0], prob_list[2][1]] 
			d = [prob_list[3][0], prob_list[3][1]] 
			q_range = [a,[b[0]+a[0], b[1]], [c[0]+b[0]+a[0], c[1]], [1,d[1]]]
				
			x = random.uniform(0,1)
				
			if x <= q_range[0][0]:
				choice = q_range[0][1]
			elif q_range[0][0] < x <= q_range[1][0]:
				choice = q_range[1][1]
			elif q_range[1][0] < x <= q_range[2][0]:
				choice = q_range[2][1]
			else:
				choice = q_range[3][1]
			###
		else:
			choice = max_action[1]
		
		# I tried two different choice methods, the first being the commented out 
		# section below, and the second, better method was the Boltzmann method
		# above.
		"""	
		for each in q_vals_list:
			if each[0] == 0:
				random_list.append(each[1])
		
		if max_action[0] == 0:
			choice = random.choice(action)
		elif (len(random_list) > 0):
			choice = random.choice(random_list)
		else:
			choice = max_action[1]
		"""
			
		return choice, max_action
			
	def update_policy(self, state, action, reward):
		actions = ["left","forward","left",None]
		each_vals_list = []
		discount = 0.5
		alpha = 0.5
		
		light = state[0]
		oncoming = state[1]
		cross_traffic = state[2]
		next_waypoint = state[3]
		anarchy_time = state[4]
		
		q_val_state = (('light', light), ('oncoming', oncoming), ('cross_traffic', cross_traffic),
					   ('next_waypoint', next_waypoint), ('anarchy_time', anarchy_time), action)
		
		q_state = self.q_values[q_val_state]
		self.next_waypoint = self.planner.next_waypoint()
		inputs = self.env.sense(self)
		deadline = self.env.get_deadline(self)
		updated = self.update_state(self.next_waypoint, inputs, deadline)
		choice, max_action = self.lookup_actions(updated) 
		
		new_value = q_state*(1-alpha) + alpha*(reward + (discount * max_action[0]))
		
		self.q_values[q_val_state] = new_value
		
	def initialize_qtable(self):
		light = ["red","green"]
		oncoming = ["left","forward","right",None]
		cross_traffic = [True, False]
		next_waypoint = ["left", "forward", "right", None]
		anarchy_time = [True, False]
		action = ["left", "forward", "right", None]
	
		q_values = {}
		state_list = []	
		for each_light in light:
			for each_oncoming in oncoming:
				for each_cross_traffic in cross_traffic:
					for each_next_waypoint in next_waypoint:
						for each_anarchy_time in anarchy_time:
							for each_action in action:
								state = (('light', each_light), ('oncoming', each_oncoming), 
										 ('cross_traffic', each_cross_traffic),('next_waypoint', each_next_waypoint),
										 ('anarchy_time', each_anarchy_time), each_action)
								state_list.append(state)
						
		for each in state_list:
			q_values[each] = 0
			
		return q_values
		
def run():
	"""Run the agent for a finite number of trials."""

    # Set up environment and agent
	e = Environment()  									# create environment (also adds some dummy traffic)
	a = e.create_agent(LearningAgent)  					# create agent
	e.set_primary_agent(a, enforce_deadline=True)  		# set agent to track

    # Now simulate it
	sim = Simulator(e, update_delay=0.01)  				# reduce update_delay to speed up simulation
	sim.run(n_trials=100)  								# press Esc or close pygame window to quit
	


if __name__ == '__main__':
    run()