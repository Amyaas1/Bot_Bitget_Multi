class MessageTelegram():
    #message=" "
    def addMessageComponent(message, string):
        #global message
        message=message+"\n"+string
        return message

    #positionList=" "
    def addPosition(positionList, string):
        #global positionList
        positionList=positionList+", "+string
        return positionList