# Geeting Started
```
NOTE:- If Anything Is Not Working Make Sure there is Python 3.7.7 version installed
```
### All the required packages are given in requirements.txt file to install all do
```
cd advisornetwork
pip install -r requirements.txt
```

### After installing all things make Sure To migrate the 'api' app first
```
 python manage.py makemigrations api
```
### then
```
python manage.py migrate api
```
### then migrate the project
```
python manage.py makemigrations 
```
### then
```
python manage.py migrate 
```
### then runserver using
```
python manage.py runserver
```

## Note:-  For testing import the thunderclient collections file into thunderclient extension in vscode and make sure all API need JWT authentication except register & login 
