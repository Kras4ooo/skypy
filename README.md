# skypy

SkyPy is a desktop application which is an online chat between users. It mimics the functionality to Skype but special is that it is OpenSource and each can complement its functionality and use it free.

# Requirements
You must have installed PyQT5. Otherwise it will not be able to run the application. Libraries which are used PyQT5, mysqlclient==1.3.6, and pycrypto==2.6.1. Pycrypto is included in the setup.py file. You must have a version of python >=3.4.

Before you start the application you need to make a table with the following fields:
* id	
* first_name	
* username	
* password	
* public_key
* created

In the following file: skypy->codebase->server->db->db_connection.py You will find the settings you need to set your database.

# How to start App
First run servermain.pi file then run clientmain.py that is all.

