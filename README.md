# TRT-Finance-Platform
A commissioned project for my ex-tuition teacher, built with gratitude for his dedication to his students.

![HomePage](./public/images/f1.png)
![ManageStudents](./public/images/f2.png)
![ManageClasses](./public/images/f3.png)

## Problem
My ex-tuition teacher had to regularly chase after parents who had not paid their tuition fees. 
Often, even when payment is made, he would have to download his bank statements and manually cross-reference the payments with his list of students, sometimes without names, invoice numbers nor parents' names.

Invoice has to also be manually generated and emailed to the parents each term,

This was a time-consuming and frustrating process, and he wanted a way to automate it.


## How to use (with docker)
1. Install docker
1. Clone this repository
1. cd into the repository with command prompt
1. Build the docker image
```
docker build -t trt-finance .
```
1. Run the docker image
```
docker run -p 8051:8051 trt-finance
```
1. Open your browser and go to `http://localhost:8051/`
1. Enjoy!

## Shutting down
1. Go to command line and type `docker ps`
1. Find the container id or name of the trt-finance container
1. Type `docker stop <container_id or name>`


## "User stories"
1. Mr Wong adds students and their details, like the class that they belong in. 
1. Mr Wong can add students to his class. Qn: Can a student be in multiple classes? Assume no. 

Managing student details
1. Set parents by id, but select the parent by name. OR just select an existing parent.

## Tech Stack
Oracle SQL: Oracle Instant Client


## Dev notes

# Install LaTeX (MacTeX)
brew install --cask mactex-no-gui

# Install Python packages
pip install codecs subprocess

todo: see total sum to be collected for this term.



Database Schema
![DBSchema](./public/images/DbSchema.png)


Use of session state:
authenticator
pulled_data is a dict, with keys being 'most_recent_term'


When installing Oracle, put instantclient in /config folder. Then `export DYLD_LIBRARY_PATH=/Users/ethanyuxin/Documents/World/TRT-Finance-Platform/config/instantclient_23_3:$DYLD_LIBRARY_PATH`


Term naming convention: 'Y24T3' for Year 2024, Term 3

# Problems
- [ ] How to handle deletion of a particular class in db, but there are still students in that class? Soln: Set the class_id in the student table to NULL?


## Testing
Commands to run to test
```
    export PYTHONPATH=$(pwd)
    pytest test/test_manage_term_and_class.py
```


## Continuation:
Invoice Generation page flow:
> Add students to term
> Show exisiting students in term
> Generate invoice for term
> Email invoice to parents

Check Payments page flow:
> Allow user to upload bank statement if want. 
> Show all students in term, paid and unpaid
> show all unpaid students
> can click send reminder email to all unpaid students


What if students join after start of term? not 12 classes for him. > Right now manually refunding. 
