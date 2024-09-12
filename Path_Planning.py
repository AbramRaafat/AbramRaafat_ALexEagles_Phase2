# -*- coding: utf-8 -*-
"""
Created on Wed Sep 11 15:43:05 2024

@author: abram raafat
"""

import tkinter as tk
from queue import PriorityQueue, Queue, LifoQueue
from functools import wraps
import random
from time import time





# Define form Constant
WINDOW_WIDTH = 400
WINDOW_HEIGHT = 400

start_node_COLOR = "darkred"
GOAL_COLOR = "gold"
OBSTICAL_COLOR = "black"
WALKABLE_COLOR = "white"
PATH_COLOR = "blue"
EXPANDED_COLOR = "lightblue"



class Node:
    
    def __init__(self, i, j):
        """
        argument:
        i -- the row index of the node 
        j -- the column index of the node
        """
        self.i = i 
        self.j = j 
        self.g = float('inf')  # Dijkstra Cost by default infinty
        self.h = float('inf')  # calc_heuristic cost for goal node by default infinty
        self.f = float('inf')  # Total cost by default infinty
        self.parent = None
        self.neighbor = []
        self.is_obstacle = False
        
    def __lt__(self,  other_node):
        """ 
        in case of A*  using the less than dunder to
        compare between two nodes for  PriorityQueue
        """
        return self.f < other_node.f
    
