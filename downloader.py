from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time
import re
from tqdm import tqdm
from lxml import etree
import pandas as pd
import urllib.request

########################################################
savepath_prefix = ''
csv_path = ''
header = {
    "User-Agent": "'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36'"
}

options = webdriver.ChromeOptions()
 
# 处理SSL证书错误问题
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')
 
# 忽略无用的日志
options.add_experimental_option("excludeSwitches", ['enable-automation', 'enable-logging'])
options.add_argument('user-agent=%s' % header)
#driver = webdriver.Chrome(options=options)

class Sequence:
    def __init__(self, mainID):
        self.url = "https://www.ncbi.nlm.nih.gov/nuccore/"+mainID
        self.sequence_mid = mainID
        self.id = ''
        self.fullname = ''
        self.keywords=['hexon','hexonprotein','fiber','fiberprotein','fiber1','fiber1protein','fiber2','fiber2protein','fiberprotein1','fiberprotein2'
                       ,'fiber-1','fiber-1protein','fiber-2','fiber-2protein','fiberprotein-1','fiberprotein-2']
        self.keyword_list=[]
        #self.startandend_list = []
        
        #创建默认的关键词列表
        k = {'keyword': 'hexon', 'startandend': [], 'link':[]}
        self.keyword_list.append(k)
        k = {'keyword': 'hexonprotein', 'startandend': [], 'link':[]}
        self.keyword_list.append(k)
        k = {'keyword': 'fiber', 'startandend': [], 'link':[]}
        self.keyword_list.append(k)
        k = {'keyword': 'fiberprotein', 'startandend': [], 'link':[]}
        self.keyword_list.append(k)
        k = {'keyword': 'fiber1', 'startandend': [], 'link':[]}
        self.keyword_list.append(k)
        k = {'keyword': 'fiber1protein', 'startandend': [], 'link':[]}
        self.keyword_list.append(k)
        k = {'keyword': 'fiber2', 'startandend': [], 'link':[]}
        self.keyword_list.append(k)
        k = {'keyword': 'fiber2protein', 'startandend': [], 'link':[]}
        self.keyword_list.append(k)
    #################################################################
    def make_dlink(self, id, start, end):
        link = f'https://www.ncbi.nlm.nih.gov/sviewer/viewer.cgi?tool=portal&save=file&log$=seqview&db=nuccore&report=fasta&id={id}&from={start}&to={end}&conwithfeat=on&withparts=on&show-sequence=on&hide-cdd=on&ncbi_phid=CE8BE4195EFFF2610000000002A70229'
        return link 
       
    def function(self):
        id = ''
        #startandend_list = []
        #标志位
        flag = True
        while flag:
            try:
                # 打开页面
                driver = webdriver.Chrome(options=options)
                page = driver.get(self.url)
                time.sleep(3)

                Goto_element = driver.find_element(By.XPATH, "/html/body/div[1]/div[1]/form/div[1]/div[4]/div/div[5]/div[2]/div[1]/div/div/div[1]/div/a")
                fullid = Goto_element.get_attribute('href')


                #获取隐式id
                id = fullid.split('#')[-1] 
                id = id.split('_')[0] #
                id = id.split('goto')[-1] #without 'goto'
                self.id = id

                #获取所有起止对
                text = driver.page_source
                html = etree.HTML(text)
                keyword_info_lst = html.xpath("//*[@class='feature']/text()")

                for i in range(len(keyword_info_lst)):
                    keyword_info_lst[i] = re.sub(r"\n", "", keyword_info_lst[i])
                    keyword_info_lst[i] = re.sub(r"\s+", "", keyword_info_lst[i])

                    if re.search(r'(\"hexon\"|hexonprotein|\"fiber\"|fiberprotein|\"fiber1\"|fiber1protein|\"fiber2\"|fiber2protein|\"fiber-1\"|\"fiber-2\")',keyword_info_lst[i]):
                        #如果匹配到了hexion\fiber\fiber1\fiber2
                        keyword = ''
                        #确认到底是什么关键字
                        #j = keyword_info_lst[i].find('product=')+9
                        if 'product=' in keyword_info_lst[i]:
                            for j in range(keyword_info_lst[i].find('product=')+9,len(keyword_info_lst[i])):
                                if keyword_info_lst[i][j] == '"':
                                    break
                            _keyword = keyword_info_lst[i][keyword_info_lst[i].find('product=')+9:j]
                            if _keyword in self.keywords:
                                keyword = _keyword

                        elif 'gene=' in keyword_info_lst[i]:
                            for j in range(keyword_info_lst[i].find('gene=')+6,len(keyword_info_lst[i])):
                                if keyword_info_lst[i][j] == '"':
                                    break
                            _keyword = keyword_info_lst[i][keyword_info_lst[i].find('gene=')+6:j]
                            if _keyword in self.keywords:
                                keyword = _keyword

                        #认为note和product是互斥的，note可以推翻product
                        #note不一定是关键字，如果note是关键字则以note为准；不是关键字以product为准
                        if 'note=' in keyword_info_lst[i]:
                            for j in range(keyword_info_lst[i].find('note=')+6,len(keyword_info_lst[i])):
                                if keyword_info_lst[i][j] == '"':
                                    break
                            _keyword = keyword_info_lst[i][keyword_info_lst[i].find('note=')+6:j]
                            if _keyword in self.keywords:
                                keyword = _keyword

                        #去掉“-”符号
                        if keyword == 'fiber-1':
                            keyword = 'fiber1'
                        if keyword == 'fiber-2':
                            keyword = 'fiber2'
                        if keyword == 'fiber-1protein':
                            keyword = 'fiber1protein'
                        if keyword == 'fiber-2protein':
                            keyword = 'fiber2protein'
                        if keyword == 'fiberprotein-1':
                            keyword = 'fiber1protein'
                        if keyword == 'fiberprotein-2':
                            keyword = 'fiber2protein'

                        #意思一样
                        if keyword == 'fiberprotein1':
                            keyword = 'fiber1protein'
                        if keyword == 'fiberprotein2':
                            keyword = 'fiber2protein'

                        startAndend = keyword_info_lst[i].split('/')[0]
                        for item in self.keyword_list:
                            if item['keyword'] == keyword:
                                item['startandend'].append(startAndend)   

                #生成下载链接
                for item in self.keyword_list:
                    for startAndend in item['startandend']:
                        #这里是为了处理“..>”这种极个别由于上传者打错的情况
                        if '>' in startAndend:
                            startAndend = startAndend.replace('>','')
                        #处理 complement(10793..13534)
                        if 'complement' in startAndend:
                            startAndend = startAndend[11:len(startAndend)-1]
                        start = startAndend.split('..')[0]
                        end = startAndend.split('..')[-1]
                        link = self.make_dlink(id=self.id,start = start, end = end)
                        item['link'].append(link)

                flag = False
                driver.close()

            except NoSuchElementException:
                print(f'获取{self.sequence_mid}失败，将重试= =')
                time.sleep(3)
                driver.close()
                continue
        
    def test(self):
        #标志位
        flag = True
        # 打开页面
        driver = webdriver.Chrome(options=options)
        page = driver.get(self.url)

        #Goto = driver.find_element(By.XPATH, '//*[@id="gotopopper1488570574_0"]')
        #Goto_element = driver.find_element(By.XPATH, "/html/body/div[1]/div[1]/form/div[1]/div[4]/div/div[5]/div[2]/div[1]/div/div/div[1]/div/a")
        #fullid = Goto_element.get_attribute('href')

        # id = fullid.split('#')[-1] #
        # id = id.split('_')[0] #
        # id = id.split('goto')[-1] #without 'goto'
        # self.id = id
        # flag = False
        # driver.close()
        time.sleep(5)
        #target = driver.find_elements(By.XPATH, "//*[@class='feature']/text()[1]")
        #target = driver.find_elements(By.CLASS_NAME,'feature')
        #print(target[0])

        text = driver.page_source
        html = etree.HTML(text)
        keyword_info_lst = html.xpath("//*[@class='feature']/text()")
        # for i in range(len(position_info_lst)):
        #     print(f'这是第{i}个元素：')
        #     print(position_info_lst[i])
        #     print('\n')

        for i in range(len(keyword_info_lst)):
            keyword_info_lst[i] = re.sub(r"\n", "", keyword_info_lst[i])
            keyword_info_lst[i] = re.sub(r"\s+", "", keyword_info_lst[i])

            if 'fiber' or 'fiberprotein' or 'fiber1' or 'fiber2' or 'fiber1protein' or 'fiber2protein' in keyword_info_lst[i]:
                #如果匹配到了hexion\fiber\fiber1\fiber2,拿到前面的起止信息
                #以符号/进行分割，找到product，查看后面的字段是否为上述产物
                if 'hexon' or 'hexonprotein' or 'fiber' or 'fiberprotein' or 'fiber1' or 'fiber2' or 'fiber1protein' or 'fiber2protein' in keyword_info_lst[i]:
                    startAndend = keyword_info_lst[i].split('/')[0]
                    start = startAndend.split('..')[0]
                    end = startAndend.split('..')[-1]
                    print(start)
                    print(end)


        #去换行符 去空格
        # keyword_info_lst[59] = re.sub(r"\n", "", keyword_info_lst[59])
        # keyword_info_lst[59] = re.sub(r"\s+", "", keyword_info_lst[59])
        # print(keyword_info_lst[59])

        #如果匹配到了hexion\fiber\fiber1\fiber2,拿到前面的起止信息
        #以符号/进行分割，找到product，查看后面的字段是否为上述产物
        # if 'hexon' or 'hexonprotein' or 'fiber' or 'fiberprotein' or 'fiber1' or 'fiber2' or 'fiber1protein' or 'fiber2protein' in keyword_info_lst[59]:
        #     startAndend = keyword_info_lst[59].split('/')[0]
        #     start = startAndend.split('..')[0]
        #     end = startAndend.split('..')[-1]
        #     print(start)
        #     print(end)


        #print(id)
        #Goto.click()
         

