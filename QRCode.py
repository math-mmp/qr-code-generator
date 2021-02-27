from dataTables import *

class QRCode:
  def __init__(self, text, errorCorretionLevel = 'H'):
    self.text = text
    self.textLength = len(text)
    self.encodingMode = None
    self.errorCorretionLevel = errorCorretionLevel
    self.version = None
  
  def create(self):
    if self.textLength == 0:
      self.errorCorretionLevel = None
      return print('write something')

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
    errorCorretionLevels = ('H', 'Q', 'M', 'L')
    index = errorCorretionLevels.index(self.errorCorretionLevel)
    for i in range(index, 4):
      self.errorCorretionLevel = errorCorretionLevels[i]
      for maxLength in characterCapacities[self.encodingMode][errorCorretionLevels[i]]:
        if self.textLength <= maxLength:
          self.version = characterCapacities[self.encodingMode][self.errorCorretionLevel].index(maxLength) + 1
          break
      if self.version != None:
        break
    if self.version == None:
      self.errorCorretionLevel = None
      return print('character capacity exceeded ')

    # Step 2.3: Add the Mode Indicator
    # Step 2.4: Add the Character Count Indicator
    # Step 2.5: Encode Using the Selected Mode
    # Step 2.6: Break Up into 8-bit Codewords and Add Pad Bytes if Necessary

    # Step 3: Error Correction Coding
    # Step 4: Structure Final Message
    # Step 5: Module Placement in Matrix
    # Step 6: Data Masking
    # Step 7: Format and Version Information

  # def show(self):

  # def save(self):

qrCode = QRCode('text')
qrCode.create()

# Logs
print('Tipo de Codificação:', qrCode.encodingMode)
print('Tamanho do Texto:', qrCode.textLength)
print('Nível de Correção:', qrCode.errorCorretionLevel)
print('Versão:', qrCode.version)