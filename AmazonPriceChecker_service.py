import requests
from bs4 import BeautifulSoup
import time 
import gi
gi.require_version('Notify', '0.7')
from gi.repository import Notify
import os
from datetime import datetime
import smtplib

headers = { "User-Agent": 'Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0'}
LOG_PATH="/tmp/AmazonPriceChecker/log"
DATA_PATH=os.path.expanduser("~/Documenti/AmazonPriceChecker/data")
USER_DATA_PATH=os.path.expanduser("~/Documenti/AmazonPriceChecker/udata")
data_dimension=0
CONNECTED=False

class Product:
    def __init__(self, url, name, price, targetPrice, value):
        self.name=name
        self.price=price
        self.targetPrice=targetPrice
        self.value=value
        self.url=url

def checkData(products):
    f=open(DATA_PATH,'r')
    line=f.readline()
    while(line != ""):
        name=line
        price=f.readline()
        targetPrice=f.readline()
        value=f.readline()
        url=f.readline()
        prd=Product(url,name,price,targetPrice,value)
        products.append(prd)
        line=f.readline()
    f.close()
    r=open(USER_DATA_PATH,'r')
    REFRESH_TIME = int(r.readline())
    r.close()
    return REFRESH_TIME
    
    

def checkPrice(products,REFRESH_TIME):
    global CONNECTED
    while True:
        for p in products:
            try:
                page = requests.get(p.url, headers=headers)
                CONNECTED=True
            except requests.ConnectionError:
                CONNECTED==False  
            while(CONNECTED!=True):
                try:
                    page = requests.get(p.url, headers=headers)
                    CONNECTED = True
                except requests.ConnectionError:
                    l=open(LOG_PATH,'a')
                    l.write(str(datetime.now)+" Lost connection")
                    l.close()
                CONNECTED==False    
            soup = BeautifulSoup(page.text, 'html.parser')
            try:
                price = soup.find(id="priceblock_ourprice").get_text()
            except AttributeError:
                try:
                    price=soup.find(id="priceBlockStrikePriceString a-text-strike")
                except AttributeError:
                    price=None
            try:
                dealPrice = soup.find(id="priceblock_dealprice").get_text()
            except AttributeError:
                dealPrice = None
                if(price==None):
                    print("ERROR")
            if (dealPrice==None):
                price = price.replace(",",".")
            else:
                price=dealPrice.replace(",",".")
            price = float(price[0:(len(price)-1)])
            if(price<=float(p.targetPrice)):
                Notify.init("Prezzo raggiunto")
                notif= Notify.Notification.new("Your product has an interesting price!!", ((p.name).strip()[0:20]+" now costs: "+str(price)+str(p.value))+"\n"+str(p.url), "dialog-information")
                notif.show()
                l=open(LOG_PATH,'a')
                l.write(str(datetime.now())+" "+p.name+" has your requested price: "+str(price)+".\n")
                l.close()
                #sendEmail(p, price)
            l=open(LOG_PATH,'a')
            l.write(str(datetime.now())+" Checked price \n")
            l.close()
        time.sleep(REFRESH_TIME)

def sendEmail(product, price):
    u=open(USER_DATA_PATH,'r')
    name=str(u.readline())
    email=str(u.readline())
    u.close()
    message="""From: Amazon Price Checker <"""+email+""">
    To: """+name+"""<"""+email+""">
    Subject: Your product has reaced your desired price!
    """+str(product.name)+""" now costs: """+str(product.price)+" "+str(product.value)+"""
    Link: """+str(product.url)+""".
    Amazon Price Checker."""
    try:
        smtpObj = smtplib.SMTP('stmp.gmail.com',587)
        smtpObj.ehlo()
        smtpObj.starttls()
        smtpObj.ehlo()
        passw=input("Insert email password: ")
        smtpObj.login(email,passw)
        smtpObj.sendmail(email, email, message)         
        print ("Successfully sent email")
        smtpObj.quit()
    except smtplib.SMTPException:
       print ("Error: unable to send email")
       smtpObj.quit()

if __name__ == "__main__":
    products=list()
    try:
        l=open(LOG_PATH,"w")
        l.write(str(datetime.now())+" Service started \n")
        l.close()
    except FileNotFoundError:
        try:
            os.mkdir("/tmp/AmazonPriceChecker")
            l=open(LOG_PATH,'w')
            l.write(str(datetime.now())+" Created log file.\n")
            l.write(str(datetime.now())+" Service started \n")
            l.close()
        except FileExistsError:
            print("ERROR")
            pass
    REFRESH_TIME = checkData(products)
    checkPrice(products, REFRESH_TIME)
    l=open(LOG_PATH,"a")
    l.write(str(datetime.now())+" Service closed \n")
    l.close()
