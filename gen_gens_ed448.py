# -*- coding: utf-8 -*-
import hashlib
import binascii
import sha3

b = 448
p = 2**448 - 2**224 - 1
q = 2**446 - 13818066809895115352007386748515426880336692474882178609894547503885
d = -39081 # The non-square element of F_p
cofactor = 4
I = [0,1]  # Edward curve has identity_element as Point (0,1)

def H(m):
  return hashlib.sha3_512(m).digest()

# for inversion modulo p, use this identity: x^(p-2) (mod p).
def inv(x):
  return expmod(x,p-2,p)

def expmod(b,e,m):
  if e == 0: return 1
  t = expmod(b,e/2,m)**2 % m
  if e & 1: t = (t*b) % m
  return t

# determine x by x = ± sqrt((1-y^2)/(1-dy^2))
def recover_x(y):
  xx = (1-y*y) * inv(1-d*y*y)
  x = expmod(xx, (p+1)/4, p) # x is now the candidate square root of x^2
  if (x*x - xx) % p != 0: raise Exception("no square root found")
  return x

def pointaddition(P,Q):
  x1 = P[0]
  y1 = P[1]
  x2 = Q[0]
  y2 = Q[1]
  x3 = (x1*y2+x2*y1) * inv(1+d*x1*x2*y1*y2)
  y3 = (y1*y2-x1*x2) * inv(1-d*x1*x2*y1*y2)
  return [x3 % p, y3 % p]

def scalarmult(P,e):
  if e == 0: return [0,1]
  Q = scalarmult(P,e/2)
  Q = pointaddition(Q,Q)
  if e & 1: Q = pointaddition(Q,P)
  return Q

def bit(h,i):
  return (ord(h[i/8]) >> (i%8)) & 1

# this is the formula for the twisted curve
def isoncurve(P):
  x = P[0]
  y = P[1]
  return (x*x + y*y - 1 - d*x*x*y*y) % p == 0

# similar to decodeLittleEndian from X25519, but works on bits rather than bytes
def decodeint(s):
  return sum(2**i * bit(s,i) for i in range(0,b))

def decodepoint(s):
  y = sum(2**i * bit(s,i) for i in range(0,b-1)) # encoded as the b-bit string
  x = recover_x(y)
  if x & 1 != bit(s,b-1): x = p-x # select the right square root x
  P = [x,y]
  if not isoncurve(P): raise Exception("decoding point that is not on curve")
  return P

def find_g(x):
    c = 0
    while True:
        ss = "%s%d" % (x, c)
        try:
            h = H(ss)
            point = decodepoint(h)
            g = scalarmult(point, cofactor)
            is_id = scalarmult(g, q)
            if is_id == I: # if P^cofactor^primeOrder == [0, 1]. The number of points of the twist is 4 times the prime q.
               return g, ss
        except Exception as e:
            pass
        c = c+1

generator2_x = "OTRv4 g2"

g2, sg2 = find_g(generator2_x)
print("g2")
print("x = " + format(g2[0], '#04x'))
print("y = " + format(g2[1], '#04x'))
print("sg2 = " + sg2)
