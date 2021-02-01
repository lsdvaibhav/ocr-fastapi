from fastapi import FastAPI, Request, File, UploadFile, BackgroundTasks
from fastapi.templating import Jinja2Templates
import shutil
import ocr
import os
import uuid
import json
import re
import pdfplumber

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/v1/extract_text_from_img")
async def extract_text(image: UploadFile = File(...)):
    temp_file_img = _save_file_to_disk(image, path="temp", save_as="img_temp")
    text = await ocr.read_image(temp_file_img)
    data   = genrateData(text)
    return {"filename": image.filename, "text": data}

@app.post("/api/v1/extract_text_from_pdf")
async def extract_tex_from_pdf(pdf: UploadFile = File(...)):
    temp_file_pdf = _save_file_to_disk(pdf, path="temp", save_as="pdf_temp")
    with pdfplumber.open(temp_file_pdf) as pdffile:
        first_page = pdffile.pages[0]
        #find big one table and extract text from it
        rows = first_page.extract_table(table_settings={})
        #extract registration number 
        text1 = str(first_page.extract_text())
        reg_pos = text1.find('Registration Number :')#position
        registrationNumber = text1[reg_pos+21:reg_pos+33]#twelve chars 

    #dictionary result 
    data={"registrationNumber":registrationNumber}
    for index,row in enumerate(rows):
        value = ""
        if index <8:
            for each in row[2:]:
                if each != None:
                    value += each 
            key = row[1]
            data.__setitem__(key, value) 
        else:
            key = row[0]
            data.__setitem__(key, value) 
    return {"filename": pdf.filename, "text": data}

def _save_file_to_disk(uploaded_file, path=".", save_as="default"):
    extension = os.path.splitext(uploaded_file.filename)[-1]
    temp_file = os.path.join(path, save_as + extension)
    with open(temp_file, "wb") as buffer:
        shutil.copyfileobj(uploaded_file.file, buffer)
    return temp_file

def genrateData(text):
    text = text.replace('[',' ')
    text = text.replace(']',' ')
    text= text.replace('|',' ')
    text = re.sub(' +', ' ',text)
    text = text.lower()
    text = text[text.find('registration number :'):text.find('note')]
    text1= ''
    datalist = []
    for each in text.split('\n'):
        if len(each) >1:
            datalist.append(each)
            for eachh in each.split(' '):
                if  eachh == '' or eachh== ' ':
                    pass
                else :
                    text1 =  text1+ eachh+' '

    rn = text1[text1.find('registration number :')+len('registration number :'):text1.find('registration number :')+len('registration number :')+12]
    ln = text1[text1.find('legal name')+len('legal name'):text1.find('trade name')]
    tnia = text1[text1.find('trade name, if any')+len('trade name, if any'):text1.find('constitution of business')]
    cob = text1[text1.find('constitution of business')+len('constitution of business'):text1.find('address of principal place of')]
    addBusiness = text1[text1.find('address of principal place of'):]
    address = addBusiness[addBusiness.find('address of principal place of')+len('address of principal place of'):addBusiness.find('business')]+addBusiness[addBusiness.find('business')+8:addBusiness.find('date of liability')]
    dol = addBusiness[addBusiness.find('date of liability')+len('date of liability'):addBusiness.find('period of validity')]
    pov = addBusiness[addBusiness.find('period of validity')+len('period of validity'):addBusiness.find('type of registration')]
    tor = addBusiness[addBusiness.find('type of registration')+len('type of registration'):addBusiness.find('particulars of approving authority')]
    poaa = addBusiness[addBusiness.find('particulars of approving authority')+len('particulars of approving authority'):addBusiness.find('signature')]
    sign = addBusiness[addBusiness.find('signature')+len('signature'):addBusiness.find('name')]
    name = addBusiness[addBusiness.find('name')+len('name'):addBusiness.find('designation')]
    des = addBusiness[addBusiness.find('designation')+len('designation'):addBusiness.find('jurisdictional office')]
    jo = addBusiness[addBusiness.find('jurisdictional office')+len('jurisdictional office'):addBusiness.find('date of issue of certificate')]
    doi = addBusiness[addBusiness.find('date of issue of certificate')+len('date of issue of certificate'):addBusiness.find('note')]
    
    data = {"gstNumber" :rn,
        "registrationNumber":rn,
        "legalName":ln,
        "tradeName":tnia,
        "cob":cob,
        "addres":address,
        "dol":dol,
        "pov":pov,
        "tor":tor,
        "poaa":poaa,
        "sign":sign,
        "name":name,
        "des":des,
        "jo":jo,
        "doi":doi,
        "datalist":datalist

    }
    return data 
