#making func for driver.get
#making appending to match tables dynamic
from tkinter import Tk, simpledialog
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import string
import sqlite3
import re

#Dialog box for stock name:
root = Tk()
root.withdraw()
stock = simpledialog.askstring("Stock Name","Enter the stock name or symbol:")

#navigate to screener.com
driver=webdriver.Chrome()
driver.get("https://www.screener.in/")

#driver.maximize_window()
driver.find_element(By.XPATH,"/html/body/main/div[2]/div/div/div/input").send_keys(stock) # type: ignore
time.sleep(1)
driver.find_element(By.XPATH,"/html/body/main/div[2]/div/div/div/ul/li[1]").click()

#shareholding patterns
PROMOTERS=driver.find_element(By.XPATH,'//*[@id="quarterly-shp"]/div/table/tbody/tr[1]/td[13]').text
FII=driver.find_element(By.XPATH,'//*[@id="quarterly-shp"]/div/table/tbody/tr[2]/td[13]').text
DII=driver.find_element(By.XPATH,'//*[@id="quarterly-shp"]/div/table/tbody/tr[3]/td[13]').text
PUBLIC=driver.find_element(By.XPATH,'//*[@id="quarterly-shp"]/div/table/tbody/tr[5]/td[13]').text
CMP=driver.find_element(By.XPATH,'//*[@id="top-ratios"]/li[2]/span[2]')
F_HIGH=driver.find_element(By.XPATH,'//*[@id="top-ratios"]/li[3]/span[2]/span[1]')
F_LOW=driver.find_element(By.XPATH,'//*[@id="top-ratios"]/li[3]/span[2]/span[2]')

#HL_ratio=(CMP-F_LOW)/(F_HIGH-F_LOW)
PB=driver.find_element(By.XPATH,'//*[@id="top-ratios"]/li[5]/span[2]').text
driver.find_element(By.XPATH,'//*[@id="company-chart-metrics"]/button[2]').click()
time.sleep(1)

#pe5yr
pe_5yr_f=driver.find_element(By.XPATH,'//*[@id="chart-legend"]/label[2]/span').text
pe5l=pe_5yr_f.split()
pe_5yr=pe5l[3]

#pe3yr
driver.find_element(By.XPATH,'//*[@id="company-chart-days"]/button[4]').click()
time.sleep(1)
pe_3yr_f=driver.find_element(By.XPATH,'/html/body/main/section[1]/div[3]/label[2]/span').text
pe3l=pe_3yr_f.split()
pe_3yr=pe3l[3]

#pettmyr
driver.find_element(By.XPATH,'//*[@id="company-chart-days"]/button[3]').click()
time.sleep(1)
pe_1yr_f=driver.find_element(By.XPATH,'//*[@id="chart-legend"]/label[2]/span').text
pe1l=pe_1yr_f.split()
pe_1yr=pe1l[3]

#pe10yr
driver.find_element(By.XPATH,'//*[@id="company-chart-days"]/button[6]').click()
time.sleep(1)
pe_10yr_f=driver.find_element(By.XPATH,'//*[@id="chart-legend"]/label[2]/span').text
pe10l=pe_10yr_f.split()
pe_10yr=pe10l[3]

#DY
DY=driver.find_element(By.XPATH,'//*[@id="top-ratios"]/li[6]/span[2]/span').text

#Quaterly sales
qsales=[]
sales_row = driver.find_elements(By.XPATH, '//*[@id="quarters"]/div[3]/table/tbody/tr[1]/td')
num_cols = len(sales_row)
nc=num_cols
for i in range(1, num_cols + 1):
    qsvalue=driver.find_element(By.XPATH,f'//*[@id="quarters"]/div[3]/table/tbody/tr[1]/td[{i}]').text
    number_string = re.findall(r'[\d,\.]+', qsvalue)
    if number_string:
        clean_string = number_string[0].replace(',', '')  # remove commas
        qsalesnum = float(clean_string)
        qsales.append(qsalesnum)

#Quaterly other income
qoincome=[]
qoi_row = driver.find_elements(By.XPATH, '//*[@id="quarters"]/div[3]/table/tbody/tr[5]/td')
num_cols = len(qoi_row)
for i in range(1, num_cols + 1):
    qoivalue=driver.find_element(By.XPATH,f'//*[@id="quarters"]/div[3]/table/tbody/tr[5]/td[{i}]').text
    number_string = re.findall(r'[\d,\.]+', qoivalue)
    if number_string:
        clean_string = number_string[0].replace(',', '')  # remove commas
        qoinum = float(clean_string)
        qoincome.append(qoinum)

