from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import os
import sys
import time
import random


# This code in short: workarounds... workarounds everywhere! :D


# Enter your zybooks login below with the course code
options = Options()
options.headless = False
email = ""     # "ExampleEmail@gmail.com"
password = ""
course = ""    # "ExampleCourseCode"
skip_completed = True   
loops = 3       # How many times to attempt to complete the current section in case of an error (lag and browser used can affect this) 
all_chapters = False # check to detect if we run all chapters or not


#Probably the ONLY piece of code that s decent looking... but it s quite bad in terms of extendability
def config_parser():
    global options
    global email
    global password
    global course
    
    try:
        f = open("LOGIN.txt", "r")
    except:
        print("ERROR: Could not find LOGIN.txt")
        os._exit(0)

    lines = f.read().split("\n")

    for line in lines:
        if (len(line) != 0 and line[0] == '#') or len(line) == 0:
            continue

        line = line.split('#')[0] #remove comments
        line = line.split(':')

        if len(line) != 2:
            continue

        key = line[0].strip().replace('\t', '')
        value = line[1].strip().replace('\t', '')
        
        if key == "email":
            email = value
        elif key == "password":
            password = value
        elif key == "course":
            course = value
        elif key == "headless":
            if value == "on":
                options.headless = True
            else:
                options.headless = False
        else:
            print("ERROR: LOGIN.txt has unknown key value ", key)
            os._exit(0)

    print("LOGIN.txt loaded successfully...")


config_parser()

#this thing is probably useful... maybe
def wait_driver(driver, string):
    try:
         WebDriverWait(driver, 10).until(expected_conditions.element_to_be_clickable((By.CSS_SELECTOR, string)))
    except Exception as e:
        print("ERROR: web driver wait")
        print(e)
        return False

    return True

def login(driver, email, password, course):
    driver.get("https://learn.zybooks.com/signin")
    while (True):
        email_input = driver.find_element(By.XPATH, "//input[@type='email']")
        password_input = driver.find_element(By.XPATH, "//input[@type='password']")
        signin_button = driver.find_element(By.CLASS_NAME, "signin-button")
        
        if not email:
            email = input("Please enter your zyBooks email: ")
        email_input.send_keys(email)
        if (email == "quit"):
            print("--Exiting--")
            driver.quit()
            os._exit(0)

        if not password:
            password = getpass.getpass("Enter your zyBooks password: ")
        password_input.send_keys(password)
        if (password == "quit"):
            print("--Exiting--")
            driver.quit()
            os._exit(0)
        
        signin_button.click()
        try:
            driver.implicitly_wait(1)
            WebDriverWait(driver, 30).until(expected_conditions.invisibility_of_element(
                (By.CSS_SELECTOR, ".zb-progress-circular.orange.med.message-present.ember-view")))
            driver.implicitly_wait(0)
        except:
            driver.quit()
            print("Timed out while authenticating login, aborting...")
            os._exit(0)
        if (driver.find_elements(By.XPATH, "//button[@disabled='']") or driver.find_elements(By.XPATH,
                "//div[contains(text(), 'Invalid email or password')]")):
            print("--Invalid email or password--\n")
            email_input.clear()
            password_input.clear()
        else:
            print("\nLogin Successful\n")
            break

def selectzyBook(driver):
    global course
    while (True):
        if not course:
            course = input("Enter your course ID or the name of your course: ")
        if (course == "quit"):
            print("--Exiting--")
            driver.quit()
            os._exit(0)
        try:
            course = course.replace(" ", "")
            zybook_selection = driver.find_element(By.XPATH,"//a[contains(@href, '" + course + "')]")
            zybook_selection.click()
            break
        except:
            print("--Invalid course--\n")
    print("zyBook Selected\n")

def chapterSelection(driver, i = 0):
    global all_chapters
    while (True):
        open_chapters = driver.find_elements(By.CSS_SELECTOR,
            "li.toc-item.chapter-item.js-draggableObject.draggable-object.expanded.ember-view")
        for open_chapter in open_chapters:
            open_chapter.find_element(By.CSS_SELECTOR,"div.chapter-info.unused").click()
        if not i:
            chapter = input("Enter the chapter number you want completed: ")
        else:
            chapter = i
        if (chapter == "quit"):
            print("--Exiting--")
            driver.quit()
            os._exit(0)
        if chapter == "all":
            chapter = 1
            all_chapters = True
            
        try:
            chapter_selection = driver.find_elements(By.XPATH, 
                "//*[contains(@class, 'table-of-contents-list')]/*[contains(@class, 'chapter-item')]")[int(chapter) - 1]
            chapter_selection.click()
            print("Chapter Selected\n")
            return chapter
        except:
            print("--Invalid chapter--\n")



