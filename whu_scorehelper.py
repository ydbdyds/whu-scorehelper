#!/usr/bin/env python
# -*- coding:utf-8 -*-
import datetime
import smtplib
from email.mime.text import MIMEText
import time
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains 
import warnings

warnings.filterwarnings("ignore", category=Warning)
chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])#提示浏览器不是selenium
chrome_options.add_argument('log-level=3')
chrome_options.add_argument('--headless')  # 无头
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--no-sandbox')  # 这个配置很重要
# chrome_options.add_experimental_option('excludeSwitches',
#                                        ['enable-automation'])  # 此步骤很重要，设置为开发者模式，防止被各大网站识别出来使用了Selenium
oldlist = ['1']

class Selenium:
     
    def __init__(self):
        self.driver = webdriver.Chrome(options=chrome_options)  # 有配置的初始化浏览器
        #self.driver = webdriver.Chrome()  # 不使用有配置的，方便看操作
        self.driver.maximize_window()  # 窗口最大化


    def sendmail(self,titile,msg):  #邮箱需开启stmp服务
        mailhost = 'smtp.qq.com'   
        mailuser = ''  #使用的邮箱
        mailpsd = ''   #授权码或密码
        sender = ''   #发送者
        receivers = ''    #接收者

        msgs = MIMEText(msg,'html','utf-8')
        msgs['Subject'] = titile
        msgs['From'] = mailuser
        msgs['To'] = receivers

        smtp = smtplib.SMTP(mailhost)
        smtp.login(mailuser,mailpsd)
        smtp.sendmail(sender,receivers,msgs.as_string())
        smtp.quit()
        print('success')

    def compareTwoList(self,oldList,newList):
        diflist=[]
        for sub in newList:
            if(oldList.count(sub)==0):
                diflist.append(sub)
                
        return diflist


    def login(self, username, password):
        self.driver.get('http://ehall.whu.edu.cn/appShow?appId=5382714380693158')  # 走信息门户认证的教务系统url，不用输入验证码
        # 找到输入框并输入账号密码
        Username = self.driver.find_element_by_id("username")
        Username.send_keys(username)
        Password = self.driver.find_element_by_id("password")
        Password.send_keys(password)
        time.sleep(0.2)
        self.driver.find_element_by_xpath('//*[@id="casLoginForm"]/p[5]/button').click()  # 登录按钮
        newlist = []
        
        try:
            # name=self.driver.find_element_by_id("ampHeaderToolUserName").text#获取姓名,内容为空，弃用
            name = self.driver.find_element_by_id("nameLable").text  # 获取学生姓名
            acade = self.driver.find_element_by_id("acade").text  # 获取学生院系
            # cookies = self.driver.get_cookies()[0]
            # print('登录成功 ...')
            # self.driver.quit()
            # html = self.driver.execute_script("return document.documentElement.outerHTML")
            html = self.driver.find_element_by_xpath('//*[@id="system"]').get_attribute('onclick')
            # 不要用 driver.page_source，那样得到的页面源码不标准
            #print(html)
            csrftoken = html.split(",")[0].split('csrftoken=')[-1]
            
            score = self.driver.find_element_by_id("btn3") #成绩按钮
            
            
            try:
                ActionChains(self.driver).move_to_element(score).perform() #悬停展开二级菜单
                
                ss=self.driver.find_element_by_xpath('//li[@class="green"]') #点击成绩查询
                ss.click()
                time.sleep(1.2)
                self.driver.switch_to_frame('page_iframe')  #切换iframe
                self.driver.switch_to_frame('iframe0')       #切换至成绩二级iframe 否则无法找到页面元素
                
                
                lessonNamelist = self.driver.find_elements_by_xpath('//table[@class="table listTable"]/tbody/tr')  #行位置
                # print(len(lessonNamelist))
                
                for lessonName in lessonNamelist:
                    lesson=lessonName.find_elements_by_xpath('td[@class="lessonName"]')  #课程名字
                    lessonscore=lessonName.find_elements_by_xpath('td[11]') #课程成绩
                    if (len(lessonscore)>0 and lessonscore[0].text!=""):   #已出成绩的科目加入newList
                        newlist.append(lesson[0].text+" "+lessonscore[0].text)
                global oldlist
                diflist = self.compareTwoList(oldlist,newlist) 
                oldlist = newlist
                if diflist==[] or len(diflist)==0:  #成绩无更新
                    return
                else:
                    self.sendmail('新成绩出来了',','.join(diflist))  #将列表转换str 以逗号分隔

                # print(len(oldlist))
                # print(oldlist)

                # demo = lessonNamelist[1].find_elements_by_tag_name("tr")
                
                # print(len(demo))
                # for lessonName in lessonNa
                # list:
                #     tdlist=lessonName.find_elements_by_tag_name("td")
                #     for item in tdlist:
                #         text = item.text
                #         print(text)
                

            except Exception as e:
                print(str(e))
            return True, acade, name, self.driver.get_cookies(), csrftoken
            
        

        except Exception as e:
            print(str(e))
            try:
                msg = self.driver.find_element_by_id("msg").text
            except Exception as e:
                # time.sleep(5)
                # cpatchaError=self.driver.find_element_by_id("cpatchaError").text
                print(str(e))
                msg = '有问题'
            # self.driver.quit()
            return False, msg


if __name__ == '__main__':
    username = ''  # 你的信息门户账号
    password = ''  # 你的信息门户账号对应的密码
    
    #spider.sendmail("测试","xy")

    while(True):
        spider = Selenium()
        spider.login(username=username, password=password)  # 查看登录结果
        print('最后一次运行时间:',datetime.datetime.now())
        time.sleep(600)
   