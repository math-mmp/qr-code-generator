from dataTables import alphanumericValues as aVs
from dataTables import errorCorretionLevels as eCLs
from dataTables import characterCapacities as cCs
from dataTables import modeIndicators as mIs
from dataTables import characterCountIndicators as cCIs
from dataTables import errorCorrectionCodeWordsBlockInformation as eCCWBI
from dataTables import requiredRemainderBits as rRBs
from dataTables import alignmentPatternLocations as aPLs
from dataTables import formatInformationString as fISs
from dataTables import versionInformationStrings as vISs

from more_itertools import roundrobin
from tkinter import filedialog
from random import randint
from math import floor
import numpy as np
import cv2

class QRCode:
  def __init__(self, text):
    self.text = text
    self.errorCorretionLevel = None
    self.encodingMode = None
    self.version = None
    self.__bitString = None
    self.__logAntilog = []
    self.__generatorPolynomial = []
    self.__messagePolynomial = []
    self.__errorCorrectionCodewords = []
    self.__finalMessage = []
    self.size = None
    self.__matrix = []
    self.__mask = None

  """ Step 1: Data Analysis ✔️ """ 
  def __dataAnalysis(self):
    if self.text.isnumeric():
      self.encodingMode = 'numeric'
    elif all(character in aVs for character in self.text):
      self.encodingMode = 'alphanumeric'
    else:
      self.encodingMode = 'byte'

  """ Step 2: Data Encoding ✔️ """
  def __dataEncoding(self):
    # Step 2.1: Choose the Error Correction Level ✔️
    # Step 2.2: Determine the Smallest Version for the Data ✔️
    ## I chose to prioritize the version over the error correction level
    for i in range(40):
      for j in range(3, -1, -1):
        if cCs[self.encodingMode][j][i] >= len(self.text):
          self.version = i + 1
          self.errorCorretionLevel = eCLs[j]
          break
      if self.version != None:
        break

    # Step 2.3: Add the Mode Indicator ✔️
    modeIndicator = mIs[self.encodingMode]
    self.__bitString = modeIndicator

    # Step 2.4: Add the Character Count Indicator ✔️
    if self.version <= 9:
      characterCountIndicatorSize = cCIs[self.encodingMode][0]
    elif 10 <= self.version <= 26:
      characterCountIndicatorSize = cCIs[self.encodingMode][1]
    else:
      characterCountIndicatorSize = cCIs[self.encodingMode][2]
    characterCountIndicator = '{:0{size}b}'.format(len(self.text), size = characterCountIndicatorSize)
    self.__bitString += characterCountIndicator

    # Step 2.5: Encode Using the Selected Mode ✔️
    groups = []
    if self.encodingMode == 'numeric':
      for digits in range(0, len(self.text), 3):
        groups.append(self.text[digits:digits + 3])
      binaryBits = (4, 7, 10)
      encodedData = ''.join('{:0{size}b}'.format(int(x), size = binaryBits[len(str(x))-1]) for x in groups)
    elif self.encodingMode == 'alphanumeric':
      pairs = []
      for digits in range(0, len(self.text), 2):
         pairs.append(self.text[digits:digits + 2])
      groups = [(45*aVs.index(x[0])) + aVs.index(x[1]) if len(x) == 2 else aVs.index(x[0]) for x in pairs]
      binaryBits = (6, 11)
      encodedData = ''.join('{:0{size}b}'.format(x, size = binaryBits[len(str(y))-1]) for x, y in zip(groups, pairs))
    else:
      groups = [ord(x) for x in self.text]
      encodedData = ''.join('{:08b}'.format(x) for x in groups)
    self.__bitString += encodedData

    # Step 2.6: Break Up into 8-bit Codewords and Add Pad Bytes if Necessary ✔️
    bitsRequired = eCCWBI[self.errorCorretionLevel][self.version - 1][0]*8
    for i in range(4):
      self.__bitString += '0' if len(self.__bitString) < bitsRequired else ''
    while len(self.__bitString)%8 != 0:
      self.__bitString += '0'
    padBytes = int((bitsRequired - len(self.__bitString))/8)
    for i in range(padBytes):
      self.__bitString += '11101100' if i%2 == 0 else '00010001'

  """ Step 3: Error Correction Coding ✔️ """
  def __greaterThanOrEqualTo256(self, array):
    return [x%255 if x >= 256 else x for x in array]

  def __alphaNotation2IntegerNotation(self, alphaNotation):
    return [self.__logAntilog[x] for x in alphaNotation]

  def __integerNotation2AlphaNotation(self, integerNotation):
    return [self.__logAntilog.index(x) for x in integerNotation]

  def __errorCorrectionCoding(self):
    # Step 3.1: Break Data Codewords into Blocks if Necessary ✔️
    ## I did the step above in step 4.1
    # Step 3.2: Understand Polynomial Long Division ✔️
    # Step 3.3: Understand The Galois Field ✔️
    # Step 3.4: Understand Galois Field Arithmetic ✔️

    # Step 3.5: Generate Powers of 2 Using Byte-Wise Modulo 100011101 ✔️
    self.__logAntilog = [1]
    while len(self.__logAntilog) != 256:
      i = self.__logAntilog[-1]*2
      self.__logAntilog.append(i if i < 256 else i^285)

    # Step 3.6: Understand Multiplication with Logs and Antilogs ✔️

    # Step 3.7: Understanding The Generator Polynomial ✔️
    g = [1, 0]
    self.__generatorPolynomial = [1, 25, 0]
    for steps in range(eCCWBI[self.errorCorretionLevel][self.version - 1][1] - 2):
      g[0] += 1 
      auxGeneratorPolynomial = []
      for i in range(len(self.__generatorPolynomial)):
        auxGeneratorPolynomial.extend([self.__generatorPolynomial[i] + g[0], self.__generatorPolynomial[i] + g[1]])
      auxGeneratorPolynomial = self.__greaterThanOrEqualTo256(auxGeneratorPolynomial)
      auxGeneratorPolynomial = self.__alphaNotation2IntegerNotation(auxGeneratorPolynomial)
      self.__generatorPolynomial = [auxGeneratorPolynomial[0]]
      for i in range(1, len(auxGeneratorPolynomial) - 1, 2):
        self.__generatorPolynomial.append(auxGeneratorPolynomial[i]^auxGeneratorPolynomial[i+1])
      self.__generatorPolynomial.append(auxGeneratorPolynomial[-1])
      self.__generatorPolynomial = self.__integerNotation2AlphaNotation(self.__generatorPolynomial)

    self.__messagePolynomial = [int(self.__bitString[i:i+8], 2) for i in range(0, len(self.__bitString), 8)]

  def __generateErrorCorrectionCodewords(self, block):
    # Step 3.8: Generating Error Correction Codewords ✔️
    # Step 3.9: Divide the Message Polynomial by the Generator Polynomial ✔️
    for steps in range(len(block)):
      generatorPolynomialMultiplied = self.__generatorPolynomial.copy()
      leadTerm = self.__integerNotation2AlphaNotation([block[-1]]) if block[-1]!= 0 else [0]
      generatorPolynomialMultiplied = [x + leadTerm[-1] for x in generatorPolynomialMultiplied]
      generatorPolynomialMultiplied = self.__greaterThanOrEqualTo256(generatorPolynomialMultiplied)
      generatorPolynomialMultiplied = self.__alphaNotation2IntegerNotation(generatorPolynomialMultiplied)
      
      a, b = generatorPolynomialMultiplied, block
      if len(self.__generatorPolynomial) > len(block):
        a, b = b, a
      a = [0]*abs(len(self.__generatorPolynomial) - len(block)) + a
      block = [x^y if y!=0 else x for x, y in zip(b, a)]
      block.pop()
    return block[::-1]

  """ Step 4: Structure Final Message ✔️ """
  def __structureFinalMessage(self):
    # Step 4.1: Determine How Many Blocks and Error Correction Codewords are Required ✔️
    auxMessagePolynomial = []
    for i in range(2, 5, 2):
      blockSize = eCCWBI[self.errorCorretionLevel][self.version-1][i+1]
      for j in range(eCCWBI[self.errorCorretionLevel][self.version-1][i]):
        auxMessagePolynomial.append(self.__messagePolynomial[blockSize*j:blockSize*(j+1)])
        self.__errorCorrectionCodewords.append(self.__generateErrorCorrectionCodewords(auxMessagePolynomial[-1][::-1]))
      group2 = eCCWBI[self.errorCorretionLevel][self.version-1][2] * eCCWBI[self.errorCorretionLevel][self.version-1][3]
      self.__messagePolynomial = self.__messagePolynomial[group2:]
    self.__messagePolynomial = auxMessagePolynomial.copy()

    # Step 4.2: Intervale the Blocks ✔️
    self.__finalMessage = list(roundrobin(*self.__messagePolynomial)) + list(roundrobin(*self.__errorCorrectionCodewords))

    # Step 4.3: Convert to Binary ✔️
    self.__finalMessage = ''.join('{:08b}'.format(x) for x in self.__finalMessage)

    # Step 4.4: Add Remainder Bits if Necessary ✔️
    self.__finalMessage += '0'*rRBs[self.version - 1]

  """ Step 5: Module Placement in Matrix ✔️ """
  def __modulePlacement(self):
    self.size = (self.version - 1)*4 + 21
    self.__matrix = np.zeros((self.size, self.size))

    # Step 5.1: Add the Finder Patterns ✔️
    cv2.rectangle(self.__matrix, pt1=(0,0), pt2=(6,6), color=1, thickness=-1)
    cv2.rectangle(self.__matrix, pt1=(1,1), pt2=(5,5), color=254, thickness=1)
    cv2.rectangle(self.__matrix, pt1=(self.size-7,0), pt2=(self.size-1,6), color=1, thickness=-1)
    cv2.rectangle(self.__matrix, pt1=(self.size-6,1), pt2=(self.size-2,5), color=254, thickness=1)
    cv2.rectangle(self.__matrix, pt1=(0,self.size-7), pt2=(6,self.size-1), color=1, thickness=-1)
    cv2.rectangle(self.__matrix, pt1=(1,self.size-6), pt2=(5,self.size-2), color=254, thickness=1)

    # Step 5.2: Add the Separators ✔️
    cv2.rectangle(self.__matrix, pt1=(-1,-1), pt2=(7,7), color=254, thickness=1)
    cv2.rectangle(self.__matrix, pt1=(self.size-8,-1), pt2=(self.size,7), color=254, thickness=1)
    cv2.rectangle(self.__matrix, pt1=(-1,self.size-8), pt2=(7,self.size), color=254, thickness=1)

    # Step 5.3: Add the Alignment Patterns ✔️
    alignmentPatternLocation = aPLs[self.version-1]
    for i in alignmentPatternLocation:
      for j in alignmentPatternLocation:
        if self.__matrix[j-1,i-1] != 254:
          cv2.rectangle(self.__matrix, pt1=(i-2,j-2), pt2=(i+2,j+2), color=1, thickness=-1)
          cv2.rectangle(self.__matrix, pt1=(i-1,j-1), pt2=(i+1,j+1), color=254, thickness=1)
    
    # Step 5.4: Add the Timing Patterns ✔️
    self.__matrix[8:self.size-8:2,6] = 1
    self.__matrix[9:self.size-9:2,6] = 254
    self.__matrix[6,8:self.size-8:2] = 1
    self.__matrix[6,9:self.size-9:2] = 254

    # Step 5.5: Add the Dark Module and Reserved Areas ✔️
    self.__matrix[4*self.version+9,8] = 1

    self.__matrix[8,0:9] = 1
    self.__matrix[8,self.size-8:self.size] = 1
    self.__matrix[0:8,8] = 1
    self.__matrix[self.size-8:self.size,8] = 1

    if self.version >= 7:
      cv2.rectangle(self.__matrix, pt1=(self.size-11,0), pt2=(self.size-9,5), color=1, thickness=-1)
      cv2.rectangle(self.__matrix, pt1=(0,self.size-11), pt2=(5,self.size-9), color=1, thickness=-1)

    # Step 5.6: Place the Data Bits ✔️
    k = 0
    for i in range(self.size-1,0,-4):
      if i == 4:
        i -= 1
      for j in range(self.size-1,-1,-1):
        if self.__matrix[j,i] == 0:
          self.__matrix[j,i] = 0 if self.__finalMessage[k] == '1' else 255
          k += 1
        if self.__matrix[j,i-1] == 0:
          self.__matrix[j,i-1] = 0 if self.__finalMessage[k] == '1' else 255
          k += 1
      if i == 8:
        i -= 1
      for j in range(0,self.size):
        if self.__matrix[j,i-2] == 0:
          self.__matrix[j,i-2] = 0 if self.__finalMessage[k] == '1' else 255
          k += 1
        if self.__matrix[j,i-3] == 0:
          self.__matrix[j,i-3] = 0 if self.__finalMessage[k] == '1' else 255
          k += 1

  """ Step 6: Data Masking ✔️ """
  def __dataMasking(self):
    self.__mask = randint(0,7)
    for i in range(self.size):
      for j in range(self.size):
        formulas = [
          (i+j)%2, i%2, j%3, (i+j)%3, (floor(i/2) + floor(j/3))%2, ((i*j)%2) + ((i*j)%3), (((i*j)%2) + ((i*j)%3))%2,
          (((i+j)%2) + ((i*j)%3))%2
        ]
        if formulas[self.__mask] == 0 and (self.__matrix[i,j] == 255 or self.__matrix[i,j] == 0):
          self.__matrix[i,j] = 255 if self.__matrix[i,j] == 0 else 0

  """ Step 7: Format and Version Information ✔️ """
  def __formatVersionInformation(self):
    formatString = [x^1 for x in list(map(int, list(fISs[self.errorCorretionLevel][self.__mask])))]
    formatString = np.array(formatString)*255
    self.__matrix[np.ix_([8], [0,1,2,3,4,5,7,8])] = formatString[0:8]
    self.__matrix[8, self.size-8:] = formatString[7:]
    self.__matrix[0:6,8] = formatString[-1:-7:-1]
    self.__matrix[7,8] = formatString[-7]
    self.__matrix[self.size-7:,8] = formatString[-9::-1]

    if self.version >= 7:
      versionString = [x^1 for x in list(map(int, list(reversed(vISs[self.version-7]))))]
      versionString = np.array(versionString)*255
      self.__matrix[self.size-11,:6] = versionString[::3]
      self.__matrix[self.size-10,:6] = versionString[1::3]
      self.__matrix[self.size-9,:6] = versionString[2::3]
      self.__matrix[:6,self.size-11] = versionString[::3]
      self.__matrix[:6,self.size-10] = versionString[1::3]
      self.__matrix[:6,self.size-9] = versionString[2::3]

    self.__matrix = np.pad(self.__matrix, 4, constant_values=255)
      
  def create(self):
    self.__dataAnalysis()
    self.__dataEncoding()
    self.__errorCorrectionCoding()
    self.__structureFinalMessage()
    self.__modulePlacement()
    self.__dataMasking()
    self.__formatVersionInformation()

  def show(self):
    if self.__matrix != []:
      cv2.namedWindow('', cv2.WINDOW_NORMAL)
      cv2.startWindowThread()
      cv2.imshow('', np.uint8(self.__matrix))
      cv2.waitKey(0)
      cv2.destroyAllWindows()
    else:
      print('Error: no qr code created.')

  def save(self):
    if self.__matrix != []:
      self.__matrix = cv2.resize(self.__matrix, (720, 720), interpolation = cv2.INTER_AREA)
      filename = filedialog.asksaveasfilename(
        title="choose filename",
        defaultextension='.png',
        initialfile='qrcode.png'
      )
      try:
       cv2.imwrite(filename, self.__matrix)
      except:
        print('Error: no file selected.')
    else:
      print('Error: no qr code created.')