import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime

headers = { "User-Agent": 'Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0'}
LOG_PATH="/tmp/AmazonPriceChecker/log"
DATA_PATH=os.path.expanduser("~/Documenti/AmazonPriceChecker/data")
USER_DATA_PATH=os.path.expanduser("~/Documenti/AmazonPriceChecker/udata")

class Product:
    def __init__(self, url, name, price, targetPrice, value):
        self.name=name
        self.price=price
        self.targetPrice=targetPrice
        self.value=value
        self.url=url
    

def newProduct(products):
    url = input("Insert Amazon URL of the product you want to check:")
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.content , 'html.parser')
    title = soup.find(id="productTitle").get_text()
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
        value = price[(len(str(price))-1):len(str(price))]
        price = price.replace(",",".")
    else:
        value = dealPrice[(len(str(dealPrice))-1):len(str(dealPrice))]
        price=dealPrice.replace(",",".")
    price = float(price[0:(len(str(price))-1)])
    print("Nome prodotto: " + title.strip())
    print("Prezzo attuale: " + str(price)+" "+ value)
    targetPrice = float(input("Inserire il prezzo desiderato: "))
    prod=Product(url,title.strip(),price,targetPrice,value)
    products.append(prod)
    f=open(DATA_PATH,'a')
    f.write(prod.name+"\n")
    f.write(str(prod.price)+"\n")
    f.write(str(prod.targetPrice)+"\n")
    f.write(str(prod.value)+"\n")
    f.write(prod.url+"\n")
    f.close()
    os.system("systemctl --user restart AmazonPriceChecker.service")
    l=open(LOG_PATH,'a')
    l.write(str(datetime.now())+" Inserted new product: "+str(prod.name)+"\n")
    l.close()

def listProduct(products):
    i=0
    for p in products:
        print("-------------------------------------------")
        print(str(i)+". "+p.name)
        print("Actual price: "+str(p.price)[0:(len(str(p.price))-1)]+ " "+ str(p.value))
        print("Target price: "+str(p.targetPrice)[0:(len(str(p.targetPrice))-1)]+ " "+ str(p.value))
        print("-------------------------------------------")
        i+=1

def deleteProduct(products):
    n=int(input("Insert product number: "))
    p=products[n]
    f=open(DATA_PATH,'r')
    data=str(f.read())
    f.close()
    newdata=data.replace(str(p.name)+str(p.price)+str(p.targetPrice)+str(p.value)+str(p.url),"")
    f=open(DATA_PATH,'w')
    f.write(newdata)
    f.close()
    products.pop(n)
    os.system("systemctl --user restart AmazonPriceChecker.service")
    l=open(LOG_PATH,'a')
    l.write(str(datetime.now())+" Deleted a product: "+str(p.name)+"\n")
    l.close()

def changeRefTime():
    d=open(USER_DATA_PATH,'r')
    REFRESH_TIME=d.readline()
    data = str(d.read())    
    d.close()
    print("Actual refresh time: "+str(REFRESH_TIME))
    REFRESH_TIME=int(input("Insert desired refresh time (in sec.): "))
    d=open(USER_DATA_PATH,'w')
    data=str(REFRESH_TIME)+"\n"+data
    d.write(data)   
    d.close()
    os.system("systemctl --user restart AmazonPriceChecker.service")
    l=open(LOG_PATH,'a')
    l.write(str(datetime.now())+" Changed refresh time, new value: "+str(REFRESH_TIME)+"\n")
    l.close()

def disableAutoStart():
    disable="systemctl --user disable AmazonPriceChecker.service"
    os.system(disable)

def enableAutoStart():
    enable="systemctl --user enable AmazonPriceChecker.service"
    os.system(enable)

def stopDaemon():
    stop="systemctl --user stop AmazonPriceChecker.service"
    os.system(stop)

def menu():
    choose=-1
    while(choose!=0):
        print("******Amazon PriceChecker******")
        print("Menu:")
        print("1. Check a new product")
        print("2. List product you're checking")
        print("3. Delete a product from check list")
        print("4. Change refresh time")
        print("5. Disable auto start")
        print("6. Enable auto start")
        print("7. Stop daemon")
        print("0. Exit")
        choose = int(input("Choose: "))
        if(choose== 1):
            newProduct(products)
        elif(choose== 2):
            listProduct(products)
        elif(choose== 3):
            deleteProduct(products)
        elif(choose == 4):
            changeRefTime()
        elif(choose == 5):
            disableAutoStart()
        elif(choose == 6):
            enableAutoStart()
        elif(choose == 7):
            stopDaemon()
        elif(choose == 0):
            print("Exit.")
            l=open(LOG_PATH,'a')
            l.write(str(datetime.now())+" Exit from application \n")
            l.close()
        else:
            print(str(choose) +" command not found")
    


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

if __name__ == "__main__":
    products=list()
    try:
        l=open(LOG_PATH,'w')
        l.write(str(datetime.now())+" Opened application \n")
        l.close()
    except FileNotFoundError:
        try:
            os.mkdir("/tmp/AmazonPriceChecker")
            l=open(LOG_PATH,'w')
            l.write(str(datetime.now())+" Created log file.\n")
        except FileExistsError:
            print("ERROR")
            pass
    pass
    l.close()

    if(os.path.exists(DATA_PATH)==False):
        try:
            os.mkdir(os.path.expanduser("~/Documenti/AmazonPriceChecker"))
            f=open(DATA_PATH,'w')
            l=open(LOG_PATH,'a')
            l.write(str(datetime.now())+" Created data folder and data file.\n")
            f.close()
            l.close()
        except FileExistsError:
            print("ERROR")
            pass

    try:
        u=open(USER_DATA_PATH,'r')
        udata=str(u.read())
        u.close()
    except FileNotFoundError:
        u=open(USER_DATA_PATH,'w')
        u.write(str(600)+"\n")
        u.write(input("Please insert your name: ")+"\n")
        u.write(input("Please insert your email: ")+"\n")
        u.close()

    if(os.path.exists(os.path.expanduser("~/.config/systemd/user/AmazonPriceChecker.service"))==False):
        s=open(os.path.expanduser("~/.config/systemd/user/AmazonPriceChecker.service"), 'w')
        s.write(
"""[Unit]
#Human readable name of the unit
Description=Amazon Price Checker Service
       
[Service]
# Command to execute when the service is started
Type=simple
ExecStart=/usr/bin/python """+str(os.getcwd())+"""/AmazonPriceChecker_service.py

[Install]
WantedBy=default.target""")
        s.close()
        daemonReload="systemctl --user daemon-reload"
        enable="systemctl --user enable AmazonPriceChecker.service"
        startService="systemctl --user start AmazonPriceChecker.service"
        os.system(daemonReload)
        os.system(enable)
        os.system(startService)

    checkData(products)
    menu()

