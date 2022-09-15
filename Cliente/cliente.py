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
def cria_pacote(payload, pacote_enviado,total_pacotes,eop):
    n_payload = int_to_byte(len(payload))
    n_pacote = int_to_byte(pacote_enviado)
    n_pacotestotal = int_to_byte(total_pacotes)
    return b'\x03\x00\x00' + n_pacotestotal + n_pacote + n_payload+b'\x00\x00\x00\x00' +payload+eop

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
            return True,0
        elif tipo == "Erro":
            file1.write(pega_data() + " /receb/" +"6/" +"14"+"\n")
            return False,header[6]
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
        #Preenche a lista de envios com os pacotes
        for i in range(0,len(info)):
            pacote = cria_pacote(info[i],i+1,len(info),dicionario["EOP"])
            lista_envio.append(pacote)

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
            #if erro ==False and cont ==3:
                #pacote_falso = cria_pacote(info[cont-1],7,len(info),dicionario["EOP"])
                #envia_data(lista_envio[cont-1],com1)
                #erro = True
            #else:
            envia_data(lista_envio[cont-1],com1)
            file1.write(pega_data() + " /envio/" +"3/" +str(len(lista_envio[cont-1]))+"/"+ str(lista_envio[cont-1][4])+ "/"+str(lista_envio[cont-1][3])+"\n")
            print(f"Envia pacote {cont}")
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
                    tipo_4,corrige = checa_mensagem(com1,file1)
                    #Indica que recebeu mensagem e fecha o loop
                    sem_mensagem = False
                    #Checa se tipo 4
                    if tipo_4:
                        print(f"pacote {cont} Ok")
                        cont +=1
                    else:
                        print(f"Tem que corrigir para pacote {corrige}")
                        cont = corrige
                if (tempo_atual-timer_1)>5:
                    #Envia denovo a mensagem
                    envia_data(lista_envio[cont-1],com1)
                    file1.write(pega_data() + " /envio/" +"3/" +str(len(lista_envio[cont-1]))+"/"+ str(lista_envio[cont-1][4])+ "/"+str(lista_envio[cont-1][3])+"\n")
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