######################################
######################################
######################################

#Be forgiven the one who shall attempt to understand this bit... bless your soul brave one
def sectionSelection(driver, chapter):
    global all_chapters
    while (True):
        chapter_selection = driver.find_elements(By.XPATH,
            "//*[contains(@class, 'table-of-contents-list')]/*[contains(@class, 'chapter-item')]")

        chapters = len(chapter_selection)
        chapter_selection = chapter_selection[int(chapter) - 1]

        sub_chapters = driver.find_elements(By.CLASS_NAME, "section-title")

        section_selection = input(
            "Enter the section number you want completed. Enter \"all\" if you would like the entire chapter completed: ")
        if (section_selection == "quit"):
            print("--Exiting--")
            driver.quit()
            os._exit(0)
        if (section_selection.isnumeric()):
            #"//*[contains(@class, 'section-list')]/*[contains(@class, 'section-item')]"
            #run_max = 1
            #run = 1
            #dup = [0] * 200 #used to prevent a bug where the code would re-run the same section multiple times for no reason
            
            #ignore this while... i was too lazy to redo for single section cases and i just copy-pasted from 'all' section option
            while chapter <= chapters:
                if all_chapters:
                    try:
                        chapter_selection = driver.find_elements(By.XPATH, 
                            "//*[contains(@class, 'table-of-contents-list')]/*[contains(@class, 'chapter-item')]")[int(chapter) - 1]
                        chapter_selection.click()
                        chapter = chapter + 1
                        print("Chapter Selected\n")
                    except:
                        print("--Invalid chapter--\n")

                run_max = 1
                run = 1
                dup = [0] * 200
                
                while run <= run_max:
                    print(run, run_max)
                    try:                    
                        try:
                            selectzyBook(driver)
                        except:
                            pass

                        try:
                            chapterSelection(driver, chapter - 1)
                        except:
                            pass

                        dup[int(section_selection)] = dup[int(section_selection)] + 1

                        if dup[int(section_selection)] >= 5:
                            run = run + 1
                            section_selection = run
                            
                            continue
                        
                        section_button = driver.find_elements(By.CLASS_NAME, "section-title")#chapter_selection.find_elements(By.XPATH, "//li[@class='section-list']")
                        print(int(section_selection))
                        section_button = section_button[int(section_selection) - 1]#.find_elements(By.XPATH, "//span[@class='section-title']")
                        section_button.click()
                        print("\nStarting chapter " + str(chapter) + " section " + str(section_selection) + "...")
                        try:
                            WebDriverWait(driver, 10).until(expected_conditions.element_to_be_clickable(
                                (By.CSS_SELECTOR, ".zybook-section.zb-card.ember-view")))
                            WebDriverWait(driver, 10).until(expected_conditions.presence_of_element_located((By.CLASS_NAME, 'zybook-section-title')))
                        except Exception as e:
                            print(
                                "Timed out while loading chapter " + chapter + " section " + section_selection + " content, aborting...")
                            print(e)
                            driver.quit()
                            os._exit(0)
                        #driver.refresh()

                        #try:
                            #WebDriverWait(driver, 5).until(expected_conditions.element_to_be_clickable(
                             #   (By.CSS_SELECTOR, ".md-action-button.enter-execution")))
                        #except:
                        #    pass
                        completeParticipationActivities(driver)
                        try:
                            driver.find_element(By.XPATH,"/html/body/div[4]/header/div[1]/div/ul/a[2]").click()
                        except NoSuchElementException:
                            driver.find_element(By.XPATH,"/html/body/div[3]/header/div[1]/div/ul/a[2]").click()
                        #break

                        run = run + 1
                        #section_selection = run
                    except Exception as e:
                        print("ERROR: while run <= run_max: inside sectionSelection")
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                        print(exc_type, fname, exc_tb.tb_lineno)
                        print(e)
                if not all_chapters:
                    break

        #do you know that Jackie Chan meme with the confused face?
        elif (section_selection == "all"):
            while chapter <= chapters:
                if all_chapters:
                    try:
                        chapter_selection = driver.find_elements(By.XPATH, 
                            "//*[contains(@class, 'table-of-contents-list')]/*[contains(@class, 'chapter-item')]")[int(chapter) - 1]
                        chapter_selection.click()
                        chapter = chapter + 1
                        print("Chapter Selected\n")
                    except:
                        print("--Invalid chapter--\n")
            
                run_max = len(driver.find_elements(By.CLASS_NAME, "section-title"))
                run = 1
                section_selection = run
                dup = [0] * 200

                while run <= run_max:
                    print(run, run_max)
                    try:                    
                        try:
                            selectzyBook(driver)
                        except:
                            pass

                        try:
                            chapterSelection(driver, chapter - 1)
                        except:
                            pass

                        dup[int(section_selection)] = dup[int(section_selection)] + 1

                        if dup[int(section_selection)] >= 5:
                            run = run + 1
                            section_selection = run
                            
                            continue
                        
                        section_button = driver.find_elements(By.CLASS_NAME, "section-title")#chapter_selection.find_elements(By.XPATH, "//li[@class='section-list']")
                        print(int(section_selection))
                        section_button = section_button[int(section_selection) - 1]#.find_elements(By.XPATH, "//span[@class='section-title']")
                        section_button.click()
                        print("\nStarting chapter " + str(chapter- 1) + " section " + str(section_selection) + "...")
                        try:
                            WebDriverWait(driver, 10).until(expected_conditions.element_to_be_clickable(
                                (By.CSS_SELECTOR, ".zybook-section.zb-card.ember-view")))
                            WebDriverWait(driver, 10).until(expected_conditions.presence_of_element_located((By.CLASS_NAME, 'zybook-section-title')))
                        except Exception as e:
                            print(
                                "Timed out while loading chapter " + chapter + " section " + section_selection + " content, aborting...")
                            print(e)
                            driver.quit()
                            os._exit(0)
                        #driver.refresh()

                        #try:
                            #WebDriverWait(driver, 5).until(expected_conditions.element_to_be_clickable(
                             #   (By.CSS_SELECTOR, ".md-action-button.enter-execution")))
                        #except:
                        #    pass
                        completeParticipationActivities(driver)
                        try:
                            driver.find_element(By.XPATH,"/html/body/div[4]/header/div[1]/div/ul/a[2]").click()
                        except NoSuchElementException:
                            driver.find_element(By.XPATH,"/html/body/div[3]/header/div[1]/div/ul/a[2]").click()
                        #break

                        run = run + 1
                        section_selection = run
                    except IndexError:
                        break 
                    except Exception as e:
                        print("ERROR: while run <= run_max: inside sectionSelection")
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                        print(exc_type, fname, exc_tb.tb_lineno)
                        print(e)
                if not all_chapters:
                    break
        else:
            print("Please enter a valid section number.")

