import pandas as pd
import re
import os
from bs4 import BeautifulSoup
import pdfplumber
import random
from tqdm import tqdm
from PIL import Image
from datetime import datetime
import time

number_quiz = 0
number_correct = 0
wrong_time = 3
formal_exam = False
report_list = pd.DataFrame(columns = ["number", "correct","your_answer", "correct_answer"])
image_path = './image/'
test_path = './test/'
report_path = './report/'
pdf_path = './pdf/'
PDF_dict = {"v10":{"pdf":"Cehv10exam.pdf","drop_page":1,"title_line":1,"footer_line":1},"v11":{"pdf":"312-50v11.pdf","drop_page":2,"title_line":1,"footer_line":2}}

def parser(version):
    table = pd.DataFrame(columns = ['number' , 'question', 'answer'])
    alltext = ''
    try:
        pdffile=PDF_dict[version]['pdf']    #pdf檔路徑及檔名
        drop_page = PDF_dict[version]['drop_page']
        title_line = PDF_dict[version]['title_line']
        footer_line = PDF_dict[version]['footer_line']
        pdf = pdfplumber.open(pdf_path+pdffile)
        total_pages = len(pdf.pages)
        firstPage = 1
        process_page = tqdm(total=len(pdf.pages))
        for page in pdf.pages:
            process_page.set_description("頁數 {}".format(page))
            process_page.update(1)
            #print(page.extract_text())
            if(firstPage<=drop_page):
                firstPage = firstPage+1
                continue
            text = page.extract_text()
            # text = text.replace('IT Certification Guaranteed, The Easy Way!','')
            # text = text.replace('312-50v11考古題：最新的EC-COUNCIL 312-50v11認證考試題庫','')
            # text = text[:text.rfind('\n')]#最後一行
            for i in range(title_line):
                text = text[text.find('\n'):]#去除第一行
            for i in range(footer_line):
                text = text[:text.rfind('\n')]#去除最後一行
            alltext += text
        # p0 = pdf.pages[35]
        # text=p0.extract_text()       #讀文字
        # #print(text)
        # text = text.replace('IT Certification Guaranteed, The Easy Way!','')
        # text = text[:text.rfind('\n')]
        # tables = tables = re.split('NO.[0-9]+|Answer: ',text)
        # for txt in tables:
            # print(txt)

        tables = re.split('NO.[0-9]+|Answer: ',alltext)
        totalTable = len(tables)
        for i in range(1,len(tables),2):
            #print(i)
            table = table.append({"number":int((i+1)/2),"question":tables[i],"answer":tables[i+1]},ignore_index=True)
            #table = table.append({"number":"i","question":"i","answer":"i"},ignore_index=True)
            #print(table[i])
        #print(totalTable)
        table.to_csv(test_path+version+"_test.csv")
        #table.to_json("test.json")
    except:
        print("檔案錯誤...")
def test():
    global number_quiz,formal_exam
    pd.set_option("display.max_colwidth",500)
    try:
        version = input("請選擇版本(v10) (v11):\n")
        if version == '':
            version = "v10"
            print("v10")
        else:
            version = version.lower()
        file = version+"_test.csv"
        if(not os.path.isfile(test_path+file)):
            print("parse PDF, please wait...")
            parser(version)
        table = pd.read_csv(test_path+file)
        print("總題數: {}".format(len(table)))
        #num = random.randint(1,720)
        list = range(1,len(table)+1)
        lists = random.sample(list, len(list))
        exam = input("是否正式考試? yes(y) or no(n)\n")
        if exam.lower()=="yes" or exam.lower()=="y":
            formal_exam = True
        elif exam.lower()=="no" or exam.lower()=="n":
            formal_exam = False
        else:
            raise
        number_quiz = int(input("測驗題數:"))
        if(number_quiz>len(table) or number_quiz<=0):
            raise
        n = number_quiz
        process = tqdm(total=n)
        for num in lists:
            if(n==0):
                break
            print("\n\033[01;34m\033[01;mQuestion {}:\033[0m\n{}".format(str(num),table.at[num-1,"question"]))
            im_path = image_path+version+'/'+str(num)+".png"
            if(os.path.isfile(im_path)):#是否有圖片
                print("請看附圖...\n")
                time.sleep(1)
                im = Image.open(r"{}".format(im_path))
                im.show()
            #print("Question "+str(num)+":"+table.at[num-1,"question"])
            answer = input().upper()
            check_input(table,num,answer)
            n = n-1
        
        count_score()
        process.set_description("分數:")
        process.update(number_correct)
    except:
        print("輸入錯誤")
    
    get_error_record()
    
def check_input(table,num,answer):
    global number_correct,report_list
    correct_answer_description = table.at[num-1,"answer"]
    #print(correct_answer_description[:correct_answer_description.find('\n')])
    should_answer = True
    answer_count = 1
    while(should_answer):
        correct_answer = correct_answer_description[:correct_answer_description.find('\n')]
        if(correct_answer_description[:correct_answer_description.find('\n')]==answer):#第一行
            if(not formal_exam):
                print("\033[01;32m\033[01;mcorrect\033[0m")
            should_answer = False
            if(answer_count==1):
                number_correct = number_correct+1
                report_list = report_list.append({"number":num,"correct":"yes","your_answer":answer,"correct_answer":correct_answer},ignore_index=True)
        else:
            if(answer_count==1):
                report_list = report_list.append({"number":num,"correct":"no","your_answer":answer,"correct_answer":correct_answer},ignore_index=True)
            answer_count = answer_count+1
            if(not formal_exam):
                print("\033[01;31m\033[01;mwrong\033[0m")
                print("Think about it...\n再想想...")
                if(answer_count>wrong_time):
                    break
                should_answer = True
                answer = input().upper()
            else:
                should_answer = False
    if(not formal_exam):
        print("\n\033[01;33m\033[01;m解答:\033[0m")
        print(correct_answer_description)

def count_score():
    print("總測驗題數: {}".format(number_quiz))
    print("正確題數: {}".format(number_correct))
    #print("分數: {}%".format(int((number_correct/number_quiz)*100)))
    
def get_error_record():
    global report_list
    try:
        report_list = report_list.append({"number":"number of quiz","correct":number_quiz},ignore_index=True)
        report_list = report_list.append({"number":"number of corect","correct":number_correct},ignore_index=True)
        report_list = report_list.append({"number":"score","correct":"{}%".format(int((number_correct/number_quiz)*100))},ignore_index=True)
        report_list.index = report_list.index+1
        report_list.to_csv(report_path+datetime.today().strftime('%Y_%m_%d')+"_report.csv")
    except:
        print("報告無法產出...")
    
if __name__=="__main__":
    #parser("V10")
    test()