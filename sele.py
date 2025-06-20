# sele.py
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import re
import sys
import string
sys.stdout.reconfigure(encoding='utf-8')

def extract_number(text):
    matches = re.findall(r'[\d,.]+', text)
    if matches:
        num = matches[0].replace(',', '')
        try:
            return float(num)
        except ValueError:
            pass
    return 0.0

def annual_info(driver):
    #Annual sales
    sales=[]
    salesa_row = driver.find_elements(By.XPATH, '//*[@id="profit-loss"]/div[3]/table/tbody/tr[1]/td')
    num_cols = len(salesa_row)
    nca=num_cols
    for i in range(2, num_cols + 1):
        svalue=driver.find_element(By.XPATH,f'//*[@id="profit-loss"]/div[3]/table/tbody/tr[1]/td[{i}]').text
        salesnum = extract_number(svalue)
        sales.append(salesnum)

    #Annual other income
    oincome=[]
    oia_row = driver.find_elements(By.XPATH, '//*[@id="profit-loss"]/div[3]/table/tbody/tr[1]/td')
    num_cols = len(oia_row)
    for i in range(2, num_cols + 1):
        oivalue=driver.find_element(By.XPATH,f'//*[@id="profit-loss"]/div[3]/table/tbody/tr[5]/td[{i}]').text
        oinum = extract_number(oivalue)
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
        npp = extract_number(npnum)
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
    for i in range(2, num_cols + 1):
        epsnum=driver.find_element(By.XPATH,f'//*[@id="profit-loss"]/div[3]/table/tbody/tr[11]/td[{i}]').text        
        epsn = extract_number(epsnum)
        eps.append(epsn)

    #EPS growth
    epsg=[]
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

    #promoter annual
    driver.find_element(By.XPATH,'//*[@id="shareholding"]/div[1]/div[2]/div[1]/button[2]').click()
    time.sleep(1)
    proan=[]
    proan_row = driver.find_elements(By.XPATH, '//*[@id="yearly-shp"]/div/table/tbody/tr[1]/td')
    num_cols = len(proan_row)
    if num_cols<nca :
        for i in range(nca-num_cols):
            proan.append("NA")

    for i in range(1, num_cols + 1):
        pronum=driver.find_element(By.XPATH,f'//*[@id="yearly-shp"]/div/table/tbody/tr[1]/td[{i}]').text
        number_string = re.findall(r'[\d\.]+', pronum)
        if not number_string: continue
        proan.append(pronum)

    #FII% annual
    time.sleep(1)
    fiian=[]
    afii_row = driver.find_elements(By.XPATH, '//*[@id="yearly-shp"]/div/table/tbody/tr[2]/td')
    num_cols = len(afii_row)
    if num_cols<nca :
        for i in range(nca-num_cols):
            fiian.append("NA")

    for i in range(1, num_cols + 1):
        fiinum=driver.find_element(By.XPATH,f'//*[@id="yearly-shp"]/div/table/tbody/tr[2]/td[{i}]').text
        number_string = re.findall(r'[\d\.]+', fiinum)
        if not number_string: continue
        fiian.append(fiinum)


    #DII% annual
    time.sleep(1)
    diian=[]
    adii_row = driver.find_elements(By.XPATH, '//*[@id="yearly-shp"]/div/table/tbody/tr[3]/td')
    num_cols = len(adii_row)
    if num_cols<nca :
        for i in range(nca-num_cols):
            diian.append("NA")

    for i in range(1, num_cols + 1):
        diinum=driver.find_element(By.XPATH,f'//*[@id="yearly-shp"]/div/table/tbody/tr[3]/td[{i}]').text
        number_string = re.findall(r'[\d\.]+', diinum)
        if not number_string: continue
        diian.append(diinum)
    return {
        "asales": sales,
        "aOther_Income": oincome,
        "aTotal_Revenue": totrev,
        "aRevenue_Growth":rg,
        "aNet_Profit":np,
        "aNet_Profit_Margin": npm,
        "aEPS": eps,        
        "aEPS_Growth": epsg,
        "aDivident_Payout": dp,
        "aPromoter": proan,
        "aFII": fiian,
        "aDII": diian
    }
    
    
    
def quaterly_info(driver):
    #Quaterly sales
    qsales=[]
    sales_row = driver.find_elements(By.XPATH, '//*[@id="quarters"]/div[3]/table/tbody/tr[1]/td')
    num_cols = len(sales_row)
    nc=num_cols
    for i in range(2, num_cols + 1):
        qsvalue=driver.find_element(By.XPATH,f'//*[@id="quarters"]/div[3]/table/tbody/tr[1]/td[{i}]').text
        qsalesnum = extract_number(qsvalue)
        qsales.append(qsalesnum)
            

    #Quaterly other income
    qoincome=[]
    qoi_row = driver.find_elements(By.XPATH, '//*[@id="quarters"]/div[3]/table/tbody/tr[5]/td')
    num_cols = len(qoi_row)
    for i in range(2, num_cols + 1):
        qoivalue=driver.find_element(By.XPATH,f'//*[@id="quarters"]/div[3]/table/tbody/tr[5]/td[{i}]').text
        qoinum = extract_number(qoivalue)
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
        nppq = extract_number(npqnum)
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
    for i in range(2, num_cols + 1):
        epsqnum=driver.find_element(By.XPATH,f'//*[@id="quarters"]/div[3]/table/tbody/tr[11]/td[{i}]').text
        epsqn = extract_number(epsqnum)
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

    return {
        "qsales": qsales,
        "qOther_Income": qoincome,
        "qTotal_Revenue": qtotrev,
        "qRevenue_Growth":rgq,
        "qNet_Profit":npq,
        "qNet_Profit_Margin": npqm,
        "qEPS": epsq,        
        "qEPS_Growth": epsgq,
        "qPromoter": qpro,
        "qFII": qfii,
        "qDII": qdii
    }


    #Quaterly info ends here   
    
    
    
    