######################################

#the weird 'i' variable in here is meant to come together with the global 'loops' to prevent re running the same section too many times on errors
def completeParticipationActivities(driver, i = 0):
    if int(i) >= int(loops):
        return
    print(i)
    try:
        print("Animation")
        playAnimations(driver)
        print("Custom Interactions")
        completeCustomInteractions(driver)
        print("New Custom Interactions")
        completeNewCustomInteractions(driver)
        print("Multiple Choice")
        completeMultipleChoice(driver)
        print("Short Answer")
        completeShortAnswer(driver)
        print("Matching")
        completeMatching(driver)
        #print("Selection Problems")
        #completeSelectionProblems(driver) #this guy here... i got too lazy to also fix this function... and to be honest i got no idea what section this is too :D
        

    except:
        i = i + 1
        completeParticipationActivities(driver, i)

    i = i + 1
    completeParticipationActivities(driver, i)

def checkCompleted(activity):
    global skip_completed
    if skip_completed:
        try:
            activity.find_element(By.CSS_SELECTOR,
                "div.zb-chevron.check.title-bar-chevron.orange.filled.large")
            return True
        except NoSuchElementException:
            return False
    return False

#i got genuinely no idea how this function works... and imagine i somehow even fixed it from the initial clone... WHAT
def playAnimations(driver):
    animation_players = driver.find_elements(By.CSS_SELECTOR,
        "div.interactive-activity-container.animation-player-content-resource.participation.large.ember-view")
    animation_players += driver.find_elements(By.CSS_SELECTOR,
        "div.interactive-activity-container.animation-player-content-resource.participation.medium.ember-view")
    animation_players += driver.find_elements(By.CSS_SELECTOR,
        "div.interactive-activity-container.animation-player-content-resource.participation.small.ember-view")

    for animation in animation_players:
        if checkCompleted(animation):
            print("Skipping completed animation activity")
            continue
        # crumbs = driver.find_element_by_css_selector("li.bread-crumb")
        start = driver.find_element(By.CSS_SELECTOR, "div.section-header-row")
        driver.execute_script("arguments[0].click();",
                              start)  # Switched to JavaScript clicking for this
                                        #because of above crumbs that seemingly can't be hidden or clicked around.
        double_speed = animation.find_element(By.CSS_SELECTOR, "div.speed-control")
        double_speed.click()
        start_button = animation.find_element(By.CSS_SELECTOR,"button.zb-button.primary.raised.start-button.start-graphic")
        start_button.click()
        while (True):
            if (animation.find_elements_by_xpath(".//div[@class='pause-button']")):
                continue
            try:
                play_button = animation.find_element(By.CSS_SELECTOR,"div.play-button.bounce")
                play_button.click()
            except:
                pass
            if (animation.find_elements(By.CSS_SELECTOR,"div.play-button.rotate-180")):
                break
        print("Completed animation activity")

