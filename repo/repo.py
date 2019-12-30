class FileRepo():
    def __init__(self,filename,readEntity,writeEntity):
        self.__filename = filename
        self.__readEntity = readEntity
        self.__writeEntity = writeEntity

    def getAllFromFile(self):
        file = open("links.txt", 'r')
