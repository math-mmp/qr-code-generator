from dataTables import alphanumericValues as aVs
from dataTables import errorCorretionLevels as eCLs
from dataTables import characterCapacities as cCs
from dataTables import modeIndicators as mIs
from dataTables import characterCountIndicators as cCIs
from dataTables import errorCorrectionCodeWordsBlockInformation as eCCWBI

class QRCode:
  def __init__(self, text, errorCorretionLevel = 'H'):
    self.text = text
    self.errorCorretionLevel = errorCorretionLevel
    self.encodingMode = None
    self.version = None
    self.__logAntilog = []
    self.__generatorPolynomial = []
    self.__messagePolynomial = []
    self.__errorCorrectionCodewords = []

  def __integerNotation2AlphaNotation(self, integerNotation):
    alphaNotation = [self.__logAntilog.index(i) for i in integerNotation]
    return alphaNotation
  
  def __alphaNotation2IntegerNotation(self, alphaNotation):
    integerNotation = [self.__logAntilog[i] for i in alphaNotation]
    return integerNotation

  def __greaterThanOrEqualTo256(self, array):
    for i in range(len(array)):
      array[i] = array[i]%255 if array[i] >= 256 else array[i]
    return array
  
  def __generateErrorCorrectionCodewords(self, block):
    for steps in range(len(block)):
      generatorPolynomialMultiplied = self.__generatorPolynomial.copy()
      leadTerm = self.__integerNotation2AlphaNotation([block[-1]])
      for i in range(len(self.__generatorPolynomial)):
        generatorPolynomialMultiplied[i] += leadTerm[-1]
      generatorPolynomialMultiplied = self.__greaterThanOrEqualTo256(generatorPolynomialMultiplied)
      generatorPolynomialMultiplied = self.__alphaNotation2IntegerNotation(generatorPolynomialMultiplied)

      if len(block) > len(self.__generatorPolynomial):
        generatorPolynomialMultiplied = [0]*(len(block) - len(self.__generatorPolynomial)) + generatorPolynomialMultiplied
        block = [i^j if j!=0 else i for i, j in zip(block, generatorPolynomialMultiplied)]
      else:
        block =  [0]*(len(self.__generatorPolynomial) - len(block)) + block
        block = [i^j if j!=0 else i for i, j in zip(generatorPolynomialMultiplied, block)]
      block.pop()
    return block[::-1]

  def create(self):
    ## Step 1: Data Analysis 
    if self.text.isnumeric():
      self.encodingMode = 'numeric'
    elif all(character in aVs for character in self.text):
      self.encodingMode = 'alphanumeric'
    else:
      self.encodingMode = 'byte'

    ## Step 2: Data Encoding
    # Step 2.1: Choose the Error Correction Level
    # Step 2.2: Determine the Smallest Version for the Data
    index = eCLs.index(self.errorCorretionLevel)
    for i in range(index, -1, -1): 
      data = cCs[self.encodingMode][i]
      try:
        self.version = [data.index(maxLength) for maxLength in data if len(self.text) <= maxLength][0] + 1
        self.errorCorretionLevel = eCLs[i]
        break
      except:
        continue

    # Step 2.3: Add the Mode Indicator
    modeIndicator = mIs[self.encodingMode]

    # Step 2.4: Add the Character Count Indicator
    if 1 <= self.version <= 9:
      characterCountIndicatorSize = cCIs[self.encodingMode][0]
    elif 10 <= self.version <= 26:
      characterCountIndicatorSize = cCIs[self.encodingMode][1]
    else:
      characterCountIndicatorSize = cCIs[self.encodingMode][2]
    characterCountIndicator = '{:0{size}b}'.format(len(self.text), size = characterCountIndicatorSize)

    # Step 2.5: Encode Using the Selected Mode
    groups = []
    if self.encodingMode == 'numeric':
      for digits in range(0, len(self.text), 3):
        groups.append(int(self.text[digits:digits + 3]))
      binaryBits = (4, 7, 10)
      encodedData = ''.join('{:0{size}b}'.format(i, size = binaryBits[len(str(i))-1]) for i in groups)
    elif self.encodingMode == 'alphanumeric':
      pairs = []
      for digits in range(0, len(self.text), 2):
         pairs.append(self.text[digits:digits + 2])
      groups = [(45* aVs.index(i[0])) + aVs.index(i[1]) if len(i) == 2 else aVs.index(i[0]) for i in pairs]
      binaryBits = (6, 11)
      encodedData = ''.join('{:0{size}b}'.format(i, size = binaryBits[len(str(j))-1]) for i, j in zip(groups, pairs))
    else:
      groups = [ord(i) for i in self.text]
      encodedData = ''.join('{:08b}'.format(i) for i in groups)

    bitString = modeIndicator + characterCountIndicator + encodedData

    # Step 2.6: Break Up into 8-bit Codewords and Add Pad Bytes if Necessary
    bitsRequired = eCCWBI[self.errorCorretionLevel][self.version - 1][0] * 8
    while len(bitString)%8 != 0:
      bitString += '0'
    padBytes = int((bitsRequired - len(bitString))/8)
    for i in range(padBytes):
      bitString += '11101100' if i%2 == 0 else '00010001'

    ## Step 3: Error Correction Coding
    # Step 3.5: Generate Powers of 2 Using Byte-Wise Modulo 100011101
    self.__logAntilog = [1]
    while len(self.__logAntilog) != 256:
      i = self.__logAntilog[-1]*2
      self.__logAntilog.append(i if i < 256 else i^285)
    
    # Step 3.7: Generator Polynomial
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
      for i in range(1, len(auxGeneratorPolynomial)-1, 2):
        self.__generatorPolynomial.append(auxGeneratorPolynomial[i]^auxGeneratorPolynomial[i+1])
      self.__generatorPolynomial.append(auxGeneratorPolynomial[-1])
      self.__generatorPolynomial = self.__integerNotation2AlphaNotation(self.__generatorPolynomial)

    self.__messagePolynomial = [int(bitString[i:i+8], 2) for i in range(0,len(bitString),8)]

    ## Step 4: Structure Final Message
    # Step 4.1: Determine How Many Blocks and Error Correction Codewords are Required
    auxMessagePolynomial = []
    for i in range(2, 5, 2):
      for j in range(0, eCCWBI[self.errorCorretionLevel][self.version - 1][i]):
        blockSize = eCCWBI[self.errorCorretionLevel][self.version - 1][i+1]
        auxMessagePolynomial.append(self.__messagePolynomial[blockSize*j:blockSize*(j+1)])
        self.__errorCorrectionCodewords.append(self.__generateErrorCorrectionCodewords(auxMessagePolynomial[-1][::-1]))
    self.__messagePolynomial = auxMessagePolynomial.copy()

    print(self.__messagePolynomial)
    print(self.__errorCorrectionCodewords)

    ## Step 5: Module Placement in Matrix
    ## Step 6: Data Masking
    ## Step 7: Format and Version Information

  # def show(self):

  # def save(self):

qrCode = QRCode('UMA IMAGEM VALE MAIS DO QUE 1.000 PALAVRAS')
qrCode.create()

print('Tipo de Codificação:', qrCode.encodingMode)
print('Tamanho do Texto:', len(qrCode.text))
print('Nível de Correção:', qrCode.errorCorretionLevel)
print('Versão:', qrCode.version)