#once again.. this bit probably does something.. never checked
def completeCustomInteractions(driver):
    custom_activties = driver.find_elements(By.XPATH,
        "//div[@class='interactive-activity-container custom-content-resource participation large ember-view']")
    custom_activties += driver.find_elements(By.XPATH,
        "//div[@class='interactive-activity-container custom-content-resource participation medium ember-view']")
    custom_activties += driver.find_elements(By.XPATH,
        "//div[@class='interactive-activity-container custom-content-resource participation small ember-view']")
    for activity in custom_activties:
        if checkCompleted(activity):
            print("Skipping completed interactive activity")
            continue
        #driver.find_element(By.XPATH,"//div[@class='section-header-row']").click()
        #start = driver.find_element(By.CSS_SELECTOR, "div.section-header-row")
        #driver.execute_script("arguments[0].click();",
         #                     start)  # Switched to JavaScript clicking for this
                                        #because of above crumbs that seemingly can't be hidden or clicked around.
        buttons = activity.find_elements(By.XPATH,".//button[@class='button']")
        for button in buttons:
            button.click()
            time.sleep(random.uniform(0.25, 1))

#decided to make the function above but twice and fixed... still got no idea what it does :D
def completeNewCustomInteractions(driver):
    
    
    custom_activties = driver.find_elements(By.XPATH, 
        "//div[@class='interactive-activity-container custom-content-resource participation large ember-view']")
    custom_activties += driver.find_elements(By.XPATH,
        "//div[@class='interactive-activity-container custom-content-resource participation medium ember-view']")
    custom_activties += driver.find_elements(By.XPATH,
        "//div[@class='interactive-activity-container custom-content-resource participation small ember-view']")
    for activity in custom_activties:
        if checkCompleted(activity):
            print("Skipping completed new interactive activity")
            continue

        start = driver.find_element(By.CSS_SELECTOR, "div.section-header-row")
        driver.execute_script("arguments[0].click();",
                              start)  # Switched to JavaScript clicking for this
                                        #because of above crumbs that seemingly can't be hidden or clicked around.
        
        #driver.find_element(By.XPATH,"//div[@class='section-header-row']").click()
        #buttons = driver.find_element(By.CSS_SELECTOR, "button.md-action-button.enter-execution")#activity.find_elements_by_xpath("//button[@class='md-action-button enter-execution']")
        buttons = activity.find_elements(By.XPATH, "//button[@class='md-action-button enter-execution']")#activity.find_elements(By.CLASS_NAME,"enter-execution")
        #print(buttons)

        for button in buttons:
            button.click()
            time.sleep(random.uniform(0.25, 1))

        #time.sleep(5)
        start = driver.find_element(By.CSS_SELECTOR, "div.section-header-row")
        driver.execute_script("arguments[0].click();",
                              start) 

        runs = activity.find_elements(By.XPATH, "//button[@class='md-button orange run']")

        for run in runs:
            
            webdriver.ActionChains(driver).move_to_element(run).click(run).perform()
            #run.click()
            time.sleep(random.uniform(0.25, 1))
        break

