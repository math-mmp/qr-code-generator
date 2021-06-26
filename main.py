from QRCode import QRCode

qrCode = QRCode('')
qrCode.create()
qrCode.show()

print('Tipo de Codificação:', qrCode.encodingMode)
print('Tamanho do Texto:', len(qrCode.text))
print('Nível de Correção:', qrCode.errorCorretionLevel)
print('Versão:', qrCode.version)