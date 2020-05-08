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


    def _get_posts(self, user_profile, spam_count):
        links=[]
        self.driver.get('https://www.instagram.com/'+user_profile+'/?hl=en')
        for i in range(spam_count):
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            sleep(1)
        page = self.driver.find_element_by_xpath("//*[@id=\"react-root\"]/section/main/div/div[3]/article")
        all_posts = page.find_elements_by_tag_name("a")
        for post in all_posts:
            link = post.get_attribute("href")
            links.append(link)
        return links

    
    def _get_all_posts(self, user_profile):
        links=[]
        self.driver.get('https://www.instagram.com/'+user_profile+'/?hl=en')
        sleep(2)
        height, last_height = 0, 1
        while last_height != height:
            last_height = height
            height = self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight); return document.body.scrollHeight;")
            sleep(2)
            page = self.driver.find_element_by_xpath("//*[@id=\"react-root\"]/section/main/div/div[3]/article")
            elements = page.find_elements_by_tag_name("a")

            for element in elements:
                if element.get_attribute('href') not in links:
                    links.append(element.get_attribute('href'))            
        return links


    # function to spam the posts from a user's profile
    def spam_posts(self, user_profile, spam_count):
        links = self._get_posts(user_profile, spam_count)
        for link in links:
            self.driver.get(link)
            comment_box = ui.WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "textarea.Ypffh")))
            comment_box.click()
            self.driver.find_element_by_xpath("//*[@id=\"react-root\"]/section/main/div/div[1]/article/div[2]/section[3]/div/form/textarea").send_keys(spam_list[random.randint(0,len(spam_list)-1)])
            #self.driver.find_element_by_xpath("//button[contains(text(), 'Post')]").click()
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
        print(len(names))
        return names


    def _get_follow_list(self, user_profile, follow_list):
        page_wait = ui.WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, \"/{0}\")]".format(follow_list))))
        self.driver.find_element_by_xpath("//a[contains(@href, \"/{0}\")]".format(follow_list)).click()
        names = self._get_names()
        return names
    

    # function to get the difference between follower and following list
    def get_follow_list_comparison(self, user_profile):
        self.driver.get('https://www.instagram.com/'+user_profile+'/?hl=en')
        followers = self._get_follow_list(user_profile, "followers")
        following = self._get_follow_list(user_profile, "following")
        list_of_not_follower = [name for name in following if name not in followers]
        list_of_not_following = [name for name in followers if name not in following]
        print("These pages are not following you: {0}\n".format(list_of_not_follower))
        print("You are not following these pages: {0}\n".format(list_of_not_following))



    def _get_likers(self):
        sleep(2)
        users = []
        height = self.driver.find_element_by_xpath("/html/body/div[4]/div/div[2]/div/div").value_of_css_property("padding-top")
        match = False
        while match==False:
            lastHeight = height

            elements = self.driver.find_elements_by_xpath("//*[@id]/div/a")

            for element in elements:
                if element.get_attribute('title') not in users:
                    users.append(element.get_attribute('title'))

            self.driver.execute_script("return arguments[0].scrollIntoView();", elements[-1])
            sleep(1)

            height = self.driver.find_element_by_xpath("/html/body/div[4]/div/div[2]/div/div").value_of_css_property("padding-top")
            if lastHeight==height:
                match = True

        print(users)
        close = self.driver.find_element_by_xpath("/html/body/div[4]/div/div[1]/div/div[2]/button").click() 
        return users


    # function to get number of likes of posts from a user's profile
    def get_num_of_likes(self, user_profile, num_posts=0):
        links = self._get_all_posts(user_profile)
        sleep(2)
        all_posts_likes = []
        if num_posts == 0:
            num_posts = len(links)
        for i in range(num_posts):
            self.driver.get(links[i])
            sleep(2)
            self.driver.find_element_by_xpath("//*[@id=\"react-root\"]/section/main/div/div[1]/article/div[2]/section[2]/div/div/button").click()
            likers = self._get_likers()
            num_likes = len(likers)
            all_posts_likes.append(num_likes)
        print(all_posts_likes)

      

# fill in your login details in login.py
# initialise bot with "bot = Instabot()"
