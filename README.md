# CS50-Final-Project
SAH (Search analyzer and helper)


### Video Demo:  <[Flask web application - CS50 Final Project](https://youtu.be/Dvcl5UgBkaY)>
### Description:
#### Flask web app for scraping prices from websites and analyzing them.
This web app, named SAH (Search analyzer and helper), implements the Flask web framework with the Python library Beautiful Soup to get data from websites and save them in an SQL database. Registering, logging in and out is implemented, and search history is accessible if a user is logged in.

### Project files:
1. app.py is main file where all flask web framework functionality is implemented.
2. pull_data.py contains function used for data mining
3. SAH.db is SQL database with three tables:
    - users - contains user id, username, and hashed password.
    - history - contains search id, user id, search keyword, and timestamp.
    - search - contains search id, item, and price.
