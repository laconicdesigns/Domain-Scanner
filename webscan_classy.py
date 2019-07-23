"""
Classed up webscan.py.

Website Scanner - Author: Blake Bartlett
Use: Scans websites blindly for files and directories that are determined by
each line in a designated dictionary file. Keep each word on a separate line.
Outputs everything in console to a file for ease of use.

    TODO:
        Add comments everywhere.

Change Log:
    7/10/2019 - Added change log.
    7/10/2019 - Started class-based program.
    7/13/2019 - Added to github. https://github.com/NotoriousBlake/Domain-Scanner.git
    7/18/2019 - Added version number. Starting today @ 0.0.1
                Created a scan_url() function to kill some repetetive text
    7/22/2019 - Started using PyCharm. Fixed a bunch of coding errors. Worked on scan_html().
"""

import os
import sys
import time
from datetime import datetime  # Used for getting time for unique file names.

import requests  # Initially for url status codes. Going to pull robots.txt too.
from lxml import html as lhtml

ws_version = "0.0.2"
debug = False


class Output:
    def __init__(self, output_string):
        current_time = datetime.now().strftime('%m-%d-%Y.%H-%M-%S')
        self.file_name = current_time + ".txt"
        if output_string is not None:
            self.output_string = output_string
        else:
            self.output_string = "\n"

    def file_write(self, output_file_name):
        pass

    def file_open(self, output_file_name):
        pass

    def file_close(self, output_file_name):
        pass

    @staticmethod
    def do(self):
        print(self.output_string)

class Server:
    def __init__(self, url, wordlist):
        self.url = url
        self.file_extensions = ['php', 'html', 'txt', 'css', 'asp', 'htm']
        self.throttle_multiplier = 4  # Time to get a file multiplied by this
        self.busy_animation = ['/', '-', '\\', '|']
        self.wordlist_len = len(wordlist)

        print("Words in Wordlist: {}".format(self.wordlist_len))
        try:
            if self.wordlist_len > 0:
                self.url_good = self.good_url(self.url)  # Get a good URL
                start_throttle_timer = ScanTimer()  # Starting throttle timer
                start_throttle_timer.start()
                start_page = requests.get(self.url_good, allow_redirects=False)  # Get good URL obj
                self.scan_html(start_page.text)
                start_throttle_timer.stop()
                if start_throttle_timer.length > 0:
                    self.throttle_timer = self.throttle_multiplier * start_throttle_timer.length
            else:
                raise ValueError("Wordlist is empty")
        except Exception as exx:
            print("Couldn't get website information. Error Info:" + exx)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)

    def good_url(self, url):
        good_url: str = ""
        url_first_four = url[0:4]
        if url_first_four != "http":
            if url_first_four != "www.":
                good_url = "http://www." + url
            else:
                good_url = "http://" + url
            # This is a good start.
            if url_first_four != "www.":
                good_url = "http://www." + url
            else:
                good_url = "http://" + url
        else:
            good_url = url
            # Just return the url

        if good_url[-1] != "/":
            good_url = good_url + "/"
            # This shouldn't affect anything, and also makes the word_list section cleaner
        return good_url

    def scan_url(self, url):
        # url is a clean url
        if debug:
            print("\nScanning URL: {}".format(url))
        scan_req = requests.get(url, allow_redirects=False)
        scan_req_sc = scan_req.status_code
        if debug:
            print("SEARCHING URL: {}".format(url))
        if scan_req_sc == 200:
            if len(scan_req.text) > 0:
                print(self.scan_html(scan_req.text))
                scan_req_list_lines = scan_req.text.splitlines(True)
            else:
                error_text = url + " was blank."
                raise ValueError(error_text)
        else:
            scan_req_list_lines = []
        return scan_req_sc, scan_req_list_lines

    def scan_html(self, html):
        # html is a string
        if len(html) > 0:
            root = lhtml.fromstring(html)
            anchor_tags = root.xpath("//a/@href")
            print("{} anchor tags at {}:".format(len(anchor_tags), self.url_good))
            print(anchor_tags)

    def scan_website(self, wordlist):

        directory_structure = []  # Storing found directories.

        print("\nWorking domains printed below for", self.url_good)
        print("-=-=-=-=-=-=-=-=-=-=")
        try_count = 0
        for word in wordlist:
            try:
                # print("Working... {}".format(self.busy_animation[try_count % 4]), end="\r")
                print("URLs tested: {}".format(try_count), end="\r")
                time.sleep(self.throttle_timer)
                clean_directory = word.strip().strip("/")
                scan_url_dir = self.url_good + clean_directory
                scan_sc, scan_req_text_lines = self.scan_url(scan_url_dir)
                try_count += 1
                print("URLs Tested: {}".format(try_count), end="\r")
                if scan_sc == 200:
                    print(scan_url_dir, "->", scan_sc)
                    # Here's an available directory.
                    directory_structure.append(clean_directory)
                    print("Current Dir Structure -> {}".format(directory_structure))
                else:
                    if debug:
                        print("URL: {}  Status Code: {}".format(scan_url_dir, scan_sc))
                for ext in self.file_extensions:  # dynamic URLs
                    time.sleep(self.throttle_timer)
                    ext_url = self.url_good + word.strip() + "." + ext
                    scan_timer2 = ScanTimer()  # Throttle timer stuff
                    scan_timer2.start()
                    scan_sc, scan_req_text_lines = self.scan_url(ext_url)
                    scan_timer2.stop()
                    if scan_timer2.length > 0:
                        self.throttle_timer = self.throttle_multiplier * scan_timer2.length  # Throttling 2.0
                        # print("Working... {}".format(self.busy_animation[try_count % 4]), end="\r")
                        print("URLs tested: {}".format(try_count), end="\r")
                    try_count += 1  # counting unique urls that are getting scanned
                    if scan_sc == 200:
                        print(ext_url, "->", scan_sc)
                    else:
                        if debug:
                            print("URL: {}  Status Code: {}".format(ext_url, scan_sc))
            except Exception as exce:
                if debug:
                    print("Error Scanning Website ->", exce)
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)

        # After that works
        # get all the info from robots.txt and scan those directories
        robot_domains = []
        robot_disallow = []
        robot_property = ""
        robot_value = ""
        try:
            robot_url = self.url_good + "robots.txt"
            robots_sc, robots_list = self.scan_url(robot_url)

            if robots_sc != 200:
                print("robots.txt error. Status Code: {}".format(robots_sc))
            else:
                print("robots.txt found.\nProcessing...")
                for line in robots_list:
                    try:
                        list_words = line.split(" ")
                        if len(list_words) > 1:
                            robot_property = list_words[0].strip(":")
                            robot_value = list_words[1].strip("\n")
                    except Exception as excep:
                        print("Error getting robots.txt -> {} {}".format(excep, list_words))
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                        print(exc_type, fname, exc_tb.tb_lineno)
                        break
                    # print(line)
                    if robot_property == "Sitemap":
                        # woodoggy. Let's go parse that. But we should probably
                        # compare it to our own directory structure first, and
                        # note the differences.
                        sitemap_location = robot_value
                        print("Found a sitemap: {}".format(sitemap_location))
                    elif robot_property == "Disallow":
                        robot_disallow.append(robot_value)
                        continue
                    elif len(robot_value) > 1:
                        if robot_value[0] == "/":
                            if robot_value not in robot_domains:
                                robot_domains.append(robot_value)
                print("Unique Domains: {}".format(robot_domains))
                print("Disallowed Domains: {}".format(robot_disallow))
        except Exception as e:
            print("Error getting robots.txt->", e)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)

        print("Tested", try_count, "urls.")
        # determine directory structure for the website, and recurse through
        # directories applying wordlist each time.
        # func scan_html(string html) that returns a list of urls found from
        # a xpath
        if len(robot_domains) < 1:
            print("No working domains found.")
        else:
            print("Found some domains.")
            for domain in robot_domains:
                print("{}\n".format(domain))
        # check each of the found domains.
        return True
        # Alert user to robots.txt directories, and ask to insert unique values
        # into words.txt for usage on future projects.

        # Change the wordlist dynamically too, so it replaces characters with
        # similar characters, such as p4ssw0rd or p455w0rd, etc.


