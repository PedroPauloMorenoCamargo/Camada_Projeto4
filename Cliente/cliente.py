#####################################################
# Camada Física da Computação
#Carareto
#11/08/2022
#Aplicação
####################################################


#esta é a camada superior, de aplicação do seu software de comunicação serial UART.
#para acompanhar a execução e identificar erros, construa prints ao longo do código! 


from enlace import *
import time
import numpy as np
import math
from datetime import datetime
from bitstring import BitArray
# Returns XOR of 'a' and 'b'
# (both of same length)
def xor(a, b):
 

    # initialize result

    result = []
 

    # Traverse all bits, if bits are

    # same, then XOR is 0, else 1

    for i in range(1, len(b)):

        if a[i] == b[i]:

            result.append('0')

        else:

            result.append('1')
 

    return ''.join(result)

# Performs Modulo-2 division

def mod2div(dividend, divisor):
 

    # Number of bits to be XORed at a time.

    pick = len(divisor)
 

    # Slicing the dividend to appropriate

    # length for particular step

    tmp = dividend[0 : pick]
 

    while pick < len(dividend):
 

        if tmp[0] == '1':
 

            # replace the dividend by the result

            # of XOR and pull 1 bit down

            tmp = xor(divisor, tmp) + dividend[pick]
 

        else:   # If leftmost bit is '0'

            # If the leftmost bit of the dividend (or the

            # part used in each step) is 0, the step cannot

            # use the regular divisor; we need to use an

            # all-0s divisor.

            tmp = xor('0'*pick, tmp) + dividend[pick]
 

        # increment pick to move further

        pick += 1
 

    # For the last n bits, we have to carry it out

    # normally as increased value of pick will cause

    # Index Out of Bounds.

    if tmp[0] == '1':

        tmp = xor(divisor, tmp)

    else:

        tmp = xor('0'*pick, tmp)
 

    checkword = tmp

    return checkword
 
# Function used at the sender side to encode
# data by appending remainder of modular division
# at the end of data.

def encodeData(data, key):
 

    l_key = len(key)
 

    # Appends n-1 zeroes at end of data

    appended_data = data + '0'*(l_key-1)

    remainder = mod2div(appended_data, key)
 

    # Append remainder in the original data

    codeword = data + remainder

    return remainder

