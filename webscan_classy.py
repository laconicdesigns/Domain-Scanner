"""
Classed up webscan.py.

Website Scanner - Author: Blake Bartlett
Use: Scans websites blindly for files and directories that are determined by
each line in a designated dictionary file. Keep each word on a separate line.
Outputs everything in console to a file for ease of use.

    TODO:
        Add comments everywhere.
        Finish output function!

Change Log:
    7/10/2019 - Added change log.
    7/10/2019 - Started class-based program.
    7/13/2019 - Added to github. https://github.com/NotoriousBlake/Domain-Scanner.git
    7/18/2019 - Added version number. Starting today @ 0.0.1
                Created a scan_url() function to kill some repetetive text
    7/22/2019 - Started using PyCharm. Fixed a bunch of coding errors. Worked on scan_html().
    7/24/2019 - Added get_domain(url) function. it pulls url.com from http://www.url.com/test/foo.bar?boo=far&baf=oor
"""

import os
import sys
import time
from datetime import datetime  # Used for getting time for unique file names.

import requests  # Initially for url status codes. Going to pull robots.txt too.
from lxml import html as lhtml

ws_version = "0.0.3"
debug = False


class Output:
    #my output = Output
    #my_output.out(string,booldebug)
    def __init__(self, domain):
        try:
            current_time = datetime.now().strftime('%m-%d-%Y.%H-%M-%S')
            self.domain = domain
            self.file_name = self.domain + current_time + ".txt"
            self.log_file = self.file_open(self.file_name)
        except Exception as initExc:
            print("Error creating Output class: {}".format(initExc))

    def file_write(self, output_string):
        try:
            self.log_file.write(str(output_string) + "\n")
        except Exception as fwExc:
            print("Log file write error: {}".format(fwExc))

    def file_open(self, output_file_name):
        try:
            file = open(output_file_name, "x")
            return file
        except Exception as logExc:
            print("File open error: {}".format(logExc))

    def file_close(self):
        self.log_file.close()

    def do(self, output_string, *args):
        if len(args) > 0:
            if args[0] == True:
                if debug:
                    print(output_string)
                    self.file_write(output_string)
        else:
            print(output_string)
            self.file_write(output_string)


