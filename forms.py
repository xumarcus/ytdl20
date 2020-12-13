import re
from flask_wtf import FlaskForm
from wtforms import TextAreaField, SelectField, SubmitField, StringField
from wtforms.validators import ValidationError, DataRequired, Length

# AgentOak/youtube_formats.md
AUDIO_FORMATS = {
    '139': 'm4a AAC 48Kbps Stereo',
    '140': 'm4a AAC 128Kbps Stereo',
    '249': 'webm (Audio) Opus 50Kbps Stereo',
    '250': 'webm (Audio) Opus 70Kbps Stereo',
    '251': 'webm (Audio) Opus 160Kbps Stereo',
    '256': 'm4a AAC 192Kbps Surround',
    '258': 'm4a AAC 384Kbps Surround',
}

VIDEO_FORMATS = {
    '160': 'mp4 H.264 144p',
    '133': 'mp4 H.264 240p',
    '134': 'mp4 H.264 360p',
    '135': 'mp4 H.264 480p',
    '136': 'mp4 H.264 720p',
    '137': 'mp4 H.264 1080p',
    '298': 'mp4 H.264 HFR 720p',
    '299': 'mp4 H.264 HFR 1080p',
    '278': 'webm VP9 144p',
    '242': 'webm VP9 240p',
    '243': 'webm VP9 360p',
    '244': 'webm VP9 480p',
    '247': 'webm VP9 720p',
    '302': 'webm VP9 HFR 720p',
    '303': 'webm VP9 HFR 1080p',
    '308': 'webm VP9 HFR 1440p',
    '315': 'webm VP9 HFR 2160p',
    '330': 'webm VP9.2 HDR HFR 144p',
    '331': 'webm VP9.2 HDR HFR 240p',
    '332': 'webm VP9.2 HDR HFR 360p',
    '333': 'webm VP9.2 HDR HFR 480p',
    '334': 'webm VP9.2 HDR HFR 720p',
    '335': 'webm VP9.2 HDR HFR 1080p',
    '336': 'webm VP9.2 HDR HFR 1440p',
    '337': 'webm VP9.2 HDR HFR 2160p',
    '394': 'mp4 AV1 144p',
    '395': 'mp4 AV1 240p',
    '396': 'mp4 AV1 360p',
    '397': 'mp4 AV1 480p',
    '398': 'mp4 AV1 HFR 720p',
    '399': 'mp4 AV1 HFR 1080p',
    '400': 'mp4 AV1 HFR 1440p',
    '401': 'mp4 AV1 HFR 2160p',
    '402': 'mp4 AV1 HFR 4320p',
}

class URLsAllValid(object):
    def __init__(self, *args, **kwargs):
        self.regex = re.compile(r'^(.+?)(\/)(watch\x3Fv=)?(embed\/watch\x3Ffeature\=player_embedded\x26v=)?([a-zA-Z0-9_-]{11})$')
    
    def __call__(self, form, field, message=None):
        assert(isinstance(field.data, str))
        if any(map(lambda string: self.regex.match(string) is None, field.data.split())):
            raise ValidationError(message or 'One or more URLs are invalid')

VALIDATE_URL = [DataRequired(), Length(max=1024), URLsAllValid()]

class IsGoogleVideoURL(object):
    def __init__(self, *args, **kwargs):
        self.regex = re.compile(r'^https\:\/\/[^\.]*\.googlevideo\.com\/videoplayback[^\/]*$')

    def __call__(self, form, field, message=None):
        assert(isinstance(field.data, str))
        if self.regex.match(field.data) is None:
            raise ValidationError(message or 'Stream URL is invalid')

class SearchForm(FlaskForm):
    urls = TextAreaField('URLs', validators=VALIDATE_URL)
    subm = SubmitField('Submit')

class StreamForm(FlaskForm):
    stream_url = SelectField('Stream URL', validators=[IsGoogleVideoURL()])
    subm = SubmitField('Stream')

class DownloadForm(FlaskForm):
    download_url = StringField('Download URL', validators=VALIDATE_URL)
    download_format = SelectField('Download Format',
        choices=(*AUDIO_FORMATS.keys(), *VIDEO_FORMATS.keys()))
    subm = SubmitField('Download')
