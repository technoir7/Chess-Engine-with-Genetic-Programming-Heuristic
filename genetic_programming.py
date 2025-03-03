from random import random,randint,choice
from copy import deepcopy
from math import log
import chess_logic_by_thomasahle
from minimax import *

state = None
# MATE_LOWER = piece['K'] - 10*piece['Q']
# MATE_UPPER = piece['K'] + 10*piece['Q']
MATE_LOWER = 50710
MATE_UPPER = 69290

class fwrapper:
  def __init__(self,function,childcount,name):
    self.function=function
    self.childcount=childcount
    self.name=name

class node:
  def __init__(self,fw,children):
    self.function=fw.function
    self.name=fw.name
    self.children=children

  def evaluate(self,inp):    
    results=[n.evaluate(inp) for n in self.children]
    return self.function(results)
  def display(self,indent=0):
    print((' '*indent)+self.name)
    for c in self.children:
      c.display(indent+1)
    

class paramnode:
  def __init__(self,idx):
    self.idx=idx

  def evaluate(self,inp):
    return inp[self.idx]
  def display(self,indent=0):
    print('%sp%d' % (' '*indent,self.idx))
    
    
class constnode:
  def __init__(self,v):
    self.v=v
  def evaluate(self,inp):
    return self.v
  def display(self,indent=0):
    # print '%s%d' % (' '*indent,self.v)
    print('%s%f' % (' '*indent,self.v))

class piecenode:
  def __init__(self, piece, name):
    self.piece = piece
    self.value=0
    self.name = name
  def evaluate(self,inp):
    # inp.pieces_dict()
    self.value = inp.pieces_dict()[self.piece]
    return inp.pieces_dict()[self.piece]
  def display(self,indent=0):
    # print '%s%d' % (' '*indent,self.v)
    # print (' '*indent)+self.name
    print((' '*indent) + self.name + " " + str(self.value))

class eval_node:
  def __init__(self,state):
    # self.function=fw.function
    self.state = state
    self.name="evaluation node"
    self.score = 0
    # self.children=children

  def evaluate(self,inp):    
    # results=[n.evaluate(inp) for n in self.children]
    # print("evaluating")
    self.score = inp.evaluation()
    return self.score
  def display(self,indent=0):
    print((' '*indent)+self.name + " " + str(self.score))
    # for c in self.children:
    #   c.display(indent+1)

# boardScore = fwrapper(lambda )

addw=fwrapper(lambda l:l[0]+l[1],2,'add')
subw=fwrapper(lambda l:l[0]-l[1],2,'subtract') 
mulw=fwrapper(lambda l:l[0]*l[1],2,'multiply')



def match(state, players):
  pos = state
  print("game")
  score = 0

  # heuristic = makerandomtree(5, pos)
  # heuristic.display()
  # searcher = Minimax(heuristic)
  player1 = Minimax(players[0])
  player2 = Minimax(players[1])
  # players[0].display()
  # players[1].display()
  moves = 0
  while moves < 7:
    # print(pos.pieces_dict())
    # print pos.score
    # chess_logic_by_thomasahle.print_pos(pos)

    if pos.score <= -MATE_LOWER:
      return 1
      # print("You lost")
      break

    move, score = player1.search(pos, secs=2)

    # # We query the user until she enters a (pseudo) legal move.
    # move = None
    # while move not in pos.gen_moves():
    #     match = re.match('([a-h][1-8])'*2, input('Your move: '))
    #     if match:
    #         move = parse(match.group(1)), parse(match.group(2))
    #     else:
    #         # Inform the user when invalid input (e.g. "help") is entered
    #         print("Please enter a move like g8f6")
    pos = pos.move(move)

    # # After our move we rotate the board and print it again.
    # # This allows us to see the effect of our move.
    # print_pos(pos.rotate())
    # pos.rotate()
    # chess_logic_by_thomasahle.print_pos(pos.rotate())
    # print pos.score

    # print(MATE_LOWER)
    # print(pos.score)

    if pos.score <= -MATE_LOWER:
      # print("You won")
      return 0
      break

    # Fire up the engine to look for a move.
    move, score = player2.search(pos, secs=2)
    # move, score = searcher.search(pos, heuristic)

    if score == MATE_UPPER:
      print("Checkmate!")

    # # The black player moves from a rotated position, so we have to
    # # 'back rotate' the move before printing it.
    # print("My move:", render(119-move[0]) + render(119-move[1]))
    pos = pos.move(move)
    moves += 1
    # print(moves)
  # print("final score")
  # print(score)
  if pos.score > 0:
    return 1
  elif pos.score < 0:
    return 0
  return -1

def iffunc(l):
  if l[0]>0: return l[1]
  else: return l[2]
ifw=fwrapper(iffunc,3,'if')

def isgreater(l):
  if l[0]>l[1]: return 1
  else: return 0
gtw=fwrapper(isgreater,2,'isgreater')

flist=[addw,mulw,ifw,gtw,subw]

# def makerandomtree(pc, state, maxdepth=4,fpr=0.5,ppr=0.6):
def makerandomtree(pc, state, maxdepth=4,fpr=0.5,ppr=0.6):
  if state is None:
    state = chess_logic_by_thomasahle.Position(chess_logic_by_thomasahle.initial, 0, (True,True), (True,True), 0, 0)

  new_list = state.pieces_dict()
  piece = random.choice(list(new_list))
  if random.random()<fpr and maxdepth>0:
    f=choice(flist)
    children=[makerandomtree(pc,state, maxdepth-1,fpr,ppr) 
              for i in range(f.childcount)]
    return node(f,children)
  elif random.random()<ppr:
    # lst = pieces(state)
    # piece = choice(lst)
    # return paramnode(randint(0,pc-1))
    # return node(piece, None)
    # return node(piece, state)
    # return piecenode(state.pieces_dict()['p'], "your pawns")
    return choice([piecenode(piece, piece), eval_node(state)])
    # return piecenode(piece(), piece.__name__)
  else:
    return choice([constnode(random.uniform(0, 1)),eval_node(state)])

    # return constnode(randint(0,10))


def scorefunction(tree,s):
  dif=0
  for data in s:
    v=tree.evaluate([data[0],data[1]])
    dif+=abs(v-data[2])
  return dif


def mutate(t,pc,probchange=0.1):
  if random.random()<probchange:
    return makerandomtree(pc, state)
  else:
    result=deepcopy(t)
    if hasattr(t,"children"):
      result.children=[mutate(c,pc,probchange) for c in t.children]
    return result

def crossover(t1,t2,probswap=0.7,top=1):
  if random.random()<probswap and not top:
    return deepcopy(t2) 
  else:
    result=deepcopy(t1)
    if hasattr(t1,'children') and hasattr(t2,'children'):
      result.children=[crossover(c,choice(t2.children),probswap,0) 
                       for c in t1.children]
    return result

def getrankfunction(dataset):
  def rankfunction(population):
    scores=[(scorefunction(t,dataset),t) for t in population]
    scores.sort()
    return scores
  return rankfunction
  
    

def evolve(state, pc,popsize,rankfunction,maxgen=500,
           mutationrate=0.1,breedingrate=0.4,pexp=0.5,pnew=0.05):
  # Returns a random number, tending towards lower numbers. The lower pexp
  # is, more lower numbers you will get
  def selectindex():
    return int(log(random.random())/log(pexp))


  # Create a random initial population
  population=[makerandomtree(pc, state) for i in range(popsize)]
  for i in range(maxgen):
    print("inside evolve for loop")
    scores=rankfunction(state, population)
    print(scores[0][0])
    scores_length = len(scores)
    if scores[0][0]==0: break
        
    # The two best always make it
    newpop=[scores[0][1],scores[1][1]]
    
    # Build the next generation
    while len(newpop)<popsize:
      random_num = random.random()
      print(random_num)
      print("inside while")
      if random_num>pnew:
        print("inside while and if statement")
        print(scores_length)
        newpop.append(mutate(
                      crossover(scores[selectindex() % scores_length][1],
                                 scores[selectindex() % scores_length][1],
                                probswap=breedingrate),
                        pc,probchange=mutationrate))
      else:
      # Add a random node to mix things up
        print("inside else")
        newpop.append(makerandomtree(pc, state))
        
    population=newpop
  scores[0][1].display()    
  return scores[0][1]


# def gridgame(p):
#   # Board size
#   max=(3,3)
  
#   # Remember the last move for each player
#   lastmove=[-1,-1]
  
#   # Remember the player's locations
#   location=[[randint(0,max[0]),randint(0,max[1])]]
  
#   # Put the second player a sufficient distance from the first
#   location.append([(location[0][0]+2)%4,(location[0][1]+2)%4])
#   # Maximum of 50 moves before a tie
#   for o in range(50):
  
#     # For each player
#     for i in range(2):
#       locs=location[i][:]+location[1-i][:]
#       locs.append(lastmove[i])
#       move=p[i].evaluate(locs)%4
      
#       # You lose if you move the same direction twice in a row
#       if lastmove[i]==move: return 1-i
#       lastmove[i]=move
#       if move==0: 
#         location[i][0]-=1
#         # Board wraps
#         if location[i][0]<0: location[i][0]=0
#       if move==1: 
#         location[i][0]+=1
#         if location[i][0]>max[0]: location[i][0]=max[0]
#       if move==2: 
#         location[i][1]-=1
#         if location[i][1]<0: location[i][1]=0
#       if move==3: 
#         location[i][1]+=1
#         if location[i][1]>max[1]: location[i][1]=max[1]
      
#       # If you have captured the other player, you win
#       if location[i]==location[1-i]: return i
#   return -1


def tournament(state, pl):
  # Count losses
  losses=[0 for p in pl]
  
  # Every player plays every other player
  for i in range(len(pl)):
    for j in range(len(pl)):
      if i==j: continue
      
      # Who is the winner?
      winner=match(state, [pl[i],pl[j]])
      print("tournament inside nested loop")
      
      # Two points for a loss, one point for a tie
      if winner==0:
        losses[j]+=2
      elif winner==1:
        losses[i]+=2
      elif winner==-1:
        losses[i]+=1
        losses[j]+=1
        pass

  # Sort and return the results
  z=zip(losses,pl)
  z.sort()
  return z      

class fwrapper:
  def __init__(self,function,params,name):
    self.function=function
    self.childcount=param
    self.name=name
    
#flist={'str':[substringw,concatw],'int':[indexw]}
flist=[addw,mulw,ifw,gtw,subw]
