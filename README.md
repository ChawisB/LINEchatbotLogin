# LINEchatbotLogin
A chatbot made to run on the LINE application.

A chatbot which does not rely on web login but done through LINE's own flex messages. This project aims to show database incorporation into a program as well as other features related to the chatbot. This chatbot possesses a rich menu as well as a quick reply menu upon successfully logging in. Note: Rich menu has a delay before it appears and disappears.

Limitations/issues:
As this is a program showcasing database usage, the login database already has a set of users created and due to there being no sign up function yet, you cannot login without using these premade users.
The chatbot currently has no further function beyond logging in as of current.

File differences:
receiveLine is the latest and primary file.
receiveLine_auto_login is one of the previous versions made with csv and pandas for a database system.
receiveLine_auto_login_mongo is the same as above but replaced pandas for mongodb as a database system.
