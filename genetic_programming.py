from random import random,randint,choice
from copy import deepcopy
from math import log
from chess_logic_by_thomasahle import *
from minimax import *

# values = {}
state = None

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
    print (' '*indent)+self.name
    for c in self.children:
      c.display(indent+1)
    

class paramnode:
  def __init__(self,idx):
    self.idx=idx

  def evaluate(self,inp):
    return inp[self.idx]
  def display(self,indent=0):
    print '%sp%d' % (' '*indent,self.idx)
    
    
class constnode:
  def __init__(self,v):
    self.v=v
  def evaluate(self,inp):
    return self.v
  def display(self,indent=0):
    # print '%s%d' % (' '*indent,self.v)
    print '%s%f' % (' '*indent,self.v)

class piecenode:
  def __init__(self, piece, name):
    self.piece = piece
    self.v=0
    # self.state = state
    # self.inp = None
    self.name = name
  def evaluate(self,inp):
    # inp.pieces_dict()
    # return self.v
    # self.inp = inp
    self.v = inp.pieces_dict()[self.piece]
    return inp.pieces_dict()[self.piece]
  def display(self,indent=0):
    # print '%s%d' % (' '*indent,self.v)
    # print (' '*indent)+self.name
    print (' '*indent) + self.name + " " + str(self.v)

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
    print (' '*indent)+self.name + " " + str(self.score)
    # for c in self.children:
    #   c.display(indent+1)

# boardScore = fwrapper(lambda )

addw=fwrapper(lambda l:l[0]+l[1],2,'add')
subw=fwrapper(lambda l:l[0]-l[1],2,'subtract') 
mulw=fwrapper(lambda l:l[0]*l[1],2,'multiply')

# my_pawns = fwrapper(lambda : state.pieces_dict()['P'], 0, 'my pawns')
# my_rooks = fwrapper(lambda : state.pieces_dict()['R'], 0, 'my rooks')
# my_knights = fwrapper(lambda : state.pieces_dict()['N'], 0, 'my knights')
# my_bishops = fwrapper(lambda : state.pieces_dict()['B'], 0, 'my bishops')
# my_queen = fwrapper(lambda : state.pieces_dict()['Q'], 0, 'my queen')
# my_king = fwrapper(lambda : state.pieces_dict()['K'], 0, 'my king')

# your_pawns = fwrapper(lambda : state.pieces_dict()['p'], 0, 'your pawns')
# your_rooks = fwrapper(lambda : state.pieces_dict()['r'], 0, 'your rooks')
# your_knights = fwrapper(lambda : state.pieces_dict()['n'], 0, 'your knights')
# your_bishops = fwrapper(lambda : state.pieces_dict()['b'], 0, 'your bishops')
# your_queen = fwrapper(lambda : state.pieces_dict()['q'], 0, 'your queen')
# your_king = fwrapper(lambda : state.pieces_dict()['k'], 0, 'your king')
def pieces(state):

  my_pawns = lambda : state.pieces_dict()['P']
  my_rooks = lambda : state.pieces_dict()['R']
  my_knights = lambda : state.pieces_dict()['N']
  my_bishops = lambda : state.pieces_dict()['B']
  my_queen = lambda : state.pieces_dict()['Q']
  my_king = lambda : state.pieces_dict()['K']

  your_pawns = lambda : state.pieces_dict()['p']
  your_rooks = lambda : state.pieces_dict()['r']
  your_knights = lambda : state.pieces_dict()['n']
  your_bishops = lambda : state.pieces_dict()['b']
  your_queen = lambda : state.pieces_dict()['q']
  your_king = lambda : state.pieces_dict()['k']

  my_pawns.__name__ = 'my_pawns'
  my_rooks.__name__ = 'my_rooks'
  my_knights.__name__ = 'my_knights'
  my_bishops.__name__ = 'my_bishops'
  my_queen.__name__ = 'my_queen'
  my_king.__name__ = 'my_king'

  your_pawns.__name__ = 'your_pawns'
  your_rooks.__name__ = 'your_rooks'
  your_knights.__name__ = 'your_knights'
  your_bishops.__name__ = 'your_bishops'
  your_queen.__name__ = 'your_queen'
  your_king.__name__ = 'your_king'

  piece_list = ([my_pawns, my_rooks, my_knights, my_bishops, my_queen, my_king, your_pawns, 
                your_rooks, your_knights, your_bishops, your_queen, your_king])

  return piece_list

def iffunc(l):
  if l[0]>0: return l[1]
  else: return l[2]
ifw=fwrapper(iffunc,3,'if')

def isgreater(l):
  if l[0]>l[1]: return 1
  else: return 0
gtw=fwrapper(isgreater,2,'isgreater')