class MazeGUI:
    def __init__(self, window):
        self.window = window
        self.maze_size = (10, 10) # The default window size
        self.cell_size = 40 # The default cell size
        self.grid = []
        self.start_node = None
        self.end_node = None
        
        # Create a fix window size
        self.canvas = tk.Canvas(window, width=WINDOW_WIDTH, height=WINDOW_HEIGHT)
        self.canvas.pack()
        
        # Dynamic maze size
        self.row_input = tk.Entry(window)
        self.row_input.pack(side=tk.LEFT)
        self.row_input.insert(0, "10") # 10 is the default number of rows
        
        self.col_input = tk.Entry(window)
        self.col_input.pack(side=tk.LEFT)
        self.col_input.insert(0, "10") # 10 is the default number of columns
        
        self.set_size_button = tk.Button(window, text="Set Maze Size", command=self.set_maze_size)
        self.set_size_button.pack(side=tk.LEFT)
        

        # activate each algorithms
        self.solve_dfs_button = tk.Button(window, text="Solve with DFS", command=self.dfs)
        self.solve_dfs_button.pack(side=tk.LEFT)

        self.solve_bfs_button = tk.Button(window, text="Solve with BFS", command=self.bfs)
        self.solve_bfs_button.pack(side=tk.LEFT)

        self.solve_dijkstra_button = tk.Button(window, text="Solve with Dijkstra", command=self.dijkstra)
        self.solve_dijkstra_button.pack(side=tk.LEFT)

        self.solve_astar_button = tk.Button(window, text="Solve with A*", command=self.a_star)
        self.solve_astar_button.pack(side=tk.LEFT)
        
        self.performance_info = tk.Label(root, text="Time: 0s, Path Length: 0")
        self.performance_info.pack(side=tk.BOTTOM)


        self.create_gride()  # Create initial maze
    
    def create_gride(self):
        """
        create 2d matrix contains Node objects each 
        with it corresponding coordinate
        """
        
        self.grid = [[Node(row_ind, col_ind) for col_ind in range(self.maze_size[1])] for row_ind in range(self.maze_size[0])]
        self.start_node = self.grid[0][0]
        self.end_node = self.grid[self.maze_size[0]-1][self.maze_size[1]-1]
      
        
        solvable = False
        while not solvable:  # Repeat until we generate a solvable maze
            self.randomize_obstacles()  
            solvable = self.valid_grid()  
            
        self.reset_grid()
        self.draw_grid()
        
    def set_maze_size(self):
        try:
            rows = int(self.row_input.get())
            cols = int(self.col_input.get())
            self.maze_size = (rows, cols)

            # Dynamically calculate cell size to fit the fixed window size
            self.cell_size = min(WINDOW_WIDTH // cols, WINDOW_HEIGHT // rows)

            self.create_gride()
        except ValueError:
            print("Please enter valid numbers for rows and columns")
            
    def randomize_obstacles(self):
        """
        there is less than 30% a node be obstical
        the obstical node should have: 
        is_obstacle attribute --> True
        parrent attribute --> None
        
        """
        for row in range(self.maze_size[0]):
            for col in range(self.maze_size[1]):
                
                self.grid[row][col].is_obstacle = False  # Clear previous obstacles
                self.grid[row][col].parent = None  # Reset parent nodes

                # Randomly place obstacles except on the start_node and end_node positions
                if random.random() < 0.3 and (row, col) not in [(0, 0), (self.maze_size[0] - 1, self.maze_size[1] - 1)]:
                    self.grid[row][col].is_obstacle = True
    def valid_grid(self):
        """
        return True if a path found else return false
        """
        queue = Queue()
        queue.put(self.start_node)
        visited = set()

        while not queue.empty():
            current = queue.get()
            if current == self.end_node:  # If we reached the goal, it's solvable
                return True

            if current in visited:
                continue

            visited.add(current)

            for neighbor in self.get_neighbors(current):
                if neighbor.is_obstacle or neighbor in visited:
                    continue
                queue.put(neighbor)

        return False  # No path found
                        
    def reset_grid(self):
        
        for row in range(self.maze_size[0]):
            for col in range(self.maze_size[1]):
                node = self.grid[row][col]
                node.g = float('inf')  # Reset Dijkstra cost 
                node.h = float('inf')  # Reset calc_heuristic cost 
                node.f = float('inf')  # Reset total cost 
                node.parent = None  # Reset parent reference 
    def draw_grid(self):
       self.canvas.delete("all")
       for row in range(self.maze_size[0]):
           for col in range(self.maze_size[1]):
               x1 = col * self.cell_size
               y1 = row * self.cell_size
               x2 = x1 + self.cell_size
               y2 = y1 + self.cell_size

               color = WALKABLE_COLOR
               if self.grid[row][col].is_obstacle:
                   color = OBSTICAL_COLOR
               elif self.grid[row][col] == self.start_node:
                   color = start_node_COLOR
               elif self.grid[row][col] == self.end_node:
                   color = GOAL_COLOR

               self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black")             
    def draw_path(self, path):
        for node in path:
            if node != self.start_node and node != self.end_node:
                x1 = node.j * self.cell_size
                y1 = node.i * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=PATH_COLOR, outline="black")
                
        
    def draw(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            self.draw_grid()
            self.reset_grid()
            
            path = func(self, *args, **kwargs)
            
            if path:
                self.draw_path(path)  # Draw the final path after the algorithm completes
            return path
        return wrapper

    def measure_time_and_length(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            
            start_time = time()
            path = func(self, *args, **kwargs)
            end_time = time()
            del_time = end_time - start_time

      
            path_length = len(path)

            self.display_time_and_length(del_time, path_length)

            return path  # Return the path for any further processing if needed
        return wrapper   
    def expand_node(self, node):
        if node != self.start_node and node != self.end_node:
            x1 = node.j * self.cell_size
            y1 = node.i * self.cell_size
            x2 = x1 + self.cell_size
            y2 = y1 + self.cell_size
            self.canvas.create_rectangle(x1, y1, x2, y2, fill=EXPANDED_COLOR, outline="black")
        self.canvas.update()  # Update the canvas to show expanded nodes in real-time        
            
    def calc_heuristic(self, node):
        """
        return the manhaten calc_heuristic
        """
        return abs(node.i - self.end_node.i) + abs(node.j - self.end_node.j)        
            
                    

    @draw
    @measure_time_and_length
    def dfs(self):
      stack = LifoQueue()
      stack.put(self.start_node)
      visited = set()
      path = []
      while not stack.empty():
          current = stack.get()
          if current == self.end_node:
              path = self.reconstruct_path(current)
              break
          if current in visited:
              continue
          visited.add(current)
          self.expand_node(current)

          for neighbor in self.get_neighbors(current):
              if neighbor.is_obstacle or neighbor in visited:
                  continue
              neighbor.parent = current
              stack.put(neighbor)
      return path


    @draw
    @measure_time_and_length
    def bfs(self):
       self.draw_grid()
       self.reset_grid()  # Reset before each run
       queue = Queue()
       queue.put(self.start_node)
       visited = set()
       path = []

       while not queue.empty():
           current = queue.get()
           if current == self.end_node:
               path = self.reconstruct_path(current)
               break
           if current in visited:
               continue
           visited.add(current)
           self.expand_node(current)

           for neighbor in self.get_neighbors(current):
               if neighbor.is_obstacle or neighbor in visited:
                   continue
               neighbor.parent = current
               queue.put(neighbor)

       return path

   
    @draw
    @measure_time_and_length
    def dijkstra(self):
    
        self.reset_grid()  # Reset before each run
        self.draw_grid() # draw new grid each run
        pq = PriorityQueue()
        self.start_node.g = 0
        pq.put((self.start_node.g, self.start_node))
        visited = set()
        path = []

        while not pq.empty():
            _, current = pq.get()
            if current == self.end_node:
                path = self.reconstruct_path(current)
                break
            if current in visited:
                continue
            visited.add(current)
            self.expand_node(current)

            for neighbor in self.get_neighbors(current):
                if neighbor.is_obstacle or neighbor in visited:
                    continue
                tentative_g = current.g + 1
                if tentative_g < neighbor.g:
                    neighbor.g = tentative_g
                    neighbor.parent = current
                    pq.put((neighbor.g, neighbor))

        return path

   
    @draw
    @measure_time_and_length
    def a_star(self):
        """
        f(n) = g(n) + h(n)
        
        """
        pq = PriorityQueue()
        self.start_node.g = 0
        self.start_node.h = self.calc_heuristic(self.start_node)
        self.start_node.f = self.start_node.g + self.start_node.h
        pq.put((self.start_node.f, self.start_node))
        visited = set()
        path = []

        while not pq.empty():
            _, current = pq.get()
            if current == self.end_node:
                path = self.reconstruct_path(current)
                break
            if current in visited:
                continue
            visited.add(current)
            self.expand_node(current)

            for neighbor in self.get_neighbors(current):
                if neighbor.is_obstacle or neighbor in visited:
                    continue
                updated_g = current.g + 1
                if updated_g < neighbor.g:
                    neighbor.g = updated_g
                    neighbor.h = self.calc_heuristic(neighbor)
                    neighbor.f = neighbor.g + neighbor.h
                    neighbor.parent = current
                    pq.put((neighbor.f, neighbor))


        return path        
        
    def get_neighbors(self, node):
        neighbors = []
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        for direction in directions:
            new_row, new_col = node.i + direction[0], node.j + direction[1]
            if 0 <= new_row < self.maze_size[0] and 0 <= new_col < self.maze_size[1]:
                neighbors.append(self.grid[new_row][new_col])
        return neighbors

    def reconstruct_path(self, current):
        path = []
        while current:
            path.append(current)
            current = current.parent
        return path
    def display_time_and_length(self, elapsed_time, path_length):
         # Update the label with the time and path length
         self.performance_info.config(text=f"Time: {elapsed_time:.4f} seconds, Path Length: {path_length}") 

# Main Function
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Maze Solver with DFS, BFS, Dijkstra, and A*")
    app = MazeGUI(root)
    root.mainloop()
        
            
        
        
        