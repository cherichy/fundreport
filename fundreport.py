import requests
from bs4 import BeautifulSoup as bs
import numpy as np
import pandas as pd
np.set_printoptions(precision=4, suppress=True)

def info_fund(fid):
    soup=bs(requests.get('http://fund.eastmoney.com/'+fid+'.html').content,features="html.parser")
    value=float(soup.find(id="gz_gsz").text)
    ratio=float(soup.find(id="gz_gszzl").text[:-1])/100
    delta=soup.find(id="gz_gszze").text
    delta=float(delta[1:]) if delta[0]=='+' else float(delta)
    # After 20:00
    if abs(value/(1+ratio)-delta/ratio)>0.005:
        ratio=(1-delta/value)*(1+ratio)-1
        value-=delta
        delta=value*ratio/(1+ratio)
    return value,ratio,delta

def cal_return(fid,share,cost):
    res=info_fund(fid)
    value,ratio,delta=res
    total_return=(value-cost)*share
    total_ratio=value/cost-1
    today_return=delta*share
    today_ratio=ratio
    return value,today_ratio,today_return,total_ratio,total_return

# Edit the fund No., share and cost.
funds=[
    ["008327",10000,1]
]

ret_report=np.zeros((len(funds),5))
for idx,fund in enumerate(funds):
    res=cal_return(*fund)
    ret_report[idx,:]=np.array(list(res))

total_cost=sum(i[1]*i[2] for i in funds)
total_return=ret_report[:,4].sum()
total_money=total_cost+total_return
total_ratio=total_return/total_cost
today_return=ret_report[:,2].sum()
today_ratio=today_return/(total_money-today_return)

total_report=np.array([today_ratio,today_return,total_ratio,total_return])

with open("report.csv",'w') as f:
    f.write("基金号, 份额, 成本价, 今日价, 今日收益率, 今日收益, 总收益率, 总收益\n")
    for fund,ret in zip(funds,ret_report):
        f.write("%s, %.2f, %.4f, %.4f, %.2f%%, %.2f, %.2f%%, %.2f\n"%(*fund,ret[0],ret[1]*100,ret[2],ret[3]*100,ret[4]))
    f.write("汇总,,%.2f,%.2f,%.2f%%, %.2f, %.2f%%, %.2f\n"%(total_cost,total_money,today_ratio*100,today_return,total_ratio*100,total_return))
