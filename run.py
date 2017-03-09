#! flask/bin/python

from app import app  # when this is being imported, the app is being setup due to __init__.py

app.run(debug=True)