#this guy works sometimes... have mercy on me I hat to struggle a bunch of hours to make this work somehow ok... just let me be ;(
def completeMultipleChoice(driver):
    multiple_choice_sets = driver.find_elements(By.XPATH,
        "//div[@class='interactive-activity-container multiple-choice-content-resource participation large ember-view']")
    multiple_choice_sets += driver.find_elements(By.XPATH,
        "//div[@class='interactive-activity-container multiple-choice-content-resource participation medium ember-view']")
    multiple_choice_sets += driver.find_elements(By.XPATH,
        "//div[@class='interactive-activity-container multiple-choice-content-resource participation small ember-view']")
    for question_set in multiple_choice_sets:
        if checkCompleted(question_set):
            print("Skipping completed multiple choice activity")
            continue

        #driver.find_element(By.XPATH,"//div[@class='section-header-row']").click()
        questions = question_set.find_elements(By.XPATH,
            ".//div[@class='question-set-question multiple-choice-question ember-view']")

        for question in questions:
            #if (question.find_elements(By.XPATH,".//div[@class='explanation has-explanation correct']")):
            #    break

            choices = question.find_elements(By.XPATH,".//label[@aria-hidden='true']")

            for choice in choices:
                try:
                    choice.click()
                except:
                    webdriver.ActionChains(driver).move_to_element(choice).click(choice).perform()
                #if (question.find_elements(By.XPATH,".//div[@class='explanation has-explanation correct']")):
                 #   break
                time.sleep(random.uniform(0.25, 1))
            time.sleep(random.uniform(0.1, 0.25))

        print("Completed multiple choice set")

#this guy gave me the most headaches.. yet i managed to get it working like last night at 3am... got no idea how but it works.
#it probably uses some magic in there.
def completeShortAnswer(driver):
    short_answer_sets = driver.find_elements(By.XPATH,
        "//div[@class='interactive-activity-container short-answer-content-resource participation large ember-view']")
    short_answer_sets += driver.find_elements(By.XPATH,
        "//div[@class='interactive-activity-container short-answer-content-resource participation medium ember-view']")
    short_answer_sets += driver.find_elements(By.XPATH,
        "//div[@class='interactive-activity-container short-answer-content-resource participation small ember-view']")
    for question_set in short_answer_sets:
        try:
            if checkCompleted(question_set):
                print("Skipping completed short answer activity")
                continue
            #driver.find_element(By.XPATH,"//div[@class='section-header-row']").click()
            #start = driver.find_element(By.CSS_SELECTOR, "div.section-header-row")
            #driver.execute_script("arguments[0].click();",
             #                     start)  # Switched to JavaScript clicking for this
                                            #because of above crumbs that seemingly can't be hidden or clicked around.
            questions = question_set.find_elements(By.XPATH,
                ".//div[@class='question-set-question short-answer-question ember-view']")

            for question in questions:
                show_answer_button = question.find_element(By.CSS_SELECTOR,
                    "button.zb-button.secondary.show-answer-button")

                #show_answer_button.click()
                #show_answer_button.click()
                webdriver.ActionChains(driver).move_to_element(show_answer_button).click(show_answer_button).perform()
                webdriver.ActionChains(driver).move_to_element(show_answer_button).click(show_answer_button).perform()

                #WebDriverWait(driver, 10).until(expected_conditions.presence_of_element_located((By.CLASS_NAME, "forfeit-answer")))

            #questions = driver.find_elements(By.XPATH,
             #   ".//div[@class='question-set-question short-answer-question ember-view']")

            driver.find_elements(By.XPATH,
                "//*[contains(@class, 'question-set-question')]/*[contains(@class, 'short-answer-question')]")

            answer = question_set.find_elements(By.CLASS_NAME,"forfeit-answer")#driver.find_elements(By.XPATH,"//span[@class='forfeit-answer']")
            
            for i, question in enumerate(questions):
                text_area = question.find_element(By.CSS_SELECTOR,
                    "textarea.ember-text-area.ember-view.zb-text-area.hide-scrollbar")

                text_area.send_keys(answer[i].text)

                check_button = question.find_element(By.CSS_SELECTOR,
                    "button.zb-button.primary.check-button")

                webdriver.ActionChains(driver).move_to_element(check_button).click(check_button).perform()

                time.sleep(random.uniform(0.25, 1))
            print("Completed short answer set")
        except:
            pass

