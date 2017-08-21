from flask import Flask,request,make_response, render_template
from cloudant.client import Cloudant
from cloudant.error import CloudantException
from cloudant.result import Result, ResultByKey
import time
import os
import hashlib
import pyDes




#establishing connection
USERNAME="cloudant username"
PASSWORD="cloudant password"
URL="cloudant url"
client=Cloudant(USERNAME,PASSWORD,url=URL)
client.connect()




#connecting to database
my_database = client['mydatabase']
if my_database.exists():
   print 'Connected'



app=Flask(__name__)


@app.route('/')
def index():
    return app.send_static_file('index.html')



@app.route('/upload',methods=['POST','GET'])
def upload():

    version =1
    file = request.files['file']

    file_name = file.filename
    file_content=file.read()
    #encrypt_filename = "Encrypted_" + file_name



    for document in my_database:
        if document['file_name']== file_name:
            if document['content']==file_content:
                return 'File already exists'
            else:
                version+=1


    ##uploading
    data = {'_id': file_name, 'file_name': file_name, 'version_no': version, 'content': file_content, 'last_mod':time.ctime(os.path.getmtime(file.filename))}

    doc = my_database.create_document(data)
    return 'Your have uploaded the file - {0} successfully!'.format(file_name)




@app.route('/download',methods=['GET'])
def download():
    fname = request.args.get('filename')
    filename= os.path.splitext(fname)[0]
    file_ext= os.path.splitext(fname)[1]
    print filename
    print file_ext

    document=my_database[fname]
    newfilename = filename+ '_' + str(document['version_no'])+file_ext
    downloadfile = open(newfilename, 'w')
    downloadfile.write(document['content'])
    downloadfile.close()
    return 'You have downloaded the file - {0} successfully!'.format(fname)


@app.route('/list')
def list():
    list = ''
    for document in my_database:
        new=document['file_name']+ '_' + str(document['version_no'])
        #list.append((new,document['last_mod']))
        list += new + '--------------'+document['last_mod']+'<br>'
    return list


@app.route('/delete')
def delete():
    #filename is used as an id too
    id = request.args.get('filename')
    document = my_database[id]
    document.delete()
    return 'File Delete Successful'


if __name__ == '__main__':
    #port = int(os.environ.get('PORT',5000))
    app.run(port=5000,debug=True)