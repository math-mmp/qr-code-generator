from QRCode import QRCode

qrCode = QRCode('UMA IMAGEM VALE MAIS DO QUE 1.000 PALAVRAS')
qrCode.create()

print('Tipo de Codificação:', qrCode.encodingMode)
print('Tamanho do Texto:', len(qrCode.text))
print('Nível de Correção:', qrCode.errorCorretionLevel)
print('Versão:', qrCode.version)