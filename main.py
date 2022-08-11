import os
import json
import random
import shutil
from fastapi import FastAPI, HTTPException, UploadFile, Request
from fastapi.responses import JSONResponse
from typing import  Union
from pyquery import PyQuery
from pydantic import BaseModel
from uuid import uuid4 # Universally Unique Identifier
import re
# PyDantic BaseModel Class
class Item(BaseModel):
    name: str
    type_contacts: Union[str, None] = None # Optional value (See in FastAPI/docs)
    price: float
    company: Union[str, None] = None # Optional value (See in FastAPI/docs)

# Exception Class
class MyException(Exception):
    def __init__(self, name: str):
        self.name = name





cpu_link = 'https://benchmarks.ul.com/compare/best-cpus'

# Get all information from link (html)
doc = PyQuery(url=cpu_link,encoding="UTF-8")

# Get information under <tr>
cpu_ = doc.find('tbody').children()

# Find out all text value in class 'infocard-cell-data' and split as a list
cpu_index = cpu_.find('.order-cell').text().split(' ')
#print(cpu_index)
# Find out all text value in class 'ent-name' and split as a list

cpu_name = cpu_.find('.OneLinkNoTx').text()
cpu_name  = re.split('AMD | Intel',cpu_name )
cpu_score = cpu_.find('.bar-score').text().split(' ')
#print(cpu_name)
# Create a dictionary with keys and values
my_cpudex = dict(zip(cpu_index, cpu_name))

app = FastAPI() # FastAPI Module

# Local data initialize
my_items = []
my_file = 'item.json'
my_file_names = []
# Load local json file if exist
if os.path.exists(my_file):
    with open(my_file, "r") as f:
        my_items = json.load(f)

# GET Method Exercise (Basic)
@app.get('/')
def root():
    return {"message": "Processors August 2022 Top 199"}

# GET Method Exercise
@app.get('/random-cpu')
def random_cpu():
    return random.choice(list(my_cpudex.items()))

'''
    ---> Try to Change this API below into path parameter API ! <---
    Where is their difference ? You can see page 17 in powerpoint !
'''
# GET Method Exercise (Interact with local database), query parameter
@app.get('/get-cpu/{cpu_rank}')
def get_cpu(cpu_rank: int = 1):
    if cpu_rank > len(my_cpudex):
        '''
            ---> Try to Change this HTTPException below into your own Exception ! <---
            You can use any status_code between 400 to 499 as client error
        '''
        raise HTTPException(404, f"CPU ID {cpu_rank} is not in your cpudex")
    else:
        # Turn integer value to string and leading zero as len == 3
        cpu_rank = str(cpu_rank)
        # Find out if CPU_rank is in database
        if cpu_rank in my_cpudex:
            return {f"CPU ID = {cpu_rank}":f"CPU Name = {my_cpudex[cpu_rank]}"}
        else:
            raise HTTPException(404, f"CPU ID {cpu_rank} is not in your cpudex")

# GET Method Exercise
@app.get('/show-cpu')
def show_cpu():
    return {'This is my cpudex' : my_cpudex}

@app.get('/delete_list')
def delete_cpulist():
    my_items.clear()
    return {'delete my_items' }

# Exception Handler
@app.exception_handler(MyException)
def call_exception_handler(request:Request, exc: MyException):
    return JSONResponse (
        status_code= 420,
        content= {
            'Message' : f'Oops ! {exc.name} not in list.try again.'
        }
    )

# POST Method Exercise
@app.post('/add-item', response_model=Item)
def create_item(item: Item):
    item_dict = item.dict()
    # Generate an UUID with HEX code
    item_rank = uuid4().hex
    item_dict.update({"id":item_rank})
    my_items.append(item_dict)
    # Save a new item into local database (JSON file)
    with open(my_file, "w") as f:
        json.dump(my_items, f, indent=4)
    return item_dict

# GET/POST Method Result
@app.get('/show-items')
def show_item():
    if len(my_items):
        return {'Items':my_items}
    else:
        # Create a exception message
        raise HTTPException(404, 'Item not found')

# POST Method Exercise (Upload File & Save to local)
@app.post('/upload')
def Upload_file(file: Union[UploadFile, None] = None):
    if not file: return {"message" : "No file upload"}
    try:
        file_location = './' + file.filename
        with open(file_location, "wb") as f:
            shutil.copyfileobj(file.file, f)
            file.close()
        my_file_names.append(file.filename)
        return {"Result" : "OK"}
    except:
        raise MyException(name=f'Upload File {file.filename}')
