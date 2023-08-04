Before getting started with the projects you need to go through the following steps:
## 1. Enable the Gmail API
In the Google Cloud console, enable the Gmail API. [Enable the API](https://console.cloud.google.com/flows/enableapi?apiid=gmail.googleapis.com)

## 2. Configure the OAuth consent screen
If you're using a new Google Cloud project to complete this quickstart, configure the OAuth consent screen and add yourself as a test user. If you've already completed this step for your Cloud project, skip to the next section. [Follow these steps](https://developers.google.com/gmail/api/quickstart/python#configure_the_oauth_consent_screen)

## 3. Authorize credentials for a desktop application

[Follow these setps](https://developers.google.com/gmail/api/quickstart/python#authorize_credentials_for_a_desktop_application) to generate credentails.

## 4 Download the credentials file
Download the credentials file from Step 3 and save it in the same directory as the project as credentials.json

## 5. Setup environment
```py -m venv env```

Activate the environment:

For Windows:
```.\env\Scripts\activate```

For Linux:
```source env/bin/activate```

## 6. Install required packages
```pip install -r requirements.txt```

## 7. Run the project
```py main.py```

Also, You can play with the rules in rule.json file to get the desired output.


### Enjoy!!!
