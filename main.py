from selenium import webdriver
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class InstaBot:
    def __init__(self,site,filename):
        self.driver = webdriver.Chrome()
        # e nevoie de pret minim si pret maxim pentru a sorta dupa
        self.driver.get("https://www.olx.ro/electronice-si-electrocasnice/?search%5Bfilter_float_price%3Afrom%5D=2&search%5Bfilter_float_price%3Ato%5D=1")
        self.__filename = filename

    def query(self):
        self.driver.find_element_by_xpath("//input[@name='q']")\
            .send_keys("dell xps 13")
        self.driver.find_element_by_xpath("//input[@id='submit-searchmain']")\
            .click()

    def laptopQuery(self):
        
        self.driver.find_element_by_xpath("//input[@id='search-text']")\
            .send_keys("dell xps 13 i7 512")
        sleep(2)

        minimValueInput = WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.XPATH, '//input[@name="search[filter_float_price:from]"]')))
        self.driver.execute_script("arguments[0].value = '1900';", minimValueInput)

        maximValueInput = WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.XPATH, '//input[@name="search[filter_float_price:to]"]')))
        self.driver.execute_script("arguments[0].value = '5200';", maximValueInput)

        self.driver.find_element_by_xpath("//input[@id='search-submit']")\
            .click()

    def returnPriceElement(self,i):
        '''
        i+4 - asa pleaca in pagina de la row 4
        '''
        return self.driver.find_element_by_xpath('// *[ @ id = "offers_table"] / tbody / tr['+str(i)+'] / td / div / table / tbody / tr[1] / td[3] / div / p / strong')

    def returnHrefElement(self,i):
        return self.driver.find_element_by_xpath('//*[@id="offers_table"]/tbody/tr['+str(i)+']/td/div/table/tbody/tr[1]/td[2]/div/h3/a')

    def returnLocationElement(self,i):
        return self.driver.find_element_by_xpath('//*[@id="offers_table"]/tbody/tr['+str(i)+']/td/div/table/tbody/tr[2]/td[1]/div/p/small[1]/span')

    def returnDateElement(self,i):
        return self.driver.find_element_by_xpath('//*[@id="offers_table"]/tbody/tr['+str(i)+']/td/div/table/tbody/tr[2]/td[1]/div/p/small[2]/span')

    def returnHrefElementList(self):
        elems_href = self.driver.find_elements_by_xpath("//a[contains(@href,'oferta')]")
        for i in range(0, len(elems_href)):
            elems_href[i] = elems_href[i].get_attribute("href").split('#')[0]
        return list(dict.fromkeys(elems_href))

    def createWebpage(self):
        sleep(4)
        elems_href = self.returnHrefElementList()


        file = open(self.__filename,'w')

        file.write("<html><head><title>OlxOffers</title></head><body><table border='yes'>")
        for i in range(4, 4+len(elems_href)):
            file.write("<tr><td>")
            file.write(self.returnPriceElement(i).text)
            file.write("</td><td>")
            file.write(self.returnLocationElement(i).text)
            file.write("</td><td>")
            file.write(self.returnDateElement(i).text)
            file.write("</td><td><a href="+elems_href[i-4]+">")
            file.write(elems_href[i-4])
            file.write("</a></td></tr>")
        file.write("</table></html>")



    def iesi(self):
        self.driver.close()

olxBot = InstaBot("olx.ro","olxTable.html")
olxBot.laptopQuery()
olxBot.createWebpage()
olxBot.iesi()