#whole workstream
class Pipline:
    def __init__(self, Sequence_list):
        # 传入seq队列
        self.seq_list = Sequence_list

            
    ###############Function#################
    
    #TODO：批量下载，重命名下载文件，记得下载不截断的文件
    #urllib.request.urlretrieve(url, save_path)
    def download(self):
        print("开始下载！")
        for seq in tqdm(self.seq_list):
            for item in seq.keyword_list:
                keyword = item['keyword']
                i = 0
                for i in range(len(item['startandend'])):
                    startandend = item['startandend'][i]
                    if '>' in startandend:
                        startandend = startandend.replace('>','')
                    link = item['link'][i]
                
                    filename = seq.fullname + "_" + keyword + "_" + startandend
                    savepath = savepath_prefix + filename + ".fasta"
                    urllib.request.urlretrieve(link, savepath)
            #下载全基因组
            link = f'https://www.ncbi.nlm.nih.gov/sviewer/viewer.cgi?tool=portal&save=file&log$=seqview&db=nuccore&report=fasta&id={seq.id}&conwithfeat=on&withparts=on&show-sequence=on&hide-cdd=on&ncbi_phid=CE8BE4195EFFF2610000000002A70229'
            savepath = savepath_prefix + seq.fullname + ".fasta"
            urllib.request.urlretrieve(link, savepath)
            print("下载完毕！")

                    

    def workflow(self):
        for seq in tqdm(self.seq_list):
            #获取隐式id和起止对
            seq.function()
        self.download()
            
