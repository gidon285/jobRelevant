import time
import math

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

class blockChainCrawler:
    """
    this is the crawler assienment, due to lack of time, the algorithm returns an object which should hold all of the information.
    explanation:
        
        the __init__ method starts the class, starts the driver and gets the latest transaction in the transactions tab.
        then we call the search method to loop through the addresses, the idea -> get the current address -> follow it to the end 
        of the logging page (calculation in line 53-58) then go there, and look for the CoinBase green span, if found then return the number
        of count, with the num(iteration number) after that go to the next previous addresses.
        close the driver.

    """
    def __init__(self):
        self._driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        self._previous = []
        self._path= {}
        
        self._driver.get("https://www.blockchain.com/explorer?utm_campaign=dcomnav_explorer")
        time.sleep(3)
        main_div = self._driver.find_element(by=By.XPATH, value="//div[@class='l6gh2f-9 foMdHG']")
        elementList = main_div.find_elements(by=By.CSS_SELECTOR, value= "a")

        href_list = []
        for ele in elementList:
            href_list.append(ele.get_attribute("href"))
        self._driver.get(href_list[0])

        latest_div = self._driver.find_element(by=By.XPATH, value="//div[@class='ge5wha-0 gMWvxK']")
        links = latest_div.find_elements(by=By.CSS_SELECTOR, value= "a")
        for element in links:
            link = element.get_attribute("href")
            if link.__contains__("address"):
               self._previous.append(link)
        self._path = {item:0 for item in range(len(self._previous))}

    def search(self, link:str, count=int, num=int):

        self._driver.get(self._previous[num])
        time.sleep(3)
        transactions_span = self._driver.find_element(by=By.XPATH, value="//span[@class='sc-1ryi78w-0 cILyoi sc-16b9dsl-1 ZwupP u3ufsr-0 eQTRKC']")
        transactions_span = transactions_span.text.split(" ")
        transactions_str = str(transactions_span[4])
        
        # get accurate number- turn 3,000 -> 3000
        if transactions_str.__contains__(","):
            transactions_str= transactions_str.replace(",", "")

        total_transactions = int(transactions_str)
        # # 5 past transactions per page
        page_number = math.ceil(total_transactions/5)
        modulo = total_transactions % 5
        # lets go to the last page and see the first transaction.
        final_page = self._previous[num]+"?page={page}".format(page = page_number)
        self._driver.get(final_page)
        time.sleep(2)
        current_address_past_trans = self._driver.find_element(by=By.XPATH, value="//div[@class='ild1xh-0 iZEoxD']/div[{index}]".format(index= modulo+1))
        links = current_address_past_trans.find_elements(by=By.CSS_SELECTOR, value="a")
        
        # empty links means maybe we are at the last "edge", so we look for the Coinbase span.
        if len(links) == 0:
            try:
                coinbase = self._driver.find_element(by=By.XPATH, value="//span[@class='sc-1ryi78w-0 jEaPao sc-16b9dsl-1 ZwupP sc-45ldg2-0 iA-DtFk']")
            except:
                print("coin base not found")
            self._path[num] = count
            return 
        else:
            # else consider first link as the next (previous) address.
            for element in links:
                link = element.get_attribute("href")
                if link.__contains__("address"):
                    count += 1
                    self.search(str(link), count, num)

    def close_crawler(self):
        self._driver.close()

    def get_prevs(self):
        return self._previous

if __name__ == "__main__":
    crawly = blockChainCrawler()
    num = 0
    for prev in crawly.get_prevs():
        crawly.search(prev, 0, num)
    crawly.close_crawler()