#i did not touch this function at all and i regret nothing.. do we even have matching in the zybook?
def completeMatching(driver):
    matching_sets = driver.find_elements(By.XPATH,
        "//div[@class='interactive-activity-container custom-content-resource participation large ember-view']")
    matching_sets += driver.find_elements(By.XPATH,
        "//div[@class='interactive-activity-container custom-content-resource participation medium ember-view']")
    matching_sets += driver.find_elements(By.XPATH,
        "//div[@class='interactive-activity-container custom-content-resource participation small ember-view']")
    for matching in matching_sets:
        if checkCompleted(matching):
            print("Skipping completed matching/run activity")
            continue
        try:  # Support for 'run this code' activities, which use same class definition as matching activities. Only works for some code activities, as some require just running while others require editing the code first
            run_button = matching.find_element(By.CSS_SELECTOR,"button.run-button.zb-button.primary.raised")
            run_button.click()
            print("Attempted run activity")
            continue
        except NoSuchElementException:
            pass

        matching.click()
        rows = matching.find_elements(By.CSS_SELECTOR,"definition-row")

        class row_is_correct(object):
            def __init__(self, row):
                self.row = row

            def __call__(self, driver):
                if self.row.text.endswith("Correct"):
                    return True
                else:
                    return False

        for row in rows:
            row_correct = False
            while not row_correct:
                choice = matching.find_element(By.XPATH,"draggable-object")
                bucket = row.find_element(By.CLASS_NAME,"term-bucket")
                driver.execute_script(drag_and_drop_js, choice, bucket)
                try:
                    WebDriverWait(row, .75).until(row_is_correct(row))  # Lowering delay causes issues
                    row_correct = True
                except TimeoutException:
                    pass
        print("Completed matching set")


def completeSelectionProblems(driver):
    
    
    selection_problem_sets = driver.find_elements(By.XPATH,
        "//div[@class='interactive-activity-container detect-answer-content-resource participation large ember-view']")
    selection_problem_sets += driver.find_elements(By.XPATH,
        "//div[@class='interactive-activity-container detect-answer-content-resource participation medium ember-view']")
    selection_problem_sets += driver.find_elements(By.XPATH,
        "//div[@class='interactive-activity-container detect-answer-content-resource participation small ember-view']")
    for question_set in selection_problem_sets:
        if checkCompleted(question_set):
            print("Skipping completed selection activity")
            continue
        #driver.find_element_by_xpath("//div[@class='section-header-row']").click()
        questions = question_set.find_elements(By.XPATH,
            ".//div[@class='question-set-question detect-answer-question ember-view']")
        for question in questions:
            choices = question.find_elements(By.XPATH,".//div[@class='unclicked']")
            for choice in choices:
                choice.click()
                if (question.find_elements(By.XPATH,".//div[@class='explanation has-explanation correct']")):
                    break
        print("Completed selection problem set")

#ignore this function.. i m probably doing something wrong :))))))))))
#also .. this is for that one person who just has to read through this madness:
        #come on... go ahead
        #enjoy the copy-pasted code in there
        #it s definitely not the exact code 3-4 times.. no no
        #really now why do you even bother at this point
        #ok i ll let you in in a secret... this function.. is supposed to be...
                #the first function that supposedly completes a challenge question OOOOOOOOOOOOOO (does not work tho)
