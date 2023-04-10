# Solved : List/Pull/Get all google reviews through the google my business api using python. (2023)
Get google reviews using Google My Business API for all accounts and locations

Install all the required libraries.
This code will result in json files for all locations and then combines all the files to create a single csv file. If you do not want this its fairly simple to edit the code.

Things to note:
Also, since the code will not find any json files previously stored on your system, so the first time it runs, it might error in producing a combined file, so try to re-run and it will solve the problem.

Errors:
 "Access denied". 
 Just add the gmail account to the Test users in the OAuth Consent Screen.

Before dismissing the error, check the details of the error. If the error consists of domain error then set port = (a 5 digit number) and register that in the authorized domains section in the Oauth Screen.
