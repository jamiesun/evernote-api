#!/usr/bin/env python

from bottle import post,route, run,request,response
import logging
import hashlib
import binascii
import evernote.edam.userstore.constants as UserStoreConstants
import evernote.edam.type.ttypes as Types
import evernote.edam.error.ttypes as Errors
import evernote.edam.notestore.NoteStore as NoteStore
from evernote.api.client import EvernoteClient,Store
import ConfigParser
import json,re

config = ConfigParser.ConfigParser()
config.read("app.conf")

def get_notestore():
    store = Store(config.get("main","evernote_token"), 
        NoteStore.Client, config.get("main","notestore_url"))
    if not store:  # Trick for PyDev code completion
        store = NoteStore.Client()
        raise Exception('Should never reach here')
    return store

def render_json(**tmp_vars):
    return json.dumps(tmp_vars, ensure_ascii=False)


def filterRes(src,thumb='720mark'):
    def _filter_img(value):
        imgs = re.findall('(http://www.comeonever.com/static/res/[a-zA-Z0-9]+.[a-zA-Z]{3})\s?', value)
        for img in imgs:
            value = value.replace(img, '<a href="' + img + '" target="_blank"><img src="' + img + '" /></a>')
        
        imgs = re.findall('(http://img.comeonever.com/comeonever/([a-zA-Z0-9]+/)?[a-zA-Z0-9]+.[a-zA-Z]{3})\s?', value)
        for img in imgs:
            value = value.replace(img[0], '<a href="' + img[0] + '" target="_blank"><img src="' + img[0] + '!'+ thumb +'"  /></a>')

        return value    
    value = _filter_img(src)
    return value.replace("\n","<br/>")      

@post('/evernote/note/create')
def evernote_create():
    note_store = get_notestore()

    reqdata = request.json

    title = reqdata.get("title")
    content = reqdata.get("content")

    note = Types.Note()
    note.notebookGuid = config.get("main","book_guid")
    note.title = title.encode("utf-8")
    note.content = '<?xml version="1.0" encoding="UTF-8"?>'
    note.content += '<!DOCTYPE en-note SYSTEM ' \
                    '"http://xml.evernote.com/pub/enml2.dtd">'
    note.content += '<en-note>'
    note.content +=  filterRes(content.encode("utf-8"))
    note.content += '</en-note>'
    response.set_header("Content-type", " application/json")
    created_note = note_store.createNote(note)
    return render_json(code=0,guid=created_note.guid)

@post('/evernote/note/update')
def evernote_update():
    note_store = get_notestore()

    reqdata = request.json

    guid = reqdata.get("guid")
    title = reqdata.get("title")
    content = reqdata.get("content")

    note = Types.Note()
    note.guid = guid
    note.notebookGuid = config.get("main","book_guid")
    note.title = title.encode("utf-8")
    note.content = '<?xml version="1.0" encoding="UTF-8"?>'
    note.content += '<!DOCTYPE en-note SYSTEM ' \
                    '"http://xml.evernote.com/pub/enml2.dtd">'
    note.content += '<en-note>'
    note.content +=  filterRes(content.encode("utf-8"))
    note.content += '</en-note>'
    response.set_header("Content-type", " application/json")
    created_note = note_store.updateNote(config.get("main","evernote_token"),note)
    return render_json(code=0,guid=created_note.guid)

@route("/books")
def books():
    note_store = get_notestore()
    books = note_store.listNotebooks()
    resp = ''
    for nb in books:
        resp += '%s : %s <br/>'%(nb.name,nb.guid)

    return resp



run(host='localhost', port=8080, debug=True)