def completeProgressionChallenges(driver):  # Currently not used
    progression_challenges = driver.find_elements(By.XPATH,
        "//div[@class='interactive-activity-container custom-content-resource challenge large ember-view']")
    progression_challenges += driver.find_elements(By.XPATH,
        "//div[@class='interactive-activity-container custom-content-resource challenge medium ember-view']")
    progression_challenges += driver.find_elements(By.XPATH,
        "//div[@class='interactive-activity-container custom-content-resource challenge small ember-view']")
    for progression in progression_challenges:
        if checkCompleted(progression):
            print("Skipping completed progression activity")
            continue

        start_button = progression.find_element(By.XPATH,
                    ".//button[@class='zyante-progression-start-button button']")

        start_button.click()

    progression_challenges = driver.find_elements(By.XPATH,
        "//div[@class='interactive-activity-container custom-content-resource challenge large ember-view']")
    progression_challenges += driver.find_elements(By.XPATH,
        "//div[@class='interactive-activity-container custom-content-resource challenge medium ember-view']")
    progression_challenges += driver.find_elements(By.XPATH,
        "//div[@class='interactive-activity-container custom-content-resource challenge small ember-view']")
    for progression in progression_challenges:
        if checkCompleted(progression):
            print("Skipping completed progression activity")
            continue

        check_button = progression.find_element(By.XPATH,
                    ".//button[@class='zyante-progression-check-button button']")

        check_button.click()

    progression_challenges = driver.find_elements(By.XPATH,
        "//div[@class='interactive-activity-container custom-content-resource challenge large ember-view']")
    progression_challenges += driver.find_elements(By.XPATH,
        "//div[@class='interactive-activity-container custom-content-resource challenge medium ember-view']")
    progression_challenges += driver.find_elements(By.XPATH,
        "//div[@class='interactive-activity-container custom-content-resource challenge small ember-view']")
    text_array = []
    for progression in progression_challenges:
        if checkCompleted(progression):
            print("Skipping completed progression activity")
            continue

        data = progression.find_element(By.XPATH,
                    ".//div[@class='output expected-output']").text

        text_array.append(data)

        next_button = progression.find_element(By.XPATH,
                    ".//button[@class='zyante-progression-next-button button']")

        next_button.click()

    progression_challenges = driver.find_elements(By.XPATH,
        "//div[@class='interactive-activity-container custom-content-resource challenge large ember-view']")
    progression_challenges += driver.find_elements(By.XPATH,
        "//div[@class='interactive-activity-container custom-content-resource challenge medium ember-view']")
    progression_challenges += driver.find_elements(By.XPATH,
        "//div[@class='interactive-activity-container custom-content-resource challenge small ember-view']")

    for i, progression in enumerate(progression_challenges):
        if checkCompleted(progression):
            print("Skipping completed progression activity")
            continue

        text_area = question.find_element(By.CSS_SELECTOR, "textarea.console")

        text_area.send_keys(text_array[i])

        check_button = progression.find_element(By.XPATH,
                    ".//button[@class='zyante-progression-check-button button']")

        check_button.click()
        
        progression_status = progression.find_elements(By.XPATH,".//div[@class='zyante-progression-status-bar'']/div")
        for status in progression_status:
            if status.text == 1:
                start_button = progression.find_element(By.XPATH,
                    ".//button[@class='zyante-progression-start-button button']")
                start_button.click()
            else:
                next_button = progression.find_element(By.XPATH,"class='zyante-progression-next-button button']")
                next_button.click()
    return


######################################
######################################
######################################

#ok maybe this bit also look good... comparing it to the mayhem above
options.binary_location=r'C:\Program Files\Google\Chrome\Application\chrome.exe'

driver = webdriver.Chrome(options=options, executable_path='./chromedriver.exe')

try:
    login(driver, email, password, course)

    if wait_driver(driver, ".library-page") == False:
        print("Timed out while loading zyBook table of contents, aborting...")
        driver.quit()
        os._exit(0)
    print("LOGGED IN")
    selectzyBook(driver)

    if wait_driver(driver, ".table-of-contents.ember-view") == False:
        print("Timed out while loading zyBook list of sections, aborting...")
        driver.quit()
        os._exit(0)
    print("SELECTED COURSE")

    while True:
        chapter = chapterSelection(driver)

        if wait_driver(driver, ".section-list"):
            sectionSelection(driver, chapter)
            print("Participation activities completed.\n")

except Exception as e:
    print("ERROR: main")
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(exc_type, fname, exc_tb.tb_lineno)
    print(e)
    

driver.quit()