#total revenue quaterly
qtotrev=[]
for i in range(0, num_cols-1):
    val=qoincome[i]+qsales[i]
    qtotrev.append(val)

#revenue growth quaterly
rgq=[]
rgq.append('0')
for i in range(0, num_cols - 2):
    val=(qtotrev[i+1]-qtotrev[i])*100/qtotrev[i]
    rounded = round(val, 2)
    valper=str(rounded)+"%"
    rgq.append(valper)

#consolidated net profit quaterly
npq=[]
npq_row = driver.find_elements(By.XPATH, '//*[@id="quarters"]/div[3]/table/tbody/tr[1]/td')
num_cols = len(npq_row)
for i in range(1, num_cols + 1):
    npqnum=driver.find_element(By.XPATH,f'//*[@id="quarters"]/div[3]/table/tbody/tr[10]/td[{i}]').text
    number_string = re.findall(r'[\d,\.]+', npqnum)
    if number_string:
        clean_string = number_string[0].replace(',', '')  # remove commas
        nppq = float(clean_string)
        npq.append(nppq)

#Net profit margin
npqm=[]
for i in range(0, num_cols - 1):
    val=(npq[i]/qtotrev[i])*100
    rounded = round(val, 2)
    strval=str(rounded)+'%'
    npqm.append(strval)

#EPS quaterly
epsq=[]
epsq_row = driver.find_elements(By.XPATH, '//*[@id="quarters"]/div[3]/table/tbody/tr[11]/td')
num_cols = len(epsq_row)
for i in range(1, num_cols + 1):
    epsqnum=driver.find_element(By.XPATH,f'//*[@id="quarters"]/div[3]/table/tbody/tr[11]/td[{i}]').text
    number_string = re.findall(r'[\d,\.]+', epsqnum)
    if number_string:
        clean_string = number_string[0].replace(',', '')  # remove commas
        epsqn = float(clean_string)
        epsq.append(epsqn)

#EPS growth quaterly
epsgq=[]
epsgq.append('0')
for i in range(0, num_cols - 2):
    val=(epsq[i+1]-epsq[i])*100/epsq[i]
    rounded = round(val, 2)
    valper=str(rounded)+"%"
    epsgq.append(valper)

#promoter quaterly
qpro=[]
qpro_row = driver.find_elements(By.XPATH, '//*[@id="quarterly-shp"]/div/table/tbody/tr[1]/td')
num_cols = len(qpro_row)
if num_cols<nc :
    for i in range(nc-num_cols):
        qpro.append("NA")

for i in range(1, num_cols + 1):
    qpronum=driver.find_element(By.XPATH,f'//*[@id="quarterly-shp"]/div/table/tbody/tr[1]/td[{i}]').text
    number_string = re.findall(r'[\d\.]+', qpronum)
    if not number_string: continue
    qpro.append(qpronum)

#FII% quaterly
qfii=[]
qfii_row = driver.find_elements(By.XPATH, '//*[@id="quarterly-shp"]/div/table/tbody/tr[1]/td')
num_cols = len(qfii_row)
if num_cols<nc :
    for i in range(nc-num_cols):
        qfii.append("NA")

for i in range(1, num_cols + 1):
    qfiinum=driver.find_element(By.XPATH,f'//*[@id="quarterly-shp"]/div/table/tbody/tr[2]/td[{i}]').text
    number_string = re.findall(r'[\d\.]+', qfiinum)
    if not number_string: continue
    qfii.append(qfiinum)

#DII% quaterly
qdii=[]
qdii_row = driver.find_elements(By.XPATH, '//*[@id="quarterly-shp"]/div/table/tbody/tr[1]/td')
num_cols = len(qdii_row)
if num_cols<nc :
    for i in range(nc-num_cols):
        qdii.append("NA")

for i in range(1, num_cols + 1):
    qdiinum=driver.find_element(By.XPATH,f'//*[@id="quarterly-shp"]/div/table/tbody/tr[3]/td[{i}]').text
    number_string = re.findall(r'[\d\.]+', qfiinum)
    if not number_string: continue
    qdii.append(qdiinum)

    
    

#Quaterly info ends here




#Annual sales
sales=[]
salesa_row = driver.find_elements(By.XPATH, '//*[@id="profit-loss"]/div[3]/table/tbody/tr[1]/td')
num_cols = len(salesa_row)
nca=num_cols
for i in range(1, num_cols + 1):
    svalue=driver.find_element(By.XPATH,f'//*[@id="profit-loss"]/div[3]/table/tbody/tr[1]/td[{i}]').text
    number_string = re.findall(r'[\d,\.]+', svalue)
    if number_string:
        clean_string = number_string[0].replace(',', '')  # remove commas
        salesnum = float(clean_string)
        sales.append(salesnum)
    
