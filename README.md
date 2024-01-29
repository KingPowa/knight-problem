# Knight Path Finder

## Problem Description

```
A knight is in a known cell on an empty chessboard and needs to reach another known cell.

Write a Python program that can take as input the two positions on the chessboard and returns as output:

* the set of all minimum-length sequences to move the piece from the initial cell to the final cell;
* a graphviz/dot file of the previous "all shortest path" graph.

Your code can use external libraries or you can avoid them as you wish. 
The case do not require machine learning specific algorithms or approaches.

Please provide also:

* a `requirements.txt`, if needed;
* a `Dockerfile` for the full environment, if you know how to create a `Dockerfile`;
* a short `README.md`.
```

This application finds the shortest paths for a knight on a chessboard from a given starting position to a target position.

## Installation

Clone the repository to your local machine:

```bash
git clone <repository-url>
```

Navigate to the cloned directory:

```bash
cd <cloned-directory>
```

## Usage
### Command Line Arguments

The script knight.py accepts the following arguments:

    row: Row of the chessboard. Must be 0 <= row < board_width (default = 8)
    column: Column of the chessboard. Must be 0 <= column < board_length (default = 8)
    target_row: Target row on the chessboard.
    target_column: Target column on the chessboard.
    -bw or --board_width: Custom width of the chessboard (default = 8)
    -bl or --board_length: Custom length of the chessboard (default = 8)

### Running the Script

To run the script, use the following command:

```bash
python knight.py [row] [column] [target_row] [target_column] [-bw board_width] [-bl board_length]
```

For example:

```bash
python knight.py 1 1 4 3 -bw 8 -bl 8
```

the `-bw` and `-bl` parameters are optionals and allow for bigger chessboard.

## Using Docker

A Dockerfile is provided for containerization of the application.
### Building the Docker Image

To build the Docker image, run:

```bash
docker build -t knight-simulation .
```

### Running the Container

To run the application inside a Docker container, use:

```bash
docker run -v [folder_path]:/app/knight_simulation/graphviz_output -e row=1 -e col=1 -e target_row=4 -e target_col=3 -e board_width=8 -e board_length=8 knight-simulation
```

Where `folder_path` represents the path where we want the result.
For example:

```bash
docker run -v .:/app/knight_simulation/graphviz_output -e row=1 -e col=1 -e target_row=4 -e target_col=3 -e board_width=8 -e board_length=8 knight-simulation
```

You can customize the environment variables (row, col, target_row, target_col, board_width, board_length) as you wish.