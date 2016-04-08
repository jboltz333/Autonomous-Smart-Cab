import random
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator


# PROCESSES:
# 1. Next waypoint location, relative to current location and heading
# 2. Intersection state(traffic light and presence of cars)
# 3. Current deadline value(time steps remaining)
# 4. And produces some random move/action
# 5. If enforce_deadline set to False, you have unlimited time
# 6. Current state/action taken and reward/penalty earned shown in simulator

# RULES:
# 1. No stopping at green unless have to
# 2. As you get closer, more reward (closer == distance)
# 3. Higher penalty as steps increase
# 4. High penalty for accident
# 5. Reward for successful right on red
# 6. Reward for successful left on green

# INPUTS:
# 1. light 		== red/green
# 2. oncoming 	== none/right/left/straight
# 3. left 		== none/right/left/straight
# 4. right 		== none/right/left/straight

# OUTPUTS:
# 5. action 	== none/right/left/straight
# 6. reward 	== integer value
# 7. timer      == integer value


class LearningAgent(Agent):
	"""An agent that learns to drive in the smartcab world."""

	def __init__(self, env):
		super(LearningAgent, self).__init__(env)  			# sets self.env = env, state = None, next_waypoint = None, and a default color
		self.color = 'red'  								# override color
		self.planner = RoutePlanner(self.env, self)  		# simple route planner to get next_waypoint
        # TODO: Initialize any additional variables here
		light,oncoming,right,left,choice = 0,0,0,0,0
		
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
		light = inputs['light']
		oncoming = inputs['oncoming']
		right = inputs['right']
		left = inputs['left']
		valid_actions = [None, 'forward', 'left', 'right']
		
		if light == 'green':
			if oncoming == None:
				choice = random.choice(valid_actions[1:])
			else:
				if oncoming == 'right':
					choice = random.choice(valid_actions[0])
				else:
					valid_actions = [None,'straight','right']
					choice = random.choice(valid_actions[:])
		else:
			if left == 'straight':
				choice = random.choice(valid_actions[0])
			else:
				valid_actions = [None,'right']
				choice = random.choice(valid_actions[:])
				
		
        # TODO: Select action according to your policy
		action = choice

        # Execute action and get reward
		reward = self.env.act(self, action)

        # TODO: Learn policy based on state, action, reward
		print "LearningAgent.update(): deadline = {}, inputs = {}, action = {}, reward = {}".format(deadline, inputs, action, reward)  # [debug]


def run():
    """Run the agent for a finite number of trials."""

    # Set up environment and agent
    e = Environment()  									# create environment (also adds some dummy traffic)
    a = e.create_agent(LearningAgent)  					# create agent
    e.set_primary_agent(a, enforce_deadline=True)  		# set agent to track

    # Now simulate it
    sim = Simulator(e, update_delay=2.0)  				# reduce update_delay to speed up simulation
    sim.run(n_trials=10)  								# press Esc or close pygame window to quit


if __name__ == '__main__':
    run()
