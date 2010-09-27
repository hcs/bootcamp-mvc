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
        return render_template({"title":"Index", "content": content})

    @cherrypy.expose
    def ps(self):
        procs = list_procs()
        d = {"title":"Running processes", "content": format_html_list(procs)}
        return render_template(d)

    @cherrypy.expose
    def hostname(self):
        hostname = socket.gethostname()
        return render_template({"title":"Hostname",
                                "content": html_escape(hostname)})

    @cherrypy.expose
    def schedule(self, classname=None):
        d = load_schedule()
        if classname is None:
            content = format_html_list([format_schedule_item(k,v)
                                        for k,v in d.iteritems()], False)
        else:
            content = (format_schedule_item(classname, d[classname])
                       if classname in d else "Could not find that class.")
        return render_template({"title":"Schedule", "content":content})
        

def list_procs():
    if os.name == 'nt':
        return list_procs_nt()
    return list_procs_nix()

def list_procs_nt():
    return []

def list_procs_nix():
    proc = subprocess.Popen(["/bin/ps", "-a"], stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
    out,_ = proc.communicate()
    return out.split("\n")[1:-1]

def html_escape(s):
    return s.replace("<","&lt;").replace(">","&gt;")

def safe_string_format(tmpl, args):
    return tmpl % tuple(map(html_escape, args))

def format_html_list(rg,safe=True):
    to_join = ["<ul>"]
    for ele in rg:
        to_fmt = html_escape(ele) if safe else ele
        to_join.append(" "*4 + "<li>%s</li>" % to_fmt)
    to_join.append("</ul>")
    return "\n".join(to_join)

def format_link(href, text):
    return safe_string_format('<a href="%s">%s</a>', (href,text))

def render_template(dictFields):
    required = ("title","content","footer",)
    for key in [key for key in required if key not in dictFields]:
        dictFields[key] = ""
    return TEMPLATE % dictFields

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
