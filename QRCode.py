from dataTables import *

class QRCode:
  modeIndicator = None
  characterCountIndicatorSize = None
  characterCountIndicator = None
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
    elif all(character in alphanumericValues for character in self.text):
      self.encodingMode = 'alphanumeric'
    else:
      self.encodingMode = 'byte'

    ## Step 2: Data Encoding
    # Step 2.1: Choose the Error Correction Level
    # Step 2.2: Determine the Smallest Version for the Data
    index = errorCorretionLevels.index(self.errorCorretionLevel)
    for i in range(index, -1, -1): 
      data = characterCapacities[self.encodingMode][i]
      try:
        self.version = [data.index(maxLength) for maxLength in data if self.textLength <= maxLength][0] + 1
        self.errorCorretionLevel = errorCorretionLevels[i]
        break
      except:
        continue

    # Step 2.3: Add the Mode Indicator
    modeIndicator = modeIndicators[self.encodingMode]

    # Step 2.4: Add the Character Count Indicator
    if 1 <= self.version <= 9:
      characterCountIndicatorSize = characterCountIndicators[self.encodingMode][0]
    elif 10 <= self.version <= 26:
      characterCountIndicatorSize = characterCountIndicators[self.encodingMode][1]
    else:
      characterCountIndicatorSize = characterCountIndicators[self.encodingMode][2]
    characterCountIndicator = '{:0{size}b}'.format(self.textLength, size = characterCountIndicatorSize)

    # Step 2.5: Encode Using the Selected Mode
    bitString = modeIndicator + characterCountIndicator
    # Step 2.6: Break Up into 8-bit Codewords and Add Pad Bytes if Necessary

    # Step 3: Error Correction Coding
    # Step 4: Structure Final Message
    # Step 5: Module Placement in Matrix
    # Step 6: Data Masking
    # Step 7: Format and Version Information

  # def show(self):

  # def save(self):

qrCode = QRCode('Escreva seu texto aqui')
qrCode.create()

# Logs
print('Tipo de Codificação:', qrCode.encodingMode)
print('Tamanho do Texto:', qrCode.textLength)
print('Nível de Correção:', qrCode.errorCorretionLevel)
print('Versão:', qrCode.version)