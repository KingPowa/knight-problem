# Knight Path Extension

## Problem Description

```
Write a short markdown file named `NOTES.md` which should contain a description in English on how you would extend you previous script, showing some knowledge of the previously listed topics.

* Python
* Machine Learning / Deep Learning (at least one of the following):
	* object detection;
	* object tracking;
	* time series anomaly detection;
	* tabular data classification;
	* reinforcement learning;
	* transformers.
* Systems:
	* AWS;
	* Docker / Docker Compose;
	* distributed architectures.
* Edge Computing.

You don't have to write something about every subject: choose a subset of them and be creative.

Trivial example: how could you create a good dataset to write a classifier for valid knight moves? Or how could you turn your script into a secure cloud service?

The more topics you can link together or the more creative you are in describing possible lines of research and development, the better. 😃
```

## Extension of the Knight Path Problem

### Blocking cells, unknown target, unknown bounds

An interesting extension of the problem involves a chessboard with unknown bounds and target cells. In this scenario, the agent (the knight) also encounters pieces that may block its path. This becomes a non-trivial problem. Algorithms like Dijkstra and A* are ineffective here, as they require known target cells for their heuristics.
Using again BFS (Breadth-First Search) is one approach. However, it becomes impractical for large chessboards, as it requires maintaining a board representation that can be memory-intensive.
Introducing and additional constraint of the "dynamicity" of the blocking elements may finally justify the application of RL. If the target changes, even deterministically, BFS becomes impractical in a large environment. The best path would constantly change during execution.

With this setting, I would apply an RL algorithm following these rules:
- **State Space**: for the state space, it really depends on what the knight can observe. If in the action range the knight may observe the presence of blocking piece (which means, in the square formed by the cells which he would end up in by executing an L-action _a_), then I would likely encode this info in the state space, as well as a "sequence" of performed actions, time elapsed (number of moves) and history of rewards. This may give information to the agent regarding the trajectory he is following in the board. Constructing an internal representation of the chessboard may also be a possible solution for keeping track of the state. For instance, the agent might use a relative position to its initial spot (marked as 0,0). But, this depends on the board size: if it's too large, this method becomes impractical.
- **Action Space**: we will have a set of 8 actions available at each step. Since the environment is not observable until an action is performed, the action spaces remains always the same;
- **Reward**: the environment allows for the construction of a suitable reward. I would likely assign an increasingly negative reward for each step performed, which can be furtherly worsened by possible action that leads to blocking elements. A positive reward would be given if the end location is reached;
- **Action Selection**: without considering yet the algorithm, it is important to perform here proper exploration. I would adopt an exploration strategy such as epsilon-greedy strategy/Upper confidence bound.
- **Algorithm**: the algorithm to choose here is non trivial. Handling an history-based state representation requires, in my opinion, an approach that is able to retain historical information, so that the agent knows how to deal with the environment. Deep Q-Network seems a good approach here, as it allows to deal with the arbitrarily large state spaces and with the lack of information. Since past choices are really important here, I would also apply Experience Replay to allow sampling of old trajectories and train the network with past experience. The network could be used to "handle" sequential data (the history-based state) via the adoption of network like Recurrent Neural Network (preferably LSTM based) or even transformers.

Anyway, this extension is quite complex and would require a lot of time to obtain a fairly good approach.

## Live Chessboard Problem

If, instead, the objective would be to make the challenge more interesting, a possible extension would be to map the problem to a real-life board. Basically, an entire system could be created with the objective of tracking the movement on the board, represent them in an engine and visualize possible routes from that position which can be used to reach a target cell.

This non trivial application would require some steps:

### Tracking system

The tracking system would be composed by a possible HD camera that detects movement on the board. This image is taken after each movement and transferred to processing system. The processing system would have the duty of using a framework for analysing the image, detect the knight position and translate the board to an encoded representation (for example, a bit like representation which is quite compact).

My choice in this case would be
- _OpenCV_ as a tool for analysing the board. This would be used to take the image, transform it in a suitable format (for example, scaling it for consistent representation of the board) and use some segmentation/contour detection approach for identifying the knight and the board;
- _AWS Lambda_ for providing the functionalities of the tracking system. For example, the part that should execute openCV could be an AWS Lambda that take the image and outputs the representation. If security is a concern, some sort of local processing (_Edge device_) could be used before sending the data to the pathfinding module, so that the sensible data is processed before reaching an external system (as AWS would be on cloud);
- _A RESTful API_ that can be used by the camera/edge device to communicate with the AWS Lambda service for the pathfinding module. 
- _Detection System_ (Optional) for enhanced accuracy in detection. For example, a network like YOLO can be used for real time tracking of the knight during its movement, if instead of a camera we have a device that captures the images as a sequence (a video).

### Pathfinding engine

Another subsystem would take the representation and translate it to a set of paths, in a way similar to this script. This representation should follow a precise format, which can be used by other system for visualisation.

For this, I would use a version of my script with enhanced capabilities, probably using a more efficient representation and serving it not as a script but as a function with predefined input/output format. This would run on an AWS Lambda service.

### Visualisation Engine

The visualisation system would take the representation from the AWS Lambda service and present it to the end user. This can be done by providing a simple RESTful API to the AWS Lambda, so that the application can receive the shortest paths and the knight position from the system and represent it.

### Further Enhancements

In general, possible tweaks I would apply are:
- Ensuring API provides a strong authentication method and data encription between source and pathfinding engine;
- Integration of "fallback" mechanism in case the YOLO/openCV systems fails. For example, both a mechanism that infers if a predicted state is coherent (misplaced pieces) and a method for recomputing the board (asking for new image) would be extremely useful;