def bitstring_to_bytes(s):
    return int(s, 2).to_bytes((len(s) + 7) // 8, byteorder='big')
# voce deverá descomentar e configurar a porta com através da qual ira fazer comunicaçao
#   para saber a sua porta, execute no terminal :
#   python -m serial.tools.list_ports
# se estiver usando windows, o gerenciador de dispositivos informa a porta

#use uma das 3 opcoes para atribuir à variável a porta usada
#serialName = "/dev/ttyACM0"           # Ubuntu (variacao de)
#serialName = "/dev/tty.usbmodem1411" # Mac    (variacao de)
serialName = "COM4"                  # Windows(variacao de)


dicionario = {
    "EOP":b'\xAA\xBB\xCC\xDD'
}

def int_to_byte(int):
    byte = int.to_bytes(1, 'big')
    return byte

def cria_timeout(eop):
    return b'\x05\x00\x00\x00\x00\x00\x00\x00\x00\x00'+eop
def cria_pacote(payload, pacote_enviado,total_pacotes,eop):
    n_payload = int_to_byte(len(payload))
    n_pacote = int_to_byte(pacote_enviado)
    n_pacotestotal = int_to_byte(total_pacotes)
    data = BitArray(payload)
    key = '{0:016b}'.format(int('0x5935',16))
    resto = encodeData(data.bin, key)
    print(resto)
    resto_em_bytes = bitstring_to_bytes(resto)
    print(resto_em_bytes)
    resto_hexa = resto_em_bytes.hex()
    return b'\x03\x00\x00' + n_pacotestotal + n_pacote + n_payload+b'\x00\x00'+ resto_em_bytes+payload+eop,resto_hexa

def cria_handshake(id,total_pacotes,eop):
    handshake = b'\x01\x00\x00' +int_to_byte(total_pacotes)+ b'\x00' + int_to_byte(id) +b'\x00\x00\x00\x00' + eop
    return handshake

def tipo_header(pacote):
    if pacote[0] == 1:
        return "Handshake Cliente"
    if pacote[0] == 2:
        return "Handshake Server"
    if pacote[0] == 3:
        return "Data Transmission"
    if pacote[0]== 4:
        return "Ok"
    if pacote[0]== 6:
        return "Erro"

def checa_eop(eop):
    if eop == b'\xAA\xBB\xCC\xDD':
        return True
    else:
        return False

def envia_data(pacote,com1):
    com1.sendData(np.asarray(pacote))
    x = com1.tx.getStatus()
    while x == 0:
        x = com1.tx.getStatus()
    return

def checa_id(numero):
    if numero == 4:
        return True
    return False
def checa_handshake(com1):
    #Verifica se esta vazio
    if com1.rx.getIsEmpty():
        return False
    #Pega o header
    header, nrx = com1.getData(10)
    #Pega o eop
    eop, eop_nrx = com1.getData(4)
    #Verifica o tipo
    tipo = tipo_header(header)
    #Ve se é o tipo correto
    if tipo == 'Handshake Server':
        #Checa o ID
        tem_id = checa_id(header[5])
        #Checa pra ver se tem o EOP e ID
        tem_eop = checa_eop(eop)
        if tem_eop and tem_id:
            return True
        else:
            return False
    else:
        return False
def pega_data():
    # datetime object containing current date and time
    now = str(datetime.now())
    return now
def checa_mensagem(com1,file1):
    #Pega header
    header, nrx = com1.getData(10)
    #Pega eop
    eop,eop_nrx = com1.getData(4)
    tem_eop = checa_eop(eop)
    #Checa se tem eop
    if tem_eop:
        #Checa tipo da mensagem
        tipo = tipo_header(header)
        if tipo == "Ok":
            file1.write(pega_data() + " /receb/" +"4/" +"14"+"\n")
            return True,0,header[7]
        elif tipo == "Erro":
            file1.write(pega_data() + " /receb/" +"6/" +"14"+"\n")
            return False,header[6],0
        else:
            print("Comunicação Errada")
            quit()
    else:
        print("Sem EOP")
        quit()
arquivo = 'Cliente/arq/situacao8.txt'  
def main():
    try:
        open(arquivo, 'w').close()
        file1 = open(arquivo, "a")
        print("Iniciou o main")
        #declaramos um objeto do tipo enlace com o nome "com". Essa é a camada inferior à aplicação. Observe que um parametro
        #para declarar esse objeto é o nome da porta.
        com1 = enlace(serialName)
        com1.enable()
        time.sleep(.2)
        com1.sendData(b'00')
        time.sleep(1)
        #Se chegamos até aqui, a comunicação foi aberta com sucesso. Faça um print para informar.
        print("Abriu a comunicação")
        #Se chegamos até aqui, a comunicação foi aberta com sucesso. Faça um print para informar.
        imageR = "Cliente/img/images.png"

        TxBuffer = open(imageR,'rb').read()
        #Itera condicionalmente para que deixe os pacotes o mais eficiente possível (payload = 114 bytes sempre que der)
        info = [TxBuffer[i:i + 114] for i in range(0, len(TxBuffer), 114)]
        #Cria Lista de Envios e adiciona o Handshake
        lista_envio = [cria_handshake(7,len(info),dicionario["EOP"])]
        lista_restos = []
        #Preenche a lista de envios com os pacotes
        for i in range(0,len(info)):
            pacote,resto_hexa = cria_pacote(info[i],i+1,len(info),dicionario["EOP"])
            lista_restos.append(resto_hexa)
            lista_envio.append(pacote)
        print(lista_restos)
        #Variável para ver se o servidor esta ocioso
        inicia = False
        #Loop do handshake
        while inicia == False:
            #Envia o Handshake
            envia_data(lista_envio[0],com1)
            file1.write(pega_data() + " /envio/" +"1/" +"14"+"\n")
            print("enviou handshake")
            time.sleep(5)
            #Váriavel dizendo se a resposta foi sucesso ou nao
            resposta = checa_handshake(com1)
            if resposta:
                file1.write(pega_data() + " /receb/" +"2/" +"14"+"\n")
                print("recebeu handshake")
                inicia = True
                #Tira o Handshake da Lista
                lista_envio.pop(0)       
        #Contador
        cont = 1
        erro = False
        while cont<= len(lista_envio):
            print(lista_restos[cont-1])
            #if erro ==False and cont ==3:
                #pacote_falso = cria_pacote(info[cont-1],7,len(info),dicionario["EOP"])
                #envia_data(lista_envio[cont-1],com1)
                #erro = True
            #else:
            envia_data(lista_envio[cont-1],com1)
            print(f"envia {cont}")
            file1.write(pega_data() + " /envio/" +"3/" +str(len(lista_envio[cont-1]))+"/"+ str(lista_envio[cont-1][4])+ "/"+str(lista_envio[cont-1][3])+"/"+ lista_restos[cont-1]+"\n")
            timer_1 = time.time()
            timer_2 = time.time()
            #
            sem_mensagem = True
            while sem_mensagem:
                tempo_atual = time.time()
                #Checa se rx está vazio
                vazio = com1.rx.getIsEmpty()
                if vazio == False:
                    #Checa se a mensagem é do tipo 4 e se n for o número para corrigir o envio do pacote
                    tipo_4,corrige,atualiza = checa_mensagem(com1,file1)
                    #Indica que recebeu mensagem e fecha o loop
                    sem_mensagem = False
                    #Checa se tipo 4
                    if tipo_4:
                        cont = (atualiza +1)
                        print(cont)
                    else:
                        print(f"corrige{corrige}")
                        cont = corrige
                if (tempo_atual-timer_1)>5:
                    #Envia denovo a mensagem
                    envia_data(lista_envio[cont-1],com1)
                    file1.write(pega_data() + " /envio/" +"3/" +str(len(lista_envio[cont-1]))+"/"+ str(lista_envio[cont-1][4])+ "/"+str(lista_envio[cont-1][3])+"/"+ lista_restos[cont-1]+"\n")
                    #Reseta T1
                    timer_1 = time.time()  
                if (tempo_atual-timer_2)>20:
                    #Timeout
                    envia_data(cria_timeout(dicionario["EOP"]),com1)
                    file1.write(pega_data() + " /envio/" +"5/" +"14"+"\n")
                    print("Timeout!")
                    exit()
                


                


    
        





        # Encerra comunicação
        print("-------------------------")
        print("Comunicação encerrada")
        print("-------------------------")
        com1.disable()    
    except Exception as erro:
        print("ops! :-\\")
        print(erro)
        

    #so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    main()