###############################################################
        
if __name__ == "__main__":
    seq_list = []
    #创建seqlist
    data = pd.read_csv(csv_path,encoding="utf-8")
    data = data.values.tolist()

    for i in range(len(data)):
        mainID = data[i][2]
        seq = Sequence(mainID=mainID)
        if pd.isna(data[i][1]):
            seq.fullname = data[i][0] + "_"  + data[i][2]
        else:
            seq.fullname = data[i][0] + "_" + data[i][1] + "_" + data[i][2]
        seq.fullname = seq.fullname.strip()
        # print(seq.fullname)
        # print(len(seq.fullname))
        seq_list.append(seq)

    ############TEST###############
    # mainID = 'JF510462'
    # seq = Sequence(mainID=mainID)
    # seq_list.append(seq)
    # mainID = 'DQ460220'
    # seq = Sequence(mainID=mainID)
    # seq_list.append(seq)
    # mainID = 'MH777395'
    # seq = Sequence(mainID=mainID)
    # seq_list.append(seq)
    #mainID = 'HE608152'
    #seq = Sequence(mainID=mainID)
    # seq_list.append(seq)
    ############TEST##############


    pip = Pipline(seq_list)
    pip.workflow()

    # #print(pip.seqList_info)
    #print(pip.dlink_list)

    #seq.function()
    #print(seq.id)
    #print(seq.keyword_list)



