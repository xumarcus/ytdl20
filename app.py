import os
from flask import Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or '185946e8'

import dacite
import humanfriendly
import youtube_dl
from contextlib import suppress
from dataclasses import dataclass
from typing import List, Optional

from flask import request, send_file, render_template, redirect
from forms import SearchForm, StreamForm, DownloadForm, AUDIO_FORMATS, VIDEO_FORMATS

@dataclass
class Dash(object):
    filesize: Optional[int]
    format_id: str
    url: str

@dataclass
class Info(object):
    webpage_url: str
    title: str
    average_rating: float
    formats: List[Dash]    

    def __post_init__(self):
        self.stream_form = StreamForm()
        self.stream_form.stream_url.choices = [
            (dash.url, '%s (%s)' % (
                AUDIO_FORMATS[dash.format_id],
                humanfriendly.format_size(dash.filesize)))
            for dash in self.formats if dash.format_id in AUDIO_FORMATS
        ]
        self.download_form = DownloadForm()
        self.download_form.download_format.choices = [
            (dash.url, '%s (%s)' % (
                VIDEO_FORMATS[dash.format_id],
                humanfriendly.format_size(dash.filesize)))
            for dash in self.formats if dash.format_id in VIDEO_FORMATS
        ]

@app.route('/', methods=['GET', 'POST'])
def index():
    form = SearchForm(request.form)
    infos = list()
    if form.validate_on_submit():
        with youtube_dl.YoutubeDL() as ydl:
            def extract_info(url):
                with suppress(youtube_dl.DownloadError):
                    return dacite.from_dict(
                        data_class=Info,
                        data=ydl.extract_info(url, download=False)
                    )
            for url in form.urls.data.split():
                infos.append(extract_info(url))
    errors = form.errors.get('urls')
    if errors:
        return render_template('index.html', form=form, msg='\n'.join(errors))
    return render_template('index.html', form=form, infos=infos)

@app.route('/stream', methods=['POST'])
def stream():
    return redirect(request.form.get('stream_url') or '/')

@app.route('/download', methods=['POST'])
def download():
    form = DownloadForm(request.form)
    if form.validate_on_submit():
        config = {
            'format': '%s+bestaudio/best' % form.download_format.data,
            'outtmpl': '/tmp/%(format_id)s-%(id)s.%(ext)s',
            'merge_output_format': 'mkv'
        }
        with youtube_dl.YoutubeDL(config) as ydl:
            with suppress(youtube_dl.DownloadError):
                info = ydl.extract_info(form.download_url.data, download=True)
                filename = '/tmp/%(format_id)s-%(id)s.mkv' % info
                attachment_filename = '%(title)s.mkv' % info
                return send_file(
                    filename, 
                    as_attachment=True,
                    attachment_filename=attachment_filename
                )
    return redirect('/')
