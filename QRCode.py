from dataTables import alphanumericValues as aVs
from dataTables import errorCorretionLevels as eCLs
from dataTables import characterCapacities as cCs
from dataTables import modeIndicators as mIs
from dataTables import characterCountIndicators as cCIs
from dataTables import errorCorrectionCodeWordsBlockInformation as eCCWBI

class QRCode:
  modeIndicator = None
  characterCountIndicatorSize = None
  characterCountIndicator = None
  encodedData = None
  bitString = None

  def __init__(self, text, errorCorretionLevel = 'H'):
    self.text = text
    self.textLength = len(text)
    self.encodingMode = None
    self.errorCorretionLevel = errorCorretionLevel
    self.version = None
  
  def create(self):

    # Step 1: Data Analysis 
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
        self.version = [data.index(maxLength) for maxLength in data if self.textLength <= maxLength][0] + 1
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
    characterCountIndicator = '{:0{size}b}'.format(self.textLength, size = characterCountIndicatorSize)

    # Step 2.5: Encode Using the Selected Mode
    groups = []
    if self.encodingMode == 'numeric':
      for digits in range(0, self.textLength, 3):
        groups.append(int(self.text[digits:digits + 3]))
      binaryBits = (4, 7, 10)
      encodedData = ''.join('{:0{size}b}'.format(i, size = binaryBits[len(str(i))-1]) for i in groups)
    elif self.encodingMode == 'alphanumeric':
      pairs = []
      for digits in range(0, self.textLength, 2):
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
      if i%2 == 0:
        bitString += '11101100'
      else:
        bitString += '00010001'

    # Step 3: Error Correction Coding
    # Step 4: Structure Final Message
    # Step 5: Module Placement in Matrix
    # Step 6: Data Masking
    # Step 7: Format and Version Information

  # def show(self):

  # def save(self):

qrCode = QRCode('HELLO WORLD')
qrCode.create()

# Logs
print('Tipo de Codificação:', qrCode.encodingMode)
print('Tamanho do Texto:', qrCode.textLength)
print('Nível de Correção:', qrCode.errorCorretionLevel)
print('Versão:', qrCode.version)