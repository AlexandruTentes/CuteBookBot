The program asks for 2 inputs: 
	- chapter (int) - position
	- section (int) - position

# DO NOT TURN OFF THE PROGRAM IT WILL FIX ITSELF SOMEWHAT AT RUNTIME...
# DO NOT TURN OFF THE PROGRAM IT WILL FIX ITSELF SOMEWHAT AT RUNTIME...
# DO NOT TURN OFF THE PROGRAM IT WILL FIX ITSELF SOMEWHAT AT RUNTIME... 

The program has the option to run all. Simply type 'all' when asked to 
input the chapter and 'all' again when asked to input the section.

FEATURES:

- the program strongly aims to 'keep going' by handling errors and recovering from them
- can run without the need of a GUI (check LOGIN.txt)
- simply double type 'all' in the inputs and let the bot do the magic
- do not forget to add your login details and configs (check LOGIN.txt)

ISSUES:

- the program behaves weirdly when it encounters LAB only sections in each chapter

- sometimes some activities do not get completed at all (no idea why)
- big problems with the 'short answers' activities (the text that the bot
	gets from "Show answer" is sometimes wrong)


DEPENDENCIES:

- selenium==3.141.0
- urllib3>=1.26.5

EXECUTABLES:

- chromedriver v102.0.5005.61 (this is for my machine only, you need to get the version for yours)
	https://chromedriver.chromium.org/downloads
- geckodriver (no idea here... i got it from the source: https://github.com/Djaenk/zyBooks-Activity-Completer)


# pyton version: 3.9.2

(simply run 'pip install {item}` to get each dependency Eg: `pip install selenium==3.141.0`)



If there is any issue do not be scared to fix it yourself :D. I only ask to 
create GitHub issues as well as forks for any changes/fixes.

P.S.: find this line of code: `options.binary_location=r'C:\Program Files\Google\Chrome\Application\chrome.exe'` 
	and change the path to your machine's browser location (once again I was too lazy to add that to the LOGIN.txt :D)


