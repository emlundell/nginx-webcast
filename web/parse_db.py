#!/usr/bin/env python3

"""
    parse(start_day, end_day) => [(connections, stream_name)]

        start_day: "2020-06-22"
        end_day: None
        connections: int
        stream_name: str


    Example:

        conn_per_stream = parse_db("2020-06-22", None)

        # Only parse one day
        $ python3 parse_db.py 2020-06-22 
        []
"""

import sqlite3
import mmap
import re
from typing import List, Tuple
import datetime
import argparse 
import os

class Parse:

    def __init__(self, start_day: str, end_day: str):

        self.conn = sqlite3.connect(':memory:')
        self.log_file_path = "/var/log/syslog-ng/"

        self._create_db()

        self.all_days = self._fill_in_days(start_day, end_day)

    def _fill_in_days(self, start_day: str, end_day: str) -> List[str]:

        end_day = end_day or start_day

        start_day_dt = datetime.datetime.strptime(start_day, "%Y-%M-%d")
        end_day_dt = datetime.datetime.strptime(end_day, "%Y-%M-%d")

        if start_day_dt > end_day_dt:
            end_day_dt, start_day_dt = start_day_dt, end_day_dt

        delta = end_day_dt - start_day_dt
        dd = [start_day_dt + datetime.timedelta(days=x) for x in range(delta.days + 1)]
        days = [datetime.datetime.strftime(d, "%Y-%M-%d") for d in dd]
        print(f"days filled in {days}")
        return days

    def _get_log_file_names(self) -> str:

        logfiles = []
        for date in self.all_days:
            if os.path.exists(f"{self.log_file_path}syslog-{date}.log"):
                logfiles.append(f"{self.log_file_path}syslog-{date}.log")
            elif os.path.exists(f"{self.log_file_path}syslog-{date}.log.zip"):
                logfiles.append(f"{self.log_file_path}syslog-{date}.log.zip")

        print(f"Logs to be parsed: {logfiles}")
        return logfiles

    def _create_db(self):
        try:
            c = self.conn.cursor()
            c.execute("CREATE TABLE stream (inserted date, ip text, uri text)")
            print("Table stream created.")
        except:
            print("Table stream already exists. Skipping creation...")

    def _insert_line(self, values: Tuple):
        with self.conn:
            c = self.conn.cursor()
            c.execute("INSERT INTO stream VALUES (?,?,?)", values)

    def parse_log_to_db(self):
        
        """
        Jun 22 09:27:11 9bda909079bd 172.19.0.4 - - [22/Jun/2020:09:27:11 +0000] "GET /stream/hls/test_hi/index.m3u8 HTTP/1.1" 200 137 "http://localhost/" "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:77.0) Gecko/20100101 Firefox/77.0" 1
        Jun 22 09:27:20 9bda909079bd 172.19.0.4 - - [22/Jun/2020:09:27:19 +0000] "GET /stream/hls/test_audio/index.m3u8 HTTP/1.1" 200 138 "http://localhost/" "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:77.0) Gecko/20100101 Firefox/77.0" 1
        Jun 22 09:27:21 9bda909079bd 172.19.0.4 - - [22/Jun/2020:09:27:21 +0000] "GET /stream/hls/test_hi/5.ts HTTP/1.1" 200 1262796 "http://localhost/" "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:77.0) Gecko/20100101 Firefox/77.0" 1
        Jun 22 09:27:21 9bda909079bd 172.19.0.4 - - [22/Jun/2020:09:27:21 +0000] "GET /stream/hls/test_hi/6.ts HTTP/1.1" 200 931540 "http://localhost/" "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:77.0) Gecko/20100101 Firefox/77.0" 1
        """
        comp_hls = re.compile(r"^.* (\d\d\d\.\d\d\.\d\.\d) - - \[(.*)\] \"GET \/(.*)\/hls\/(.*_.*)\/(.*)\.ts HTTP\/1\.1\" (.*) (.*) \".*\" (.*)$")
        # Copy current syslog file to temp
        # This is to ensure that we don't block the file for system writing
        # Parse over time range, and add to DB
        for log_file in self._get_log_file_names():  
            with open(log_file, 'rb') as f:
                m = mmap.mmap(f.fileno(), 0, prot=mmap.PROT_READ)

                line = m.readline()
                while line:
                    res = comp_hls.match(line.decode("utf-8"))
                    if res:
                        # TODO: Ref proper groups
                        tup = (res.group(99), res.group(2), res.group(3))
                        self._insert_line(tup)

                    line = m.readline()

    def get_connections_per_stream(self) -> List[Tuple[int, str]]:
        # Open DB and parse per stream, returning connections per stream
        print("Inside get_connections_per_stream. Not implmenented...")

def parse_db(start_day, end_day):

    p = Parse(start_day, end_day)
    p.parse_log_to_db()
    return p.get_connections_per_stream()

if __name__ == "__main__":

    import sys 
    sys.argv = ['2020-06-27', '2020-06-27']

    parser = argparse.ArgumentParser()
    parser.add_argument("start_day", help='2020-06-22')
    parser.add_argument("end_day", nargs="?", help='2020-06-23')
    args = parser.parse_args()

    connections_per_stream  = parse_db(args.start_day, args.end_day)
    print(connections_per_stream)

