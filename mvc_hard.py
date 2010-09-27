#!/usr/bin/env python

import csv
import os
import socket
import subprocess

import cherrypy

TEMPLATE = """
<html>
<head>
<title>%(title)s</title>
<style>
  body > div.main {
    width: 800px;
    margin-left: auto;
    margin-right: auto;
  }
</style>
</head>
<body>
  <div class="main">
    <h2>%(title)s</h2>
    <div class="content">
    %(content)s
    </div>
    <div class="footer">
    %(footer)s
    </div>
  </div>
</body>
</html>
"""

SCHEDULE = "schedule.csv"

class ProcReporter(object):
    @cherrypy.expose
    def index(self):
        banned = ("index", "favicon_ico")
        def is_exposed(name):
            member = getattr(self,name)
            return (callable(member) and hasattr(member,"exposed")
                    and getattr(member,"exposed") and name not in banned)
        links = []
        for name in dir(self):
            if is_exposed(name):
                links.append(name)
        content = "<br/>".join([format_link(l,l) for l in links])
        return ("<html><head><title>Index</title><head><body><h2>Index</h2>"
                "%s</body></html>"
                % content)

    @cherrypy.expose
    def ps(self):
        # get a list of the running processes (examine the rest of the code),
        # format it into HTML, and display it.
        return "Implement me (ps)"

    @cherrypy.expose
    def hostname(self):
        # get the hostname somehow, and pass it to the template rendering
        # function.
        return "Implement me (hostname)"

    @cherrypy.expose
    def schedule(self, classname=None):
        # Display the schedule in an unordered list or in a table.
        # If classname is none, display everything. If the classname is
        # specified, only display the specified class.
        return "Implement me (schedule)"
        

def list_procs():
    if os.name == 'nt':
        return list_procs_nt()
    return list_procs_nix()

def list_procs_nt():
    get_list_from_procs(["tasklist"])

def list_procs_nix():
    get_list_from_proc(["/bin/ps", "-a"])

def get_list_from_proc(args):
    proc = subprocess.Popen(args, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
    out,_ = proc.communicate()
    return out.split("\n")[1:-1]

def html_escape(s):
    return s.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")

def safe_string_format(tmpl, args):
    return tmpl % tuple(map(html_escape, args))

def format_html_list(rg,safe=True):
    # convert a list of strings to HTML markup for an unordered list (ul).
    # if safe is true, the contents of the list items must be html escaped.
    return "Implement me (format_html_list)!"

def format_link(href, text):
    return safe_string_format('<a href="%s">%s</a>', (href,text))

def render_template(dictFields):
    required = ("title","content","footer",)
    # Fill in the values in the TEMPLATE string using the values in dictFields.
    # If no value is found in the dictionary, use the empty string.
    return None

# CSV-related functions

def load_schedule(fname=SCHEDULE):
    infile = open(fname)
    rdr = csv.reader(infile)
    d = {}
    for row in rdr:
        if row:
            d[row[0]] = row[1:]
    infile.close()
    return d

def format_schedule_item(name,schedule_properties):
    full_name,time = schedule_properties
    return format_link("/schedule/%s" % name,
                       "%s (%s) meets at %s" % (full_name, name.upper(), time))

if __name__ == "__main__":
    cherrypy.quickstart(ProcReporter())
