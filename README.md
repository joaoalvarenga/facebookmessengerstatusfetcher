# Facebook Messenger Status Fetcher  
![built with](https://img.shields.io/badge/Built%20with-Python%203-green.svg)
This fetcher monitoring people "online status" on Facebook, I've build this to collect some data about people's behavior in Facebook, that could be used to predict what a specific person are doing or where are this person.  

## Getting Started

### Dependencies  
You'll need to install a MongoDB server if you don't have it.  
To install dependencies just run:
```
$ python3 -m pip install -r requirements.txt
```
The last thing you need is PhantomJS, that you can install using npm. (Don't install using package manager(pacman, apt, yum etc))  
```
$ npm install -g phantomjs-prebuilt
```

### Running
Now you need to define which users you'll watch, you need to create a file with all facebook ids splitted by lines.
Example:
fids.txt
```
dude01
girl95
george.orwell.1984
```

Now just run
```
$ python3 fetcher.py
    --id File containing Facebook profiles ids

    --email Facebook login email
    
    --password Facebook login password
```
Example
```
$ python3 fetcher.py --id fids.txt --email bigbrother@minlove.com --password ilovethebigbrother
```
# License
MIT License

# Contributing

:+1::tada: Thank you, you've scrolled down here :tada::+1:

Steps to contribute:

- Make your awesome changes focusing on increasing information detail level
- Submit pull request