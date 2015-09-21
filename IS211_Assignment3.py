__author__ = 'wilsonincs'
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Assignment 3"""

import csv
import urllib2
import argparse
import re
import operator
import datetime
import collections


PROJECT_URL = "http://s3.amazonaws.com/cuny-is211-spring2015/weblog.csv"

def main():

    def download_data(url):
        """ opens csv from url --accepts a string
            Tries to connect to url 3 times...
            if no connection after 3 attempts returns false to main
        """
        counter = 3

        while counter > 0:
            try:
                response = urllib2.urlopen(url)
                return response

            except urllib2.URLError:
                print 'Unable to connect to server... Trying again, please wait...'
                counter -= 1
                continue
        return False


    def data_table(data):
        """ takes raw csv data from download_data and creates a dictionary keyed to row id"""

        file_in = csv.reader(data)
        key = 1
        entries = {}

        for row in file_in:
            entries[key] = row
            key += 1

        return entries

    def process_data(table):
        """ takes dictionary from data_table and returns results to main for output to user
        2 loops - first parses images and browsers using regex and stores results in lists
                - second counts number of hits per browser
        Returns tuple-- (percent of image hits (float), most popular browser(str),
            hits per hour (list of ordered tuples descending)  """

        images = []
        browsers = []
        brows_count = {'Chrome': 0, 'Firefox': 0, 'MSIE': 0, 'Safari': 0}
        hours = collections.defaultdict(int)
        date_format = "%Y-%m-%d %H:%M:%S"

        for key, row in table.iteritems():      # main loop - regex for images and browsers
            img_search = (re.findall(r'.gif$|.png$|.jpg$|.jpeg$', row[0], re.I | re.M))
            browser_search = (re.findall(r'Chrome/|Firefox/|MSIE|'
                                         r'Version/\d.\d.\d\sSafari|Version/\d.\d\s\b[a-z0-9]+/[a-z0-9]+\b\sSafari',
                                         row[2], re.I | re.M))

            new_date = datetime.datetime.strptime(row[1], date_format)
            hours[new_date.hour] += 1       # creates a key (if not present)from hour and increments

            if len(img_search) != 0:        # appends to a new list
                images.append(img_search[0])

            if len(browser_search) != 0:    # appends to a new list
                browsers.append(browser_search[0])

        for i in browsers:      # count number of hits per browser

            if i[:3] == 'Fir':
                brows_count['Firefox'] += 1
            elif i[:3] == 'Chr':
                brows_count['Chrome'] += 1
            elif i[:3] == 'MSI':
                brows_count['MSIE'] += 1
            else:
                brows_count['Safari'] += 1

        most_used_brows = max(brows_count.iteritems(), key=operator.itemgetter(1))
        most_hit_hours = sorted(hours.iteritems(), key=operator.itemgetter(1))[::-1]  # reverse reorder
        image_percent = (float(len(images))/float(len(table))) * 100

        return image_percent, most_used_brows[0], most_hit_hours

    ## command line script...

    parser = argparse.ArgumentParser()
    parser.add_argument("--url", help="url connecting to csv file")
    args = parser.parse_args()

    if args.url:
        try:
            raw_server_data = download_data(args.url)
            if not raw_server_data:                     # returns false, fails to connect
                print "Can't connect to server... please try again later"

            else:
                table = data_table(raw_server_data)
                results = process_data(table)

                print "Image requests account for {0}% of all requests".format(results[0])
                print "{0} is the most popular browser".format(results[1])

                for hour in results[2]:
                    print "Hour {0} has {1} hits".format(hour[0], hour[1])

        except ValueError:
            print 'invalid url'

    else:
        print "you must enter a  url  next to the --url flag... program closing"

if __name__ == "__main__":

    main()