#Annual other income
oincome=[]
oia_row = driver.find_elements(By.XPATH, '//*[@id="profit-loss"]/div[3]/table/tbody/tr[1]/td')
num_cols = len(oia_row)
for i in range(1, num_cols + 1):
    oivalue=driver.find_element(By.XPATH,f'//*[@id="profit-loss"]/div[3]/table/tbody/tr[5]/td[{i}]').text
    number_string = re.findall(r'[\d,\.]+', oivalue)
    if number_string:
        clean_string = number_string[0].replace(',', '')  # remove commas
        oinum = float(clean_string)
        oincome.append(oinum)

#total revenue
totrev=[]
for i in range(0, num_cols-1):
    val=oincome[i]+sales[i]
    totrev.append(val)
    
#revenue growth
rg=[]
rg.append('0')
for i in range(0, num_cols - 2):
    val=(totrev[i+1]-totrev[i])*100/totrev[i]
    rounded = round(val, 2)
    valper=str(rounded)+"%"
    rg.append(valper)

#consolidated net profit
np=[]
np_row = driver.find_elements(By.XPATH, '//*[@id="profit-loss"]/div[3]/table/tbody/tr[10]/td')
num_cols = len(np_row)
for i in range(1, num_cols + 1):
    npnum=driver.find_element(By.XPATH,f'//*[@id="profit-loss"]/div[3]/table/tbody/tr[10]/td[{i}]').text
    number_string = re.findall(r'[\d,\.]+', npnum)
    if number_string:
        clean_string = number_string[0].replace(',', '')  # remove commas
        npp = float(clean_string)
        np.append(npp)

#Net profit margin
npm=[]
for i in range(0, num_cols - 1):
    val=(np[i]/totrev[i])*100
    rounded = round(val, 2)
    strval=str(rounded)+'%'
    npm.append(strval)

#EPS
eps=[]
eps_row = driver.find_elements(By.XPATH, '//*[@id="profit-loss"]/div[3]/table/tbody/tr[11]/td')
num_cols = len(eps_row)
for i in range(1, num_cols + 1):
    epsnum=driver.find_element(By.XPATH,f'//*[@id="profit-loss"]/div[3]/table/tbody/tr[11]/td[{i}]').text
    number_string = re.findall(r'[\d,\.]+', epsnum)
    if number_string:
        clean_string = number_string[0].replace(',', '')  # remove commas
        epsn = float(clean_string)
        eps.append(epsn)

#EPS growth
epsg=[]
i=0
epsg.append('0')
for i in range(0, num_cols - 2):
    val=(eps[i+1]-eps[i])*100/eps[i]
    rounded = round(val, 2)
    valper=str(rounded)+"%"
    epsg.append(valper)

#dividend payout
dp=[]
div_row = driver.find_elements(By.XPATH, '//*[@id="profit-loss"]/div[3]/table/tbody/tr[12]/td')
num_cols = len(div_row)
for i in range(1, num_cols + 1):
    dpnum=driver.find_element(By.XPATH,f'//*[@id="profit-loss"]/div[3]/table/tbody/tr[12]/td[{i}]').text
    number_string = re.findall(r'[\d,\.]+', dpnum)
    if number_string:
        dp.append(dpnum)
print(dp)

#promoter annual
driver.find_element(By.XPATH,'//*[@id="shareholding"]/div[1]/div[2]/div[1]/button[2]').click()
time.sleep(1)
proan=[]
i=2
proan.append('NA')
proan.append('NA')
proan.append('NA')
while i<11:
    pronum=driver.find_element(By.XPATH,f'//*[@id="yearly-shp"]/div/table/tbody/tr[1]/td[{i}]').text
    proan.append(pronum)
    i+=1

#FII% annual
time.sleep(1)
fiian=[]
i=2
fiian.append('NA')
fiian.append('NA')
fiian.append('NA')
while i<11:
    fiinum=driver.find_element(By.XPATH,f'//*[@id="yearly-shp"]/div/table/tbody/tr[2]/td[{i}]').text
    fiian.append(fiinum)
    i+=1

#DII% annual
time.sleep(1)
diian=[]
i=2
diian.append('NA')
diian.append('NA')
diian.append('NA')
while i<11:
    diinum=driver.find_element(By.XPATH,f'//*[@id="yearly-shp"]/div/table/tbody/tr[2]/td[{i}]').text
    diian.append(diinum)
    i+=1

#ANNUAL ENDS HERE!


driver.quit()