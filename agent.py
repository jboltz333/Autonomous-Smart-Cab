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

# GRID:
# 8 across X 6 down

"""
 1. The idea here is that the agent should learn to follow the next_waypoint 
    whenever traffic allows it to, without you telling it anything about how 
    the traffic laws work.
 2. Write some methods to keep track of the agent's performance
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

"""
 1. If the light is "red", and the planner tell you to go 'forward', and deadline= 10, what should the agent do? 
   (stop and wait for the light to turn 'green' for example, because in the past it received -1 when trying to run the red light)
 2. If the light is 'green', and the planner recommends you to go 'forward', what should be the optimum action?
    (well, go 'forward')
 3. etc...
The agent should learn from the rewards it received in the past and figure out the best way to act (and thus get maximum reward) 
if the same situation happens again.
"""

"""
For each of those pieces of information about the state, think about how many different values there are. 
Again, try thinking about how often the agent will visit each state--it'll need to visit each state more than four times in order 
to learn the relative value of each action
"""

"""
action = random.choice(possibledirections)

# Execute action and get reward
reward = self.env.act(self, action)
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
This refers to the agent's internal state, not what information the environment has about it. If you update self.state there, 
it'll be shown in the GUI screen.

E.g.:
self.state = "Foo"
"""

class LearningAgent(Agent):
	"""An agent that learns to drive in the smartcab world."""

	def __init__(self, env):
		super(LearningAgent, self).__init__(env)  			# sets self.env = env, state = None, next_waypoint = None, and a default color
		self.color = 'red'  								# override color
		self.planner = RoutePlanner(self.env, self)  		# simple route planner to get next_waypoint
        # TODO: Initialize any additional variables here
		
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
		updated = self.update_state(self.next_waypoint, inputs, deadline)

		valid_actions = [None, 'forward', 'left', 'right']
		choice = random.choice(valid_actions[:])
				
        # TODO: Select action according to your policy
		action = choice

        # Execute action and get reward
		reward = self.env.act(self, action)
		
		# TODO: Learn policy based on state, action, reward
		print "LearningAgent.update(): deadline = {}, inputs = {}, action = {}, reward = {}".format(deadline, inputs, action, reward)  # [debug]
		
	def update_state(self, self.next_waypoint, inputs, deadline):
		left = inputs['left']
		oncoming = inputs['oncoming']
		light = inputs['light']
		
		if deadline <= 10:
			anarchytime = True
		else:
			anarchytime = False
		
		if left != 'straight':
			left = False 
		else:
			left = True
		
		state = [light, oncoming, left, self.next_waypoint, anarchytime]


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
