    #!/usr/bin/env python2
    #
    # Proxy Google Search API
    # Generate List of hosts
    # for Nmap Scripting Engine
    #
    # Proxy file format:
    # http IP PORT
    # socks5 IP PORT
    # ...
    #
    # by tesla
    #
    import re
    import time
    import json
    import shlex
    import urllib
    import signal
    import os.path
    import argparse
    import subprocess
    import requesocks as requests
    parser = argparse.ArgumentParser(usage='python dorksNmap.py proxy_lst 3 0.5 "inurl:news.asp"'
    '8 12 target_out nmap_out',
    description='Proxy Google Search API : Generate File for NSE')
    parser.add_argument('proxies', type = str, help = 'Proxies list file')
    parser.add_argument('pause', type = int, help = 'Pause request (secs)')
    parser.add_argument('timeout', type = float, help = 'Timeout requests (secs)')
    parser.add_argument('dork', type = str, help = 'Dork query')
    parser.add_argument('rsz', type = int, help = 'Results per page (1-8)')
    parser.add_argument('start', type = int, help = 'Start index (0,4,8,12,16,...)')
    parser.add_argument('output', type = str, help = 'Target output file')
    parser.add_argument('noutput', type = str, help = 'Nmap output file')
    args = parser.parse_args()
    W = '\033[97m'
    N = '\033[0m'
    def signal_handler(signal, frame):
    print '' + W
    print 'Quitting..'
    print '' + N
    exit(0)
    signal.signal(signal.SIGINT, signal_handler)
    def getResults():
    list_url = []
    fin_url = []
    i = 0
    entry = 0
    query = urllib.urlencode({'q' : args.dork})
    # https://developers.google.com/errors/?csw=1
    # We received automated requests, such as scraping and prefetching.
    # Automated requests are prohibited; all requests must be made as a result of an end-user action.
    upath = 'http://ajax.googleapis.com/ajax/services/search/web?v=1.0'
    while entry <= args.start:
    y = 0
    var = []
    url = upath + '&%s' %query + '&rsz=%s' %args.rsz + '&start=%s' %entry
    print '' + W
    print(url) + N
    session = requests.session()
    with open(args.proxies) as line: fdata = line.readlines()
    for x in fdata: var.append(x.split(' '))
    while y < len(var):
    # To improve
    session.proxies = {'http':'%s://%s:%s' %(str(var[y][0]), str(var[y][1]), str(var[y][2]).replace('\n', ''))}
    try:
    response = session.get(url, timeout = args.timeout)
    results = response.text
    if response.status_code == 200:
    res = json.loads(results)
    data = res['responseData']['results']
    for z in data: list_url.append(z['url'])
    afile = open(args.output, 'a')
    while i < len(list_url):
    fin_url.append(((list_url[i])[7:].split('/'))[0])
    if(fin_url[i].strip() != ''):
    afile.write(fin_url[i]+'\n')
    print(str(session.proxies)[10:-2] + ' ' + fin_url[i])
    i += 1
    afile.close()
    break
    except requests.exceptions.ConnectionError as e:
    print(str(session.proxies)[10:-2] + ' ' + e.args[0].__doc__)
    #print(dir(e.args[0]))
    except requests.exceptions.Timeout as e:
    print(str(session.proxies)[10:-2] + ' ' + e.message)
    # Below except not checked yet
    except requests.exceptions.HTTPError as e:
    print(e)
    except requests.exceptions.TooManyRedirects as e:
    print(e)
    except requests.exceptions.RequestException as e:
    print(e)
    if(entry >= args.start): time.sleep(args.pause)
    y += 1
    entry += 4
    if(os.path.isfile(args.output)):
    # To improve
    cmd = "sudo nmap --script http-iis-webdav-vuln -p80,8080 -iL " + args.output + " -oX " + args.noutput
    nmap = shlex.split(cmd)
    subprocess.Popen(nmap).wait()
    getResults()
