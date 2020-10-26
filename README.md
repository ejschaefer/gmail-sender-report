Gmail Message Reporter
======================
This project is used to retrieve message metadata from a Gmail inbox and report the total message per sender address.


Getting Started
---------------
This script uses OAuth 2.0 authorization to access the Gmail's API and your mailbox. You must enable the Gmail API and create OAuth 2.0 client credentials before the script can request access to your mailbox.


Enable Gmail API
----------------

1. From the [Google API Console](https://console.developers.google.com/), create a new project for your app
1. Click **Enable APIs and Services** 
1. Find and Click **Gmail API**
1. Click **Enable** to activate the Gmail API for this project

Create Gmail API Credentials
----------------------------
1. From the [Google API Console](https://console.developers.google.com/), click **Credentials**
1. Click **Create Credentials** and select **OAuth client ID**
1. Select **Desktop App** and enter a descriptive name into the **Name** field
1. Click **Create**
1. Click **OK** to close the window
1. In the **OAuth 2.0 Client IDs** section, click the download icon (down arrow) next to the new credentials.
1. Save the json file as **credentials.json** in the application's source directory


Gmail API Quotas
----------------
The Gmail APIs include default query quotas:

| Quota Name | Limit   |
| ---------- | ------- |
| Queries per day | 1,000,000,000 |
| Queries per minute per user | 15,000 |
| Queries per minute | 1,200,000 |
	


Quick Install
------------- 
```shell
$ virtualenv .env
$ source .env/bin/activate
$ pip install -r requirements.txt
```

Usage
-----
```shell
# create the initial database
# seed the database with messages from the API
# retrieve sender addresses for each message
# create a report of total messages per sender
$ python report.py --seed

# Retrieve sender addresses for messages stored in the database
# create a report of total messages per sender
$ python report.py

# Only create a report of total messages per sender
$ python report.py --report-only
$ open report-output.html
```


References
-----------
- [The Gmail API: modern, fast, RESTful](https://developers.google.com/gmail/api/?hl=en_US)
- [Authorizing Your App with Gmail](https://developers.google.com/gmail/api/auth/about-auth?hl=en_US)
- [Gmail API Usage Quotas](https://developers.google.com/gmail/api/reference/quota)
- [Google Core API Client library](https://googleapis.github.io/google-api-python-client/docs/epy/index.html)
- [Gmail API Client library](https://googleapis.github.io/google-api-python-client/docs/dyn/gmail_v1.html)