from selenium import webdriver
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options


class InstaBot:
    def __init__(self, filename, storagefile, config):
        self.__options = Options()
        self.__options.add_argument("--headless")
        self.driver = webdriver.Chrome(
            options=self.__options)
        # e nevoie de pret minim si pret maxim pentru a sorta dupa
        self.driver.get("https://www.olx.ro/"
                        + config["category"]
                        + "/?search%5Bfilter_float_price%3Afrom%5D=2&search%5Bfilter_float_price%3Ato%5D=1&currency="
                        + config["currency"])
        self.__filename = filename
        self.__searchedItem = config["searchedItem"]
        self.__priceFrom = config["priceFrom"]
        self.__priceTo = config["priceTo"]
        self.__storagefile = storagefile

    def laptopQuery(self):
        sleep(1)
        self.driver.find_element_by_xpath("//input[@id='search-text']") \
            .send_keys(self.__searchedItem)
        sleep(1)

        minimValueInput = WebDriverWait(self.driver, 20) \
            .until(EC.presence_of_element_located \
                       ((By.XPATH, '//input[@name="search[filter_float_price:from]"]')))

        self.driver.execute_script("arguments[0].value = " + self.__priceFrom + ";", minimValueInput)

        maximValueInput = WebDriverWait(self.driver, 20) \
            .until(EC.presence_of_element_located \
                       ((By.XPATH, '//input[@name="search[filter_float_price:to]"]')))

        self.driver.execute_script("arguments[0].value = " + self.__priceTo + ";", maximValueInput)

        self.driver.find_element_by_xpath("//input[@id='search-submit']") \
            .click()

    def __createListWithResultedTr(self, n):
        list = []
        missing = 0
        i = 0
        while i < n + missing and i < 45:
            try:
                list.append(self.__returnPriceElement(i))
                list[-1] = i
            except:
                missing += 1
            i += 1

        return list

    def __returnPriceElement(self, i):
        return self.driver.find_element_by_xpath(
            '// *[ @ id = "offers_table"] / tbody / tr['
            + str(i)
            + '] / td / div / table / tbody / tr[1] / td[3] / div / p / strong')

    def __returnLocationElement(self, i):
        return self.driver.find_element_by_xpath(
            '//*[@id="offers_table"]/tbody/tr['
            + str(i)
            + ']/td/div/table/tbody/tr[2]/td[1]/div/p/small[1]/span')

    def __returnDateElement(self, i):
        return self.driver.find_element_by_xpath(
            '//*[@id="offers_table"]/tbody/tr['
            + str(i)
            + ']/td/div/table/tbody/tr[2]/td[1]/div/p/small[2]/span')

    def __returnPriceElementList(self, n):
        '''
        there are missing random columns in results for randomness
        but always starts with 4
        '''
        list = self.__createListWithResultedTr(n)
        elementList = []
        for i in range(0, len(list)):
            elementList.append(self.__returnPriceElement(list[i]))

        return elementList

    def __returnHrefElementList(self):
        elems_href = self.driver.find_elements_by_xpath("//a[contains(@href,'oferta')]")
        for i in range(0, len(elems_href)):
            elems_href[i] = elems_href[i].get_attribute("href").split('#')[0]
        return list(dict.fromkeys(elems_href))

    def __returnHrefElement(self, i):
        return self.driver.find_element_by_xpath(
            '//*[@id="offers_table"]/tbody/tr['
            + str(i)
            + ']/td/div/table/tbody/tr[1]/td[2]/div/h3/a')

    def __priceFormatToInt(self, priceFormat):
        priceCuts = priceFormat.text.split(" ")
        sum = 0
        for i in range(0, len(priceCuts) - 1):
            sum = sum * 1000 + int(priceCuts[i])
        return sum

    def __verifyTheExistenceOfItems(self, n):
        '''
        verify if objects with bigger/smaller values than ones sets appear
        gets error cause it will see more values than needed
        because of the random ones generated by the page
        and will try to access an inexisting ones
        '''
        pricesList = self.__returnPriceElementList(n)
        for i in range(0, len(pricesList)):
            sum = self.__priceFormatToInt(pricesList[i])
            if sum > int(self.__priceTo) or sum < int(self.__priceFrom):
                return False
        return True

    def __writeTheItemsInFile(self, elemsHref, trUsed):
        file = open(self.__filename, 'w')
        numberOfItems = min(40, len(elemsHref))
        file.write("<html><head><title>OlxOffers</title></head><body><table border='yes'>")
        storagefile = open(self.__storagefile, 'w')
        for i in range(0, min(3, numberOfItems)):
            storagefile.write(self.__returnHrefElement(trUsed[i]).get_attribute("href").split('#')[0])
            storagefile.write('\n')
        storagefile.close()
        for i in range(0, min(39, numberOfItems)):
            file.write("<tr>\n\n<td>")
            file.write(self.__returnPriceElement(trUsed[i]).text)
            file.write("</td>\n<td>")
            file.write(self.__returnLocationElement(trUsed[i]).text)
            file.write("</td>\n<td>")
            file.write(self.__returnDateElement(trUsed[i]).text)
            file.write("</td>\n<td><a href=" + self.__returnHrefElement(trUsed[i]).get_attribute("href") .split('#')[0] + ">\n")
            file.write(self.__returnHrefElement(trUsed[i]).get_attribute("href") .split('#')[0])
            file.write("\n</a></td></tr>")
        file.write("\n</table></body></html>")
        file.close()

    '''deprecated
    def __writeTheLastThreeOrLessItemsInFile(self,elemsHref):
        f = open(self.__storagefile,'w')
        for i in range(0,min(3,len(elemsHref))):
            f.write(elemsHref[i])
            f.write('\n')
        f.close()
    '''

    def __readTheLastThreeAndReturnList(self):
        f = open(self.__storagefile, 'r')
        lines = f.readlines()
        f.close()
        return lines

    def __returnTrueIfNewItemsAppear(self, elemsHref, trUsed, numberOfItems):
        lines = self.__readTheLastThreeAndReturnList()
        #daca sunt la fel de multe se verifica conditia de aparitie
        n = min(numberOfItems, len(elemsHref), len(lines))
        newItems = []
        oldItems = []
        for i in range(0, n):
            newItems.append(self.__returnHrefElement(trUsed[i]).get_attribute("href").split('#')[0])
            oldItems.append(lines[i])

        #ok - True if new items appears, False otherwise
        ok = True
        for i in range(0, n):
            if newItems[0].strip() == oldItems[i].strip():
                ok = False

        return ok

    def __writeNoItemsInFile(self):
        file = open(self.__filename, 'w')
        file.write("<html><head><title>OlxOffers</title></head><body><table border='yes'>")
        file.write("<tr><td>")
        file.write("Nu sunt elemente!")  # no elements found
        file.write("</td></tr>")
        file.write("</table></body></html>")
        file.close()

    def createWebpage(self):
        sleep(3)
        elemsHref = self.__returnHrefElementList()
        numberOfItems = min(len(elemsHref), 40) #maximum number of elements on a page
        trUsed = self.__createListWithResultedTr(numberOfItems)
        try:
            self.__verifyTheExistenceOfItems(numberOfItems )
            if self.__returnTrueIfNewItemsAppear(elemsHref, trUsed, 3) and numberOfItems >0:

                print("e diferita lista")
                self.__writeTheItemsInFile(elemsHref, trUsed)
            else:
                print("e identica lista")
        except NoSuchElementException:
            self.__writeNoItemsInFile()

    def quit(self):
        self.driver.close()


def getValueThatContainsXFromList(list, dict, x):
    for line in list:
        if x in line:
            dict[x] = line.strip().split('=')[1].strip()

def dataFromConfig():
    f = open("config.txt", "r")
    lines = f.readlines()
    dictionary = {}
    dictionary["category"] = "none"
    dictionary["searchedItem"] = "none"
    dictionary["priceFrom"] = "none"
    dictionary["priceTo"] = "none"

    getValueThatContainsXFromList(lines, dictionary, "category")
    getValueThatContainsXFromList(lines, dictionary, "searchedItem")
    getValueThatContainsXFromList(lines, dictionary, "priceFrom")
    getValueThatContainsXFromList(lines, dictionary, "priceTo")
    getValueThatContainsXFromList(lines, dictionary, "currency")
    f.close()

    return dictionary


storagefile = "storage.txt"
fileName = "olxSearched.html"
config = dataFromConfig()
olxBot = InstaBot(fileName, storagefile, config)
olxBot.laptopQuery()
olxBot.createWebpage()
olxBot.quit()
