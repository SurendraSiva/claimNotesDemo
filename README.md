This Project is a Django Application which has a RAG model as it's Primary component. The user interface of this project consists of
1. Model selection 
2. Document Upload ( pdf format )
3. Questions Upload ( excel sheet format, note: the sheet name should be 'Django_sheet')

After downloading the folder, create a virtual environment and activate it, once the virtual environment is activated, execute the command given below to insall all the required libraries.
pip install -r requirements.txt

Once all the necessary libraies are installed, move to the cliamnotes directory and run:
python manage.py makemigrations

python manage.py migrate

Once the migration is done, run the application using:
python manage.py runserver

