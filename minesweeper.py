import itertools
import random
import copy

class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """

        #If the number of cells is equal to number of mines (and there is at least one mine)
        #then all cells must be mines

        mineCount = self.count        
        
        if (len(self.cells) == mineCount) and (mineCount > 0):
            #Returns all cells
            return self.cells
        
        return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """

        #If sentence contains no mines then all cells in sentence must be safe

        mineCount = self.count
        
        if (mineCount == 0):
            return self.cells

        return set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """

        #Loops through cells
        for item in self.cells:
            #Checks to see if cell matches the "mine"
            if (item == cell):
                #Removes cell from sentence
                self.cells.remove(cell)                

                #Reduces the mine count by 1
                if (self.count > 0):
                    self.count -= 1
                else:
                    self.count = 0

                return
                

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """

        
        #Loops through cells
        for item in self.cells:
            #Checks to see if cell matches the confimed "safe" cell
            if (item == cell):
                #Removes cell from sentence
                self.cells.remove(cell)                

                return

class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """

        #Marks the cell as a move that has been made
        self.moves_made.add(cell)
        #Marks the cell as safe
        self.mark_safe(cell)

        #Creates new sentence and adds to AI's knowledge base
        neighbours = set()

        #Gets coords of current cell
        row = cell[0]
        column = cell[1]

        #Checks all cells and identifies neighbours by checking cells within 1 cell
        #of current cell
        for x in range(0, self.width):
            for y in range(0, self.height):
                #Adds adjacent cells that haven't been set as safe              
                if ((y,x) not in self.safes):
                    if (abs(row - y) == 1) and (abs(column - x) == 1):
                        neighbours.add((y, x))
                    elif (abs(row - y) == 0) and (abs(column - x) == 1):
                        neighbours.add((y, x))
                    elif (abs(row - y) == 1) and (abs(column - x) == 0):
                        neighbours.add((y, x))

        #Creates new sentence using the new neighbours and adds to knowledge base
        newSentence = Sentence(neighbours, count)
        self.knowledge.append(newSentence)

        #Mark additional cells as safe or as mines if concludable
        for sentence in self.knowledge:
            #Attempts to find known mines from sentence
            mines = sentence.known_mines()
            #Creates deep-copy of sentence
            tempSentenceCells = copy.deepcopy(sentence.cells)

            #Checks the sentence cells for mines and marks them if necessary
            for cell in tempSentenceCells:
                if (cell in mines):
                    self.mark_mine(cell)

            #Attempts to find known safes from sentence
            safes = sentence.known_safes()

            #Checks the sentence cells for safes and marks them if necessary
            for cell in tempSentenceCells:
                if (cell in safes):
                    self.mark_safe(cell)

        tempKnowledge = []
        
        #Creates new sentences using inference rules

        #Gets two sentences from knowledge base
        for first in self.knowledge:
            for second in self.knowledge:                
                #Checks if one sentence is a sub-set of the other
                if first.cells.issubset(second.cells):
                    #If the first and second sentences are the same then attempt is passed
                    if (first.cells == second.cells):
                        pass
                    #If either of the sentences have zero mines then attempt is passed
                    elif (first.count == 0) or (second.count == 0):
                        pass
                    #If either of the sentences have zero cells than attempt is passed
                    elif (len(first.cells) == 0) or (len(second.cells) == 0):
                        pass
                    else:                       
                        #Removes common cells and calculates new mine count to form a new sentence   
                        newSentence = Sentence(second.cells - first.cells, second.count - first.count)
                        tempKnowledge.append(newSentence)

        #Adds new sentences to knowledge base
        for sentence in tempKnowledge:
            self.knowledge.append(sentence)
                    

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """

        #Checks all the cells that are known to be safe and checks to see if there is one that
        #hasn't been used yet
        for cell in self.safes:
            if (cell not in self.moves_made):
                #Returns safe cell that hasn't been used
                return cell
        
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """

        #Loops through all cells
        for x in range(self.height):
            for y in range(self.width):
                cell = (x, y)

                #Returns a cell that isn't a mine and that hasn't been used yet
                if (cell not in self.moves_made) and (cell not in self.mines):
                    return cell
        
        return None