class Server:
    def __init__(self, url, wordlist):
        self.url = url
        self.file_extensions = ['php', 'html', 'txt', 'css', 'asp', 'htm']
        self.throttle_multiplier = 4  # Time to get a file multiplied by this
        self.busy_animation = ['/', '-', '\\', '|']
        self.wordlist_len = len(wordlist)
        self.url_list = []

        self.soutput = Output(self.url)

        self.soutput.do("Words in Wordlist: {}".format(self.wordlist_len))
        try:
            if self.wordlist_len > 0:
                self.url_good = self.good_url(self.url)  # Get a good URL
                start_throttle_timer = ScanTimer()  # Starting throttle timer
                start_throttle_timer.start()
                start_page = requests.get(self.url_good, allow_redirects=False, timeout=5)  # Get good URL obj
                self.scan_html(start_page.text)
                start_throttle_timer.stop()
                if start_throttle_timer.length > 0:
                    self.throttle_timer = self.throttle_multiplier * start_throttle_timer.length
            else:
                raise ValueError("Wordlist is empty")
        except Exception as exx:
            self.soutput.do("Couldn't get website information. Error Info:\n{}".format(str(exx)))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            self.soutput.do("{}\n[] - Line {}".format(exc_type, fname, exc_tb.tb_lineno))

    def good_url(self, url):
        good_url: str = ""
        url_first_four = url[0:4]
        if url_first_four != "http":
            if url_first_four != "www.":
                good_url = "https://www." + url
            else:
                good_url = "https://" + url
            # This is a good start.
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
            self.soutput.do("\nScanning URL: {}".format(url), True)
        scan_req = requests.get(url, allow_redirects=False, timeout=5)
        scan_req_sc = scan_req.status_code
        if scan_req_sc == 200:
            if len(scan_req.text) > 0:
                self.soutput.do("ASDF {}".format(self.scan_html(scan_req.text)))
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
            anchor_tags += root.xpath("//iframe/@src")
            anchor_tags += root.xpath("//script/@src")
            anchor_tags += root.xpath("//link/@href")
            anchor_tags += root.xpath("//image/@src")
            anchor_count = len(anchor_tags)
            #self.soutput.do("{} anchor tags at {}".format(anchor_count, self.url_good))
            #should be moved to wherever is calling this function
            if anchor_count > 0:
                #self.soutput.do(anchor_tags)
                for link in anchor_tags:
                    link_full = self.full_url(link)
                    if link_full in self.url_list:
                        #We've already scanned this URL.
                        continue
                    else:
                        self.url_list.append(link_full)
                        self.soutput.do("Link: {}".format(link_full), True)
                        #Scan the URL, but only if it's on the same domain we started with.
                        if self.get_domain(link_full) == self.get_domain(self.url_good):
                            #self.scan_website()
                            self.scan_url(link_full)
                            #self.soutput.do(self.full_url(link))


    def scan_website(self, wordlist):
        directory_structure = []  # Storing found directories.

        self.soutput.do("\nWorking domains printed below for {}".format(self.url_good))
        self.soutput.do("-=-=-=-=-=-=-=-=-=-=")
        try_count = 0
        for word in wordlist:
            try:
                # print("Working... {}".format(self.busy_animation[try_count % 4]), end="\r")
                print("URLs tested: {}\r".format(try_count), end="")
                time.sleep(self.throttle_timer)
                #ytmnd.com didn't create a throttle_timer variable, but the program made it here anyhow.
                clean_directory = word.strip().strip("/")
                scan_url_dir = self.url_good + clean_directory
                scan_sc, scan_req_text_lines = self.scan_url(scan_url_dir)
                try_count += 1
                print("URLs tested: {}\r".format(try_count), end="")
                if scan_sc == 200:
                    self.soutput.do(scan_url_dir, "->", scan_sc)
                    # Here's an available directory.
                    directory_structure.append(clean_directory)
                    self.soutput.do("Found a directory.\n{}".format(directory_structure))
                elif scan_sc < 300 or scan_sc > 499:
                    if debug:
                        self.soutput.do("URL: {}  Status Code: {}".format(scan_url_dir, scan_sc), True)
                #an else here would target 300s and 400s status codes
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
                        print("URLs tested: {}\r".format(try_count), end="")
                    try_count += 1  # counting unique urls that are getting scanned
                    if scan_sc == 200:
                        self.soutput.do(ext_url, "->", scan_sc)
                    elif scan_sc < 300 or scan_sc > 499:
                        if debug:
                            self.soutput.do("URL: {}  Status Code: {}".format(scan_url_dir, scan_sc), True)
            except AttributeError:
                #Likely a dead website.
                pass
            except Exception as exce:
                if debug:
                    self.soutput.do("Error Scanning Website: {}".format(exce))
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                self.soutput.do(str(exc_type))
                self.soutput.do("{} - Line #: {}".format(str(fname), str(exc_tb.tb_lineno)))

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
                self.soutput.do("robots.txt error. Status Code: {}".format(robots_sc))
            else:
                self.soutput.do("{}robots.txt found.\nProcessing...".format(self.url_good))
                for line in robots_list:
                    try:
                        list_words = line.split(" ")
                        if len(list_words) > 1:
                            robot_property = list_words[0].strip(":")
                            robot_value = list_words[1].strip("\n")
                    except Exception as excep:
                        self.soutput.do("Error getting robots.txt -> {} {}".format(excep, list_words))
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                        self.soutput.do(exc_type, fname, exc_tb.tb_lineno)
                        break
                    # print(line)
                    if robot_property == "Sitemap":
                        # woodoggy. Let's go parse that. But we should probably
                        # compare it to our own directory structure first, and
                        # note the differences.
                        sitemap_location = robot_value
                        self.soutput.do("Found a sitemap: {}".format(sitemap_location))
                        self.scan_url(sitemap_location)
                    elif robot_property == "Disallow":
                        robot_disallow.append(robot_value.strip("/"))
                        continue
                    elif robot_property == "#":
                        continue
                    elif len(robot_value) > 1:
                        stripped_domain = robot_value.strip("/")
                        if stripped_domain[0] == "/":
                            if stripped_domain not in robot_domains:
                                robot_domains.append(stripped_domain)
                self.soutput.do("Unique Domains: {}".format(robot_domains))
                self.soutput.do("Disallowed Domains: {}".format(robot_disallow))
        except Exception as e:
            self.soutput.do("Error getting robots.txt->", e)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            self.soutput.do(exc_type, fname, exc_tb.tb_lineno)

        self.soutput.do("Tested {} urls.".format(try_count))
        # determine directory structure for the website, and recurse through
        # directories applying wordlist each time.
        # func scan_html(string html) that returns a list of urls found from
        # a xpath
        if len(robot_domains) < 1:
            self.soutput.do("No working domains found.")
        else:
            self.soutput.do("Found some domains.")
            for domain in robot_domains:
                self.soutput.do("{}\n".format(domain))
        # check each of the found domains.
        if len(self.url_list) > 0:
            self.soutput.do("Found some other URLs:\n{}".format(self.url_list))

        return True
        # Alert user to robots.txt directories, and ask to insert unique values
        # into words.txt for usage on future projects.
        # I think it's just going to be urged that the user enter in appropriate directories themselves.

        # TODO: Need a function to parse URLs and return a whole http://www.url.com format string_
        #   would be used by scan_html()

        # Change the wordlist dynamically too, so it replaces characters with
        # similar characters, such as p4ssw0rd or p455w0rd, etc.
    def full_url(self, partial_url):
        #partial_urls I expect: /directory/, /file.ext, url.com, www.url.com, http://www.url.com
        if len(partial_url) > 0:
            if partial_url[0:4] == "http":
                #already a full url as far as i'm concerned...
                #well actually, this let's http://url.com through
                return partial_url
            elif partial_url[0:4] == "www.":
                #we're real close.
                fUrl = "https://" + partial_url
                return fUrl
            elif len(partial_url.split(".")) == 2:
                #url.com, url.jp, url.wtfever
                #ooh... or /file.ext...
                if partial_url[0] == "/":
                    #local directory
                    fUrl = self.url_good + partial_url
                else:
                    #external url
                    fUrl = "https://www." + partial_url
                return fUrl
            elif partial_url[0] == "/":
                fUrl = self.url_good + partial_url.strip("/")
                return fUrl
            else:
                #should be a local directory, I guess...
                fUrl = self.url_good + partial_url.strip("/")
                return fUrl

    def get_domain(self, url):
        #ideally this only gets passed full URLs, but I guess we should sanitize anyhow
        domain_full_url = self.full_url(url)
        #https://www.url.com/whtf/ever.php?s=24&tfu=yes!
        domain_space_list = domain_full_url.split(".")
        if len(domain_space_list) > 2:
            part1 = domain_space_list[1]
            pt2_split_list = domain_space_list[2].split("/")
            part2 = pt2_split_list[0]
            ret_url = part1 + part2
        elif len(domain_space_list) == 2:
            #http://domain.com, or something else that will break the code
            part2 = domain_space_list[1].strip("/")
            part1_colon_list = domain_space_list[0].split(":")
            part1 = part1_colon_list[1].strip("/")
            ret_url = part1 + part2
        else:
            #something else...
            ret_url = url
        return ret_url


class WordList:
    def __init__(self, location):
        self.location = location
        # TODO: ideally location would be a URL or a local file.
        # TODO: Check to see if the file exists. We're going to assume it does
        try:
            self.lines = self.open_file
            self.word_count = len(self.lines)
        except Exception as exc:
            self.soutput.do("Couldn't open file. -> {}".format(exc))

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
            my_server.soutput.do("Finished scan of {} in {:.2f} seconds.".format(my_server.url_good, (time.time() - op_timer1)))
        except Exception as e:
            my_server.soutput.do("Error starting scan of {}. e: {}".format(my_server.url_good, e))
