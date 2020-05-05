from selenium import webdriver
from time import sleep
from login import username, pw
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup as bs
import requests
import json
from selenium.webdriver.support import ui, expected_conditions as EC
from selenium.webdriver.common.by import By
import random
from spam import spam_list

#add in the username of the intended target
profile_name = ''
url = "https://www.instagram.com/"

class InstaBot():
    def __init__(self, username, pw):
        self.driver = webdriver.Chrome()
        self.driver.get(url)
        login_box = ui.WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//input[@name=\"username\"]")))
        login_box.send_keys(username)
        self.driver.find_element_by_xpath("//input[@name=\"password\"]").send_keys(pw)
        self.driver.find_element_by_xpath("//button[@type=\"submit\"]").click()
        not_now = ui.WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Not Now')]")))
        not_now.click()



    def _get_posts(self, user_profile):
        links=[]
        self.driver.get('https://www.instagram.com/'+user_profile+'/?hl=en')
        Pagelength = self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(1)
        source = self.driver.page_source
        data = bs(source, 'html.parser')
        body = data.find('body')
        script = body.find('script', text=lambda t: t.startswith('window._sharedData'))
        page_json = script.text.split(' = ', 1)[1].rstrip(';')
        data = json.loads(page_json)
        for link in data['entry_data']['ProfilePage'][0]['graphql']['user']['edge_owner_to_timeline_media']['edges']:
            links.append('https://www.instagram.com'+'/p/'+link['node']['shortcode']+'/')
        return links


    # function that spams the first 12 posts of a target user
    def spam_posts(self, user_profile):
        links = self._get_posts(user_profile)
        for link in links:
            self.driver.get(link)
            comment_box = ui.WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "textarea.Ypffh")))
            comment_box.click()
            self.driver.find_element_by_xpath("//*[@id=\"react-root\"]/section/main/div/div[1]/article/div[2]/section[3]/div/form/textarea").send_keys(spam_list[random.randint(0,len(spam_list)-1)])
            self.driver.find_element_by_xpath("//button[contains(text(), 'Post')]").click()
            sleep(1)




    def _get_names(self):
        box_wait = ui.WebDriverWait(self.driver, 10).until(EC.visibility_of_any_elements_located((By.CSS_SELECTOR, "div.isgrP")))
        scroll_box = self.driver.find_element_by_xpath("/html/body/div[4]/div/div[2]")

        last_height, height = 0, 1
        while last_height != height:
            last_height = height
            sleep(1)
            height = self.driver.execute_script("arguments[0].scrollTo(0, arguments[0].scrollHeight); return arguments[0].scrollHeight;", scroll_box)

        follow_box = self.driver.find_element_by_xpath("/html/body/div[4]/div/div[2]/ul/div")
        links = follow_box.find_elements_by_tag_name("a")
        names = [name.text for name in links if name.text != '']
        close = self.driver.find_element_by_xpath("/html/body/div[4]/div/div[1]/div/div[2]/button").click()
        return names



    def _get_follow_list(self, user_profile, follow_list):
        page_wait = ui.WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, \"/{0}\")]".format(follow_list))))
        self.driver.find_element_by_xpath("//a[contains(@href, \"/{0}\")]".format(follow_list)).click()
        names = self._get_names()
        return names
    

    # function to get all followers and following of a user, and prints the usernames that do not appear in both lists. 
    def get_follow_list_comparison(self, user_profile):
        self.driver.get('https://www.instagram.com/'+user_profile+'/?hl=en')
        followers = self._get_follow_list(user_profile, "followers")
        following = self._get_follow_list(user_profile, "following")
        list_of_not_follower = [name for name in following if name not in followers]
        list_of_not_following = [name for name in followers if name not in following]
        print("These pages are not following you: {0}\n".format(list_of_not_follower))
        print("You are not following these pages: {0}\n".format(list_of_not_following))

# fill in your login details in login.py
# initialise bot with "bot = Instabot()"
