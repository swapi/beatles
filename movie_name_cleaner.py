#!/usr/bin/python

import requests
import os
import simplejson
import sys

if len(sys.argv) == 2:
  ROOT = sys.argv[1]
else:
  print 'movie_name_cleaner.py <Location of Movies>'
  sys.exit(1);

ROOT = '/media/twotb/Movies/English/'
movies = os.listdir(ROOT)

arf = open('progress.txt','r')
try:
    already_read = arf.readlines()
    already_read = set(already_read)
finally:
    arf.close()

anf = open('no.txt','r')
try:
    already_no = anf.readlines()
    already_no = set(already_no)
finally:
    anf.close()

a404f = open('404.txt','r')
try:
    already_404 = a404f.readlines()
    already_404 = set(already_404)
finally:
    a404f.close()


def httpcall(m):
    print 'Doing http call for = ', m
    r = requests.get('http://mymovieapi.com/?title=' + m + '&type=json&plot=simple&episode=1&limit=1&yg=0&mt=none&lang=en-US&offset=&aka=simple&release=simple&business=0&tech=0')
    if r.ok:
        return (True, r.json)
    else:
        return (False, [])

arf = open('progress.txt', 'a')
anf = open('no.txt','a')
a404f = open('404.txt','a')
try:
    for m in movies:
        mp = str(ROOT + m + '\n')
        if mp in already_read or mp in already_no or mp in already_404:
            print 'Movie', m, 'is already scanned'
            continue
        if mp.endswith('imdb.txt\n'):
            continue
        r = httpcall(m)
        if r[0]:
            json = r[1]

            old_name = ROOT + m
            words = m.replace('.', ' ').replace('[', ' ').replace(']', ' ').replace('-', ' ').split(' ')
            if os.path.isfile(old_name):
                words = words[0:-1]
            tries = len(words) - 1
            found = True 
            while type(json) == dict and json.has_key('code') and str(json['code']) == '404':
                found = False
                if tries == 0:
                    break
                nn = ' '.join(words[0:tries])
                if words[tries - 1] == '':
                    tries -= 1
                    continue
                r = httpcall(nn)
                if r[0]:
                    found = True
                    json = r[1]
                else:
                    json = {'code': 404}
                tries -= 1
            if not found:
                a404f.write(old_name + '\n')
                print 'No result found for = ' + m
                continue
            json = json[0]
            title = json['title']
            rating = json['rating']
            year = json['year']

            new_name = ROOT + title + ' - ' + str(year) + ' (' + str(rating) + ')'

            if os.path.isfile(old_name):
                ext = old_name.split('.')[-1]
                new_name = new_name + '.' + ext

            if old_name != new_name:
                print 'Renaming', old_name, 'to', new_name
                r = raw_input('Proceed (Y/n/c): ')
                if r == '' or r == 'Y' or r == 'y':
                    os.rename(old_name, new_name)
                elif r == 'c' or r == 'C':
                    new_name = ROOT + raw_input('New name: ')
                    os.rename(old_name, new_name)
                else:
                    anf.write(old_name + '\n')
                    continue

                arf.write(new_name + '\n')

                json['oldfile'] = old_name
                if os.path.isfile(new_name):
                    df = open(new_name + '.imdb.txt', 'w')
                    simplejson.dump(json, df)
                    df.close()
                else:
                    df = open(new_name + '/imdb.txt', 'w')
                    simplejson.dump(json, df)
                    df.close()
finally:
    arf.close()
    anf.close()
    a404f.close()
