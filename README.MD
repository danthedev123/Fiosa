# Fiosa
## Fully Integrated Operating System Assistant

### 👋 Hello there! I see you have come across this old project of mine. I am no longer as interested in AI as I used to be, and I'm looking for someone to take over the project. Open an issue at the new repo (https://github.com/CoffeeAssistant/Assistant) if interested. Thanks!

Fiosa is an AI chatbot built on top of ChatGPT's API. It has full integration into your Ubuntu or MacOS system, and has access to the terminal and can control your computer to help you do tasks if you are lazy or don't know how to do them yourself.
*NOTE: I am not responsible for any damage caused to a computer using Fiosa, it has occasional hallucinations and sometimes runs random commands*

Fiosa is written in Python, and it uses a technique called Prompt Injection to have a memory of the conversation, and also to give it rules and directives for providing a good experience.

## Installation
### MacOS Quickstart
Download the .app file from the releases tab in GitHub, then move it to the applications folder or run it directly. Fisoa will store its files in <YOUR_HOME_DIR>/Fiosa.

### Linux
Download the source code and run fiosa.py (python3 fiosa.py) after installing all the required modules.

## Project roadmap

- [x] Basic chat functionality
- [x] Ability to remember past messages in the conversation
- [x] System prompt finished
- [x] Ability to run commands
- [x] Tackle hallucinations via refinements to system prompt
- [ ] Revamp UI
- [ ] System tray icon (in the background)
- [ ] Port/test on other Linux distributions
- [ ] Voice-to-text and text-to-speech (kind of like Siri or Alexa)
- [ ] Ability to know what is currently running/onscreen to better know how to assist user
- [x] Consider porting to Darwin/OSX (Ported!)
- [ ] Heck, even port it to *Windows*?