def run_scraper(stock):
    # INITIALIZE webdriver
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.chrome.options import Options

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=options
    )

    #navigate to screener.com
    driver.get("https://www.screener.in/")

    #driver.maximize_window()
    # ENTER user-specified stock
    driver.find_element(By.XPATH, "/html/body/main/div[2]/div/div/div/input").send_keys(stock)
    time.sleep(1)
    driver.find_element(By.XPATH, "/html/body/main/div[2]/div/div/div/ul/li[1]").click()

    #shareholding patterns
    PROMOTERS = driver.find_element(By.XPATH, '//*[@id="quarterly-shp"]/div/table/tbody/tr[1]/td[13]').text
    FII = driver.find_element(By.XPATH, '//*[@id="quarterly-shp"]/div/table/tbody/tr[2]/td[13]').text
    DII = driver.find_element(By.XPATH, '//*[@id="quarterly-shp"]/div/table/tbody/tr[3]/td[13]').text
    PUBLIC = driver.find_element(By.XPATH, '//*[@id="quarterly-shp"]/div/table/tbody/tr[5]/td[13]').text
    CMP = driver.find_element(By.XPATH, '//*[@id="top-ratios"]/li[2]/span[2]/span').text
    F_HIGH = driver.find_element(By.XPATH, '//*[@id="top-ratios"]/li[3]/span[2]/span[1]').text
    F_LOW = driver.find_element(By.XPATH, '//*[@id="top-ratios"]/li[3]/span[2]/span[2]').text
    cmpn=extract_number(CMP)
    fln=extract_number(F_LOW)
    fhn=extract_number(F_HIGH)
    HLP=((cmpn-fln)*100)/(fhn-fln)
    roundedh = round(HLP, 2)
    hlper=str(roundedh)+"%"
    PB = driver.find_element(By.XPATH, '//*[@id="top-ratios"]/li[5]/span[2]').text
    driver.find_element(By.XPATH, '//*[@id="company-chart-metrics"]/button[2]').click()
    time.sleep(1)
    #pe5yr
    pe_5yr_f = driver.find_element(By.XPATH, '//*[@id="chart-legend"]/label[2]/span').text
    pe5l = pe_5yr_f.split()
    pe_5yr = pe5l[3]

    #pe3yr
    driver.find_element(By.XPATH, '//*[@id="company-chart-days"]/button[4]').click()
    time.sleep(1)
    pe_3yr_f = driver.find_element(By.XPATH, '/html/body/main/section[1]/div[3]/label[2]/span').text
    pe3l = pe_3yr_f.split()
    pe_3yr = pe3l[3]

    #pe1yr
    driver.find_element(By.XPATH, '//*[@id="company-chart-days"]/button[3]').click()
    time.sleep(1)
    pe_1yr_f = driver.find_element(By.XPATH, '//*[@id="chart-legend"]/label[2]/span').text
    pe1l = pe_1yr_f.split()
    pe_1yr = pe1l[3]

    #pe10yr
    driver.find_element(By.XPATH, '//*[@id="company-chart-days"]/button[6]').click()
    time.sleep(1)
    pe_10yr_f = driver.find_element(By.XPATH, '//*[@id="chart-legend"]/label[2]/span').text
    pe10l = pe_10yr_f.split()
    pe_10yr = pe10l[3]

    #DY
    DY = driver.find_element(By.XPATH, '//*[@id="top-ratios"]/li[6]/span[2]/span').text
    
    #Run the two functions
    quaterly_data=quaterly_info(driver)
    annual_data = annual_info(driver)

    # At the end, close driver:
    driver.quit()
    
    # RETURN collected data as a dict:
    return {
        
        "PROMOTERS": PROMOTERS,
        "FII": FII,
        "DII": DII,
        "PUBLIC": PUBLIC,
        "CMP": CMP,
        "F_HIGH": F_HIGH,
        "F_LOW": F_LOW,
        "HiLoPer":hlper,
        "PB": PB,
        "pe_1yr": pe_1yr,
        "pe_3yr": pe_3yr,
        "pe_5yr": pe_5yr,
        "pe_10yr": pe_10yr,
        "DY": DY,
        **quaterly_data,
        **annual_data
    }

# Allow standalone use:
if __name__ == "__main__":
    stock_symbol = input("Enter stock name or symbol: ")
    result = run_scraper(stock_symbol)
    print(result)

