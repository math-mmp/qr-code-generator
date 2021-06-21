from dataTables import alphanumericValues as aVs
from dataTables import errorCorretionLevels as eCLs
from dataTables import characterCapacities as cCs
from dataTables import modeIndicators as mIs
from dataTables import characterCountIndicators as cCIs
from dataTables import errorCorrectionCodeWordsBlockInformation as eCCWBI
from dataTables import requiredRemainderBits as rRBs

from more_itertools import roundrobin

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
    if 1 <= self.version <= 9:
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
        groups.append(int(self.text[digits:digits + 3]))
      binaryBits = (4, 7, 10)
      encodedData = ''.join('{:0{size}b}'.format(x, size = binaryBits[len(str(x))-1]) for x in groups)
    elif self.encodingMode == 'alphanumeric':
      pairs = []
      for digits in range(0, len(self.text), 2):
         pairs.append(self.text[digits:digits + 2])
      groups = [(45* aVs.index(x[0])) + aVs.index(x[1]) if len(x) == 2 else aVs.index(x[0]) for x in pairs]
      binaryBits = (6, 11)
      encodedData = ''.join('{:0{size}b}'.format(x, size = binaryBits[len(str(y))-1]) for x, y in zip(groups, pairs))
    else:
      groups = [ord(x) for x in self.text]
      encodedData = ''.join('{:08b}'.format(x) for x in groups)
    self.__bitString += encodedData

    # Step 2.6: Break Up into 8-bit Codewords and Add Pad Bytes if Necessary ✔️
    bitsRequired = eCCWBI[self.errorCorretionLevel][self.version - 1][0]*8
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
      leadTerm = self.__integerNotation2AlphaNotation([block[-1]])
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
      for j in range(eCCWBI[self.errorCorretionLevel][self.version - 1][i]):
        blockSize = eCCWBI[self.errorCorretionLevel][self.version - 1][i+1]
        auxMessagePolynomial.append(self.__messagePolynomial[blockSize*j:blockSize*(j+1)])
        self.__errorCorrectionCodewords.append(self.__generateErrorCorrectionCodewords(auxMessagePolynomial[-1][::-1]))
    self.__messagePolynomial = auxMessagePolynomial.copy()

    # Step 4.2: Intervale the Blocks
    self.__finalMessage = list(roundrobin(*self.__messagePolynomial)) + list(roundrobin(*self.__errorCorrectionCodewords))

    # Step 4.3: Convert to Binary
    self.__finalMessage = ''.join('{:08b}'.format(x) for x in self.__finalMessage)

    # Step 4.4: Add Remainder Bits if Necessary
    self.__finalMessage += '0'*rRBs[self.version - 1]

  """ Step 5: Module Placement in Matrix """
  """ Step 6: Data Masking """
  """ Step 7: Format and Version Information """

  def create(self):
    self.__dataAnalysis()
    self.__dataEncoding()
    self.__errorCorrectionCoding()
    self.__structureFinalMessage()

  # def show(self):
  # def save(self):
