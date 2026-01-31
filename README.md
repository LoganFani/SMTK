
![simmy](media/simmy.png)


# SMTK (Sentence Mining Tool Kit)

**Pre-Release** </br>
A tool for users to easily translate and mine sentences from transcripts for language learning.

## Description

The goal for SMTK (Sentence Mining Tool Kit) is to allow users to easily translate large forms of text and transcripts. By keeping the entire process on the user's hardware, SMTK removes the barriers of cost and complexity usually associated with bulk translation.

## Features

- Integration with Anki
- Local Translation Models
- Local storage of "cards / translations"

## Getting Started

## Dependencies

### Installing Locally
* Python 3.12

### Installing with Docker (**BROKEN**)
* Docker

## Installing

### Installing Locally

After Python 3.12 is installed navigate to the SMTK folder.
```
cd SMTK
```

It is highly recommended to create an environment file using whichever one you prefer (venv for this example)

```
python3 -m venv env
```

Next install all of the dependencies in the requirements.txt file with pip

```
pip install -r requirements.txt
```

Finally run the build.py file to start the system tray application.
```
python build.py
```

Expected Output
```
INFO:     Started server process [24912]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

### Installing with Docker
After Docker is installed navigate to the SMTK folder.
```
cd SMTK
```

Build and run the container

```
docker-compose up --build 
```

* Note *
You will still have to navigate to 127.0.0.1:8000 in browser.


## Currently Working on
- Fixing bugs / errors.
- Packaging as an application.

## Future Goals
- [ ] More language models.
- [ ] Better card customization for Anki.
- [ ] Direct integration with Youtube Videos.
- [ ] More formatting feautres / ease of use.
- [ ] Pulling transcripts from video links.

## Authors

Contributors names and contact info

Logan Fani  
Email: [logancfani@gmail.com](logancfani@gmail.com)

## Version History

* 0.1
    * Initial Pre-Release and testing phase.

## License

This project is licensed under the MIT License - see the LICENSE file for details
