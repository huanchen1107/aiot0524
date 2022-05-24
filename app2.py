from flask import Flask, render_template, jsonify
import pandas as pd
from six.moves import urllib
import json

app = Flask(__name__)
@app.route("/")