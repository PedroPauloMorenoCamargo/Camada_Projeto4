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



# voce deverá descomentar e configurar a porta com através da qual ira fazer comunicaçao
#   para saber a sua porta, execute no terminal :
#   python -m serial.tools.list_ports
# se estiver usando windows, o gerenciador de dispositivos informa a porta

#use uma das 3 opcoes para atribuir à variável a porta usada
#serialName = "/dev/ttyACM0"           # Ubuntu (variacao de)
#serialName = "/dev/tty.usbmodem1411" # Mac    (variacao de)
serialName = "COM3"                  # Windows(variacao de)


dicionario = {
    "EOP":b'\xAA\xBB\xCC\xDD'
}

def int_to_byte(int):
    byte = int.to_bytes(1, 'big')
    return byte

def cria_timeout(eop):
    return b'\x05\x00\x00\x00\x00\x00\x00\x00\x00\x00'+eop

def cria_handshake_server(eop):
    handshake = b'\x02\x00\x00' + b'\x00\x00' + int_to_byte(4) +b'\x00\x00\x00\x00' + eop
    return handshake
def cria_tipo4(ultimo_pacote, eop):
    tipo_4 = b'\x04\x00\x00\x00\x00\x00\x00' + int_to_byte(ultimo_pacote)+b'\x00\x00'+ eop
    return tipo_4
def cria_tipo6(atual,eop):
    tipo_4 = b'\x06\x00\x00\x00\x00\x00' + int_to_byte(atual)+b'\x00\x00\x00'+ eop
    return tipo_4
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
def analisa_handshake(com1):
    header, nrx = com1.getData(10)
    eop, eop_nrx = com1.getData(4)
    tem_eop = checa_eop(eop)
    tipo = tipo_header(header)
    if tipo == "Handshake Cliente" and tem_eop and header[5] == 7:
        return True, header[3]
    else:
        return False, 0

def envia_data(pacote,com1):
    com1.sendData(np.asarray(pacote))
    x = com1.tx.getStatus()
    while x == 0:
        x = com1.tx.getStatus()
    return

def checa_pacote(com1,header,payload,eop,atual,file1):
    tem_eop = checa_eop(eop)
    n_pacote = header[4]
    tipo = tipo_header(header)
    len_total = len(payload)+len(header)+len(eop)
    if tipo =="Data Transmission" and n_pacote == atual and tem_eop:
        file1.write(pega_data() + " /receb/" +"3/" +str(len_total)+"/"+ str(n_pacote)+ "/"+str(header[3])+"\n")
        return True
    else:
        return False

def pega_data():
    # datetime object containing current date and time
    now = str(datetime.now())
    return now

arquivo = 'Server/arq/situacao1.txt'  
def main():
    try:
        open(arquivo, 'w').close()
        file1 = open(arquivo, "a")
        print("Iniciou o main")
        #declaramos um objeto do tipo enlace com o nome "com". Essa é a camada inferior à aplicação. Observe que um parametro
        #para declarar esse objeto é o nome da porta.
        com1 = enlace(serialName)
        com1.enable()
        print("esperando 1 byte de sacrifício")
        rxBuffer, nRx = com1.getData(1)
        com1.rx.clearBuffer()
        time.sleep(.1)
        print("Abriu a comunicação")
        #Se chegamos até aqui, a comunicação foi aberta com sucesso. Faça um print para informar.
        imageW = "Server/img/img.png"
        img = b''
        ocioso = True

        while ocioso:
            vazio = com1.rx.getIsEmpty()
            if vazio == False:
                pra_mim, numero_pacotes = analisa_handshake(com1)
                if pra_mim:
                    file1.write(pega_data() + " /receb/" +"1/" +"14"+"\n")
                    ocioso = False
            time.sleep(1)

        envia_data(cria_handshake_server(dicionario["EOP"]),com1)
        file1.write(pega_data() + " /envio/" +"2/" +"14"+"\n")

        cont = 1

        while cont<= numero_pacotes:
            timer_1 = time.time()
            timer_2 = time.time()
            sem_msg3 = True
            while sem_msg3:
                tempo_atual = time.time()
                vazio = com1.rx.getIsEmpty()
                if vazio == False:
                    header, nrx = com1.getData(10)
                    payload,nrx_payload = com1.getData(header[5])
                    eop,nrx_eop = com1.getData(4)
                    sem_msg3 = False
                if (tempo_atual-timer_2) > 20:
                    #Timeout
                    envia_data(cria_timeout(dicionario["EOP"]),com1)
                    file1.write(pega_data() + " /envio/" +"5/" +"14"+"\n")
                    print("Timeout!")
                    exit()
                if (tempo_atual-timer_1)>2:
                    envia_data(cria_tipo4(cont-1,dicionario["EOP"]),com1)
                    file1.write(pega_data() + " /envio/" +"4/" +"14"+"\n")
                    timer_1 = time.time()
                time.sleep(1)
            pacote_ok = checa_pacote(com1,header,payload,eop,cont,file1)
            if pacote_ok:
                img += payload
                print(f"Recebeu pacote {cont}")
                envia_data(cria_tipo4(cont-1,dicionario["EOP"]),com1)
                file1.write(pega_data() + " /envio/" +"4/" +"14"+"\n")
                cont +=1
            else:
                print(f"Pediu pacote {cont}")
                envia_data(cria_tipo6(cont,dicionario["EOP"]),com1)
                file1.write(pega_data() + " /envio/" +"6/" +"14"+"\n")
                   
            f = open(imageW,'wb')
            f.write(img)
            


        
                




        # Encerra comunicação
        print("-------------------------")
        print("Comunicação encerrada")
        print("-------------------------")
    except Exception as erro:
        print("ops! :-\\")
        print(erro)
        

    #so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    main()
