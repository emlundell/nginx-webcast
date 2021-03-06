#!/usr/bin/env python3

"""
    Given a date range, find the number of connections per stream.

    The syslog file is parsed for some metadata and put into an sqlite3 memory DB. 
    Then this DB is queried and the connections per stream is deduced. 
    

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
import logging
import sys

log = logging.getLogger(__file__)
logging.basicConfig(
    level=logging.ERROR,
    format=f"{__file__} [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("/var/log/scripts.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

class Parse:

    def __init__(self, start_day: str, end_day: str):

        self.conn = sqlite3.connect(':memory:')
        self.log_file_path = "/var/log/syslog-ng/"

        self._create_db()

        self.all_days = self._fill_in_days(start_day, end_day)

    def _fill_in_days(self, start_day: str, end_day: str) -> List[str]:

        end_day = end_day or start_day

        start_day_dt = datetime.datetime.strptime(start_day, "%Y-%m-%d")
        end_day_dt = datetime.datetime.strptime(end_day, "%Y-%m-%d")

        if start_day_dt > end_day_dt:
            end_day_dt, start_day_dt = start_day_dt, end_day_dt

        delta = end_day_dt - start_day_dt
        dd = [start_day_dt + datetime.timedelta(days=x) for x in range(delta.days + 1)]
        days = [datetime.datetime.strftime(d, "%Y-%m-%d") for d in dd]
        log.debug(f"days filled in {days}")
        return days

    def _get_log_file_names(self) -> str:

        logfiles = []
        for date in self.all_days:
            if os.path.exists(f"{self.log_file_path}syslog-{date}.log"):
                logfiles.append(f"{self.log_file_path}syslog-{date}.log")
            elif os.path.exists(f"{self.log_file_path}syslog-{date}.log.zip"):
                logfiles.append(f"{self.log_file_path}syslog-{date}.log.zip")

        log.debug(f"Logs to be parsed: {logfiles}")
        return logfiles

    def _create_db(self):
        try:
            with self.conn:
                self.conn.execute("CREATE TABLE stream (inserted timestamp, ip text, stream text, conn int)")
                log.debug("Table stream created.")
        except:
            log.debug("Table stream already exists. Skipping creation...")

    def _insert_line(self, values: Tuple):
        with self.conn:
            self.conn.execute("INSERT INTO stream VALUES (?,?,?,?)", values)
    
    def _get_num_unique_ip_per_minute(self):
        with self.conn:
            res = self.conn.execute("SELECT COUNT(DISTINCT ip), strftime('%Y-%m-%d %H:%M', inserted) FROM stream GROUP BY strftime('%Y-%m-%d %H:%M', inserted)")
            return res.fetchall()

    def parse_log_to_db(self):
        comp_hls = re.compile(r"^.* (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) - - \[(.*)\] \"GET \/.*\/hls\/(.*_.*)\/(.*)\.ts HTTP\/1\.1\" (\d\d\d) (\d*) \".*\" (.*) \"(.*)\"$")
        comp_dash = re.compile(r"^.* (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) - - \[(.*)\] \"GET \/.*\/dash\/(.*)\/(.*)\.m4a HTTP\/1\.1\" (\d\d\d) (\d*) \".*\" (.*) \"(.*)\"$")
       
        # Copy current syslog file to temp
        # This is to ensure that we don't block the file for system writing
        # Parse over time range, and add to DB
        for log_file in self._get_log_file_names():  
            with open(log_file, 'rb') as f:
                m = mmap.mmap(f.fileno(), 0, prot=mmap.PROT_READ)

                line = m.readline()
                while line:
                    res_hls = comp_hls.match(line.decode("utf-8"))
                    if res_hls:
                        # Ref proper groups
                        # 1: container ip, 2: stream datetime, 3: stream name, 4: fragment number, 5: http code, 6: bytes, 7: connection number, 8: forward ip
                        timestamp = datetime.datetime.strptime(res_hls.group(2), '%d/%b/%Y:%H:%M:%S +0000')
                        tup = (
                            timestamp, 
                            res_hls.group(8), 
                            res_hls.group(3),
                            res_hls.group(7) 
                            )
                        self._insert_line(tup)

                    res_dash = comp_dash.match(line.decode("utf-8"))
                    if res_dash:
                        # Ref proper groups
                        # 1: container ip, 2: stream datetime, 3: stream name, 4: fragment number, 5: http code, 6: bytes, 7: connection number, 8: forward ip
                        timestamp = datetime.datetime.strptime(res_dash.group(2), '%d/%b/%Y:%H:%M:%S +0000')
                        tup = (
                            timestamp, 
                            res_dash.group(8), 
                            res_dash.group(3),
                            res_dash.group(7) 
                            )
                        self._insert_line(tup)

                    line = m.readline()

    def get_connections_per_stream(self) -> List[Tuple[int, str]]:
        # Open DB and parse per stream, returning connections per stream
        if log.isEnabledFor(logging.DEBUG):        
            with self.conn:
                for row in self.conn.execute("SELECT * FROM stream"):
                    log.debug(row)

        return self._get_num_unique_ip_per_minute()

def parse_db(start_day, end_day, log_level='error'):
    if log_level == 'debug':
        log.setLevel(logging.DEBUG)
    elif log_level == 'info':
        log.setLevel(logging.INFO)
    
    p = Parse(start_day, end_day)
    p.parse_log_to_db()
    c = p.get_connections_per_stream()
    log.info(c)
    return c 

if __name__ == "__main__":

    right_now = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d")

    parser = argparse.ArgumentParser()
    parser.add_argument("start_day", nargs="?", default=right_now, help='2020-06-22')
    parser.add_argument("end_day", nargs="?", help='2020-06-23')
    parser.add_argument("--log-level", dest="log_level")
    args = parser.parse_args()

    parse_db(args.start_day, args.end_day, args.log_level)
