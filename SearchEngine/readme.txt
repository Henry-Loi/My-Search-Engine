Instructions to build project programs:

General:
All of the programs are written and run in Python version 3.9.13
Database package: sqlite3
Web Framework: Django

** please make sure you are in the "SearchEngine" folder before running the program below
Run the follow command to SearchEngine directory: cd ./SearchEngine 

Spider & Indexer program (program for Database Setup):
1. Run the following commands in terminal: 
    python manage.py migrate --fake webInterface 0005_topkeywords
    python manage.py migrate webInterface 0006_auto_20240510_1550
2. Wait for around 3.5 minutes
2. A output database file named "db.sqlite3" should be created/updated

Search Engine & Web webInterface program:
1. Run the following commands in terminal: 
    python manage.py runserver
2. The development server will be started at local host like "http://127.0.0.1:8000/". 
3. Ctrl+CLick the hyperlink to access the website
4. A Search Engine Website should be shown.  

Testing program:
1. Run the following commands in terminal: 
    python manage.py test
2. Wait for around 3.5 minutes
3. Test Result will be shown in terminal.
