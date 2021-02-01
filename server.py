from fastapi import FastAPI, Request, File, UploadFile, BackgroundTasks
from fastapi.templating import Jinja2Templates
import shutil
import ocr
import os
import uuid
import json
import re
# import module
from pdf2image import convert_from_path

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/v1/extract_text")
async def extract_text(image: UploadFile = File(...)):
    temp_file = _save_file_to_disk(image, path="temp", save_as="temp")
    print(temp_file)
    if image.filename.split('.')[-1] == 'pdf':
        # Store Pdf with convert_from_path function
        
        images = convert_from_path(temp_file)
        data='pdf'
        #text = await ocr.read_image(image[0])
    else :
        data= "image"
        #text = await ocr.read_image(temp_file)
    #data   = genrateData(text)
    return {"filename": image.filename, "text": data}

@app.post("/api/v1/bulk_extract_text")
async def bulk_extract_text(request: Request, bg_task: BackgroundTasks):
    images = await request.form()
    folder_name = str(uuid.uuid4())
    os.mkdir(folder_name)

    for image in images.values():
        temp_file = _save_file_to_disk(image, path=folder_name, save_as=image.filename)

    bg_task.add_task(ocr.read_images_from_dir, folder_name, write_to_file=True)
    return {"task_id": folder_name, "num_files": len(images)}

@app.get("/api/v1/bulk_output/{task_id}")
async def bulk_output(task_id):
    text_map = {}
    for file_ in os.listdir(task_id):
        if file_.endswith("txt"):
            text_map[file_] = open(os.path.join(task_id, file_)).read()
            text_map = genrateData(text_map)
    return {"task_id": task_id, "output": text_map}

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