class WordList:
    def __init__(self, location):
        self.location = location
        # TODO: ideally location would be a URL or a local file.
        # TODO: Check to see if the file exists. We're going to assume it does
        try:
            self.lines = self.open_file
            self.word_count = len(self.lines)
        except Exception as exc:
            print("Couldn't open file. ->", exc)

    @property
    def open_file(self):
        opened_file = open(self.location, 'r+')
        opened_file_list = opened_file.readlines()
        opened_file.close()
        return opened_file_list

    def get_list(self):
        return self.lines


class ScanTimer:
    def __init__(self):
        self.start_time = 0
        self.stop_time = 0

    def start(self):
        self.start_time = time.time()

    def stop(self):
        self.stop_time = time.time()

    @property
    def length(self):
        if self.start_time == 0 or self.stop_time == 0:
            # we haven't completed timing something.
            leng = 0
        else:
            leng = self.stop_time - self.start_time
        return leng


if __name__ == "__main__":

    print("Domain Scanner, written by Blake Bartlett.\nVersion: {}\n".format(ws_version))
    temp_website = input('What URL would you like to scan? ->')
    temp_wordlist = input("And where is your wordlist located at? Local File Directory: ")

    op_timer1: float = time.time()  # Start timer for whole program to run.

    my_wordlist = WordList(temp_wordlist).get_list()
    my_server = Server(temp_website, my_wordlist)
    if my_server.scan_website(my_wordlist):
        try:
            print("Finished scan of {} in {:.2f} seconds.".format(my_server.url_good, (time.time() - op_timer1)))
        except Exception as e:
            print("Error starting scan of", my_server.url_good, ". e:", e)