flist=[addw,mulw,ifw,gtw,subw]

# def exampletree():
#   return node(ifw,[
#                   node(gtw,[paramnode(0),constnode(3)]),
#                   node(addw,[paramnode(1),constnode(5)]),
#                   node(subw,[paramnode(1),constnode(2)]),
#                   ]
#               )

# def makerandomtree(pc, state, maxdepth=4,fpr=0.5,ppr=0.6):
def makerandomtree(pc, state, maxdepth=4,fpr=0.5,ppr=0.6):

  # pieces = state.pieces_dict()
  if random.random()<fpr and maxdepth>0:
    f=choice(flist)
    children=[makerandomtree(pc,state, maxdepth-1,fpr,ppr) 
              for i in range(f.childcount)]
    return node(f,children)
  elif random.random()<ppr:
    # lst = pieces(state)
    # piece = choice(lst)
    new_list = state.pieces_dict()
    # return paramnode(randint(0,pc-1))
    # return node(piece, None)
    # return node(piece, state)
    # return piecenode(state.pieces_dict()['p'], "your pawns")
    piece = random.choice(list(new_list))
    return choice([piecenode(piece, piece), eval_node(state)])
    # return piecenode(piece(), piece.__name__)
  else:
    return choice([constnode(random.uniform(0, 1))])

    # return constnode(randint(0,10))

def material_difference(state):
  # for item in state.board:
  #   if 
  return 0
              

# def hiddenfunction(x,y):
#     return x**2+2*y+3*x+5

# def buildhiddenset():
#   rows=[]
#   for i in range(200):
#     x=randint(0,40)
#     y=randint(0,40)
#     rows.append([x,y,hiddenfunction(x,y)])
#   return rows

def scorefunction(tree,s):
  dif=0
  for data in s:
    v=tree.evaluate([data[0],data[1]])
    dif+=abs(v-data[2])
  return dif


def mutate(t,pc,probchange=0.1):
  if random()<probchange:
    return makerandomtree(pc, state)
  else:
    result=deepcopy(t)
    if hasattr(t,"children"):
      result.children=[mutate(c,pc,probchange) for c in t.children]
    return result

def crossover(t1,t2,probswap=0.7,top=1):
  if random()<probswap and not top:
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
  
    

def evolve(state,popsize,rankfunction,maxgen=500,
           mutationrate=0.1,breedingrate=0.4,pexp=0.7,pnew=0.05):
  # Returns a random number, tending towards lower numbers. The lower pexp
  # is, more lower numbers you will get
  def selectindex():
    return int(log(random())/log(pexp))

  # Create a random initial population
  population=[makerandomtree(pc, state) for i in range(popsize)]
  for i in range(maxgen):
    scores=rankfunction(population)
    print scores[0][0]
    if scores[0][0]==0: break
    
    # The two best always make it
    newpop=[scores[0][1],scores[1][1]]
    
    # Build the next generation
    while len(newpop)<popsize:
      if random()>pnew:
        newpop.append(mutate(
                      crossover(scores[selectindex()][1],
                                 scores[selectindex()][1],
                                probswap=breedingrate),
                        pc,probchange=mutationrate))
      else:
      # Add a random node to mix things up
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


def tournament(pl):
  # Count losses
  losses=[0 for p in pl]
  
  # Every player plays every other player
  for i in range(len(pl)):
    for j in range(len(pl)):
      if i==j: continue
      
      # Who is the winner?
      winner=gridgame([pl[i],pl[j]])
      
      # Two points for a loss, one point for a tie
      if winner==0:
        losses[j]+=2
      elif winner==1:
        losses[i]+=2
      elif winner==-1:
        losses[i]+=1
        losses[i]+=1
        pass

  # Sort and return the results
  z=zip(losses,pl)
  z.sort()
  return z      

# class humanplayer:
#   def evaluate(self,board):

#     # Get my location and the location of other players
#     me=tuple(board[0:2])
#     others=[tuple(board[x:x+2]) for x in range(2,len(board)-1,2)]
    
#     # Display the board
#     for i in range(4):
#       for j in range(4):
#         if (i,j)==me:
#           print 'O',
#         elif (i,j) in others:
#           print 'X',
#         else:
#           print '.',
#       print
      
#     # Show moves, for reference
#     print 'Your last move was %d' % board[len(board)-1]
#     print ' 0'
#     print '2 3'
#     print ' 1'
#     print 'Enter move: ',
    
#     # Return whatever the user enters
#     move=int(raw_input())
#     return move


class fwrapper:
  def __init__(self,function,params,name):
    self.function=function
    self.childcount=param
    self.name=name
    
#flist={'str':[substringw,concatw],'int':[indexw]}
flist=[addw,mulw,ifw,gtw,subw]
