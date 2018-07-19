#Udacity Catalog Webserver Project

This project was written using specifications from Udacity's full stack developer course. This webserver application uses the Flask framework to store information in a database, and to serve that information to a webpage.

This application uses Google's Sign In API to authenticate and authorize user sessions. Bootstrap is used for styling of the web application.

##Getting Started

To get started with the webserver project, follow these instructions: 
1. Download and install a vagrant machine from [VagrantUp](https://www.vagrantup.com/). 
2. Fork the project from this Git Hub repository and save inside the vagrant directory on your virtual machine.
3. Run vagrant up to set up the machine.
4. Run vagrant ssh to log into the machine.
5. Navigate into the vagrant directory.
6. Run dbsetup.py to set up the databse.
7. Run populateshopping.py to populate the database with initial values.
8. Run application.py to start the webserver.
9. Navigate to http://localhost:8000 to view the application.
