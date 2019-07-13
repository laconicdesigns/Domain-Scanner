'''
Classed up webscan.py.

Website Scanner - Author: Blake Bartlett
Use: Scans websites blindly for files and directories that are determined by 
each line in a designated dictionary file. Keep each word on a separate line.
Outputs everything in console to a file for ease of use.

ToDo:
    :Make sure the input URL is sanitized and a proper URL with the format:
        http(s)://some.url.com
    :Output robots.txt if found. 
    
Change Log:
    7/10/2019 - Added change log.
    7/10/2019 - Started class-based program.
    7/13/2019 - Added to github. https://github.com/NotoriousBlake/Domain-Scanner.git
'''

import sys #System - Used for command line arguments.
import requests #Initially for url status codes. Going to pull robots.txt too.
from datetime import datetime #Used for getting time for unique file names.
import time #throttling using sleep()
import os

class output():
    def __init__(self, output_string):
        current_time = datetime.now().strftime('%m-%d-%Y.%H-%M-%S')
        self.file_name = file_name
        if output_string != None:
            self.output_string = output_string
        else:
            output_string = "\n"

    def file_write(output_file_name):
        pass

    def file_open(output_file_name):
        pass

    def file_close(output_file_name):
        pass

    def do():
        print(output_string)

class server():
    def __init__(self,url,wordlist):
        self.url = url
        self.file_extensions = ['php','html','txt','css','asp','htm']
        self.throttle_multiplier = 10 #Time to get a file multiplied by this
        self.busy_animation = ['/','-','\\','|']

        try:
            self.url_good = self.good_url(self.url) #Get a good URL
            start_throttle_timer = scan_timer()     #Starting throttle timer
            start_throttle_timer.start()
            request = requests.get(self.url_good)   #Get good URL obj
            start_throttle_timer.stop()
            if start_throttle_timer.length() > 0:
                self.throttle_timer = self.throttle_multiplier * start_throttle_timer.length()
                #print("Throttle Timer: {}".format(self.throttle_timer), end="\r")
            #self.status_code = request.status_code
            #self.html = request.text
            #print("::HEADERS:: ", request.headers)
        except Exception as e:
            print("Couldn't get website information. Error Info:" + e)

    def good_url(self, url):
        good_url = ""
        url_first_four = url[0:4]
        if url_first_four != "http":
            if url_first_four != "www.":
                good_url = "http://www." + url
            else:
                good_url = "http://" + url
            #This is a good start.
            if url_first_four != "www.":
                good_url = "http://www." + url
            else:
                good_url = "http://" + url
        else:
            good_url = url
            #Just return the url

        if good_url[-1] != "/":
            good_url = good_url + "/"
            #This shouldn't affect anything, and also makes the word_list section cleaner

        return good_url

    def scan_website(self, wordlist):
        try:
            list_of_words = wordlist.text.splitlines(True)
            #print("Word Count: ", len(list_of_words))
            #print(self.html)
        except Exception as e:
            print("Error getting wordlist information. ->", e)
            return
        
        print("\nWorking domains printed below for",self.url_good)
        print("-=-=-=-=-=-=-=-=-=-=")
        try_count = 0
        for word in list_of_words:
            try:
                #print("Throttle Timer: {}".format(self.throttle_timer), end="\r")
                print("Working... {}".format(self.busy_animation[try_count % 4]), end="\r")
                time.sleep(self.throttle_timer)
                scan_url_dir = self.url_good + word.strip().strip("/")
                scan_req_dir = requests.get(scan_url_dir)
                try_count += 1
                if scan_req_dir.status_code < 400 or scan_req_dir.status_code > 499:
                    print(scan_url_dir,"->", scan_req_dir.status_code)

                for ext in self.file_extensions: #dynamic URLs
                    time.sleep(self.throttle_timer)
                    scan_url = self.url_good + word.strip() + "." + ext
                    scan_timer2 = scan_timer() #Throttle timer stuff
                    scan_timer2.start()
                    scan_req = requests.get(scan_url)
                    scan_timer2.stop()
                    if scan_timer2.length() > 0:
                        self.throttle_timer = self.throttle_multiplier * scan_timer2.length() #Throttling 2.0
                        print("Working... {}".format(self.busy_animation[try_count % 4]), end="\r")
                    try_count += 1 #counting unique urls that are getting scanned
                    #print("URLs Tested: {}".format(try_count), end="\r")
                    if scan_req.status_code < 400 or scan_req.status_code > 499:
                        print(scan_url,"->", scan_req.status_code)
            except Exception as e:
                print("Error Scanning Website ->", e)
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)
            
        #After that works
        #get all the info from robots.txt and scan those directories
        try:
            robot_url = self.url_good + "robots.txt"
            print("\nChecking for",robot_url)
            
            robot_req = requests.get(robot_url)
            robots_list = robot_req.text
            robots_sc = robot_req.status_code
            if robots_sc == 404:
                print(robot_url,"does not exist.")
            else:
                print("robot_url ->", robots_sc)
                print(robots_list)
        except Exception as e:
            print("Error getting robots.txt->",e)
        
        print("Tested",try_count,"urls.")
        #determine directory structure for the website, and recurse through
        #directories applying wordlist each time.
        
        #Alert user to robots.txt directories, and ask to insert unique values
        #into words.txt for usage on future projects.
        
        #Also make the wordlist dynamic by adding appropriate file extensions
        #to add to the words. ie. .php .txt .html .wtf .js .css
        
        #Change the wordlist dynamically too, so it replaces characters with
        #similar characters, such as p4ssw0rd or p455w0rd, etc.
        
        #Put together a system that throttles the scanning speed, so as to not
        #DOS the server you're scanning, and maybe to stay under the radar too.
        #I imagine this could all get very resource intense, depending on the
        #recursion

class word_list():
    def __init__(self,location):
        self.location = location
        #TODO: ideally location would be a URL or a local file.
        #TODO: Check to see if the file exists. We're going to assume it does
        try:
            self.text = self.open_file()
            self.word_count = len(self.text)
        except Exception as e:
            print("Couldn't open file. ->",e)

    def open_file(self):
        opened_file = open(self.location, 'r+')
        opened_file_text = opened_file.read()
        opened_file.close()
        return opened_file_text
        
class scan_timer():
    def __init__(self):
        self.start_time = 0
        self.stop_time = 0
        #self.duration = 0
        
    def start(self):
        self.start_time = time.time()
        #print("Timer Start ->",self.start_time)
        
    def stop(self):
        self.stop_time = time.time()
        #print("Timer Stop ->", self.stop_time)
        
    def length(self):
        if self.start_time == 0 or self.stop_time == 0:
            len = 0
        else:
            len = self.stop_time - self.start_time
        return len

print("Starting Webscan(Classy Version)")
temp_website = input("What URL would you like to scan? ->")
temp_wordlist = input("And where is your wordlist located at? Local File Directory: ")

op_timer1 = time.time()

my_wordlist = word_list(temp_wordlist)
#my_wordlist.text = word_list(temp_wordlist)
my_server = server(temp_website, my_wordlist)
if my_server.scan_website(my_wordlist) != False:
    try:
        print("Finished scan of", my_server.url_good)
        print("Operation took {:.2f} sec to complete".format((time.time() - op_timer1)))
    except Exception as e:
        print("Error starting scan of", my_server.url_good,". e:", e)