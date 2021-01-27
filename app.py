import streamlit as st
import plotly.express as px
import numpy as np

import requests
from lxml import etree

import json

from streamlit_echarts import st_echarts

# getting perm levels
url = "https://developer.android.com/reference/android/Manifest.permission#constants_1"

req = requests.get(url)
lxml = etree.HTML(req.text)


def protection(line):
    if line.startswith("Protection level: "):
        return True
    else:
        return False


def constant(line):
    if line.startswith("Constant Value:"):
        return True
    else:
        return False


data = lxml.xpath("//*[@id=\"jd-content\"]/div/p/text()")

perm_levels = {}


for lp, lc in zip(filter(protection, data), filter(constant, data)):
    permission = lc.split("\"")[-2].split(".")[-1]
    level = lp.strip("\n ").split("Protection level: ")[1].split("|")[0]

    perm_levels[permission] = level

# print(perm_levels)


# Getting data and analyzing it

path = "Top25Global.json"

with open(path) as fp:
    data = json.load(fp)


orgArr = {}

for i in data:
    org = i
    org_levels = {}

    orgArr[i] = {}

    # per item per org
    for j in data[org]:

        # item has a severity level defined
        if (j in perm_levels):
            level = perm_levels[j]

            # if level already there for this org
            if (level in orgArr[org]):
                orgArr[org][level] += 1
            else:
                orgArr[org][level] = 1

pieArr = {}

for i in orgArr:
    pieArr[i] = []

    for j in orgArr[i]:
        pieArr[i].append({"value": orgArr[i][j], "name": j})


def createPie(org):
    pie_options = {
            "backgroundColor": "#2c343c",
            "title": {
                "text": "Distribution in levels of permissions",
                "left": "center",
                "top": 20,
                "textStyle": {"color": "#ccc"},
            },
            "tooltip": {"trigger": "item", "formatter": "{a} <br/>{b} : {c} ({d}%)"},
            "visualMap": {
                "show": True,
                "min": -5,
                "max": 10,
                # "inRange": {"colorLightness": [0, 1]},
            },
            "series": [
                {
                    "name": "Distribution in levels of permissions",
                    "type": "pie",
                    "radius": "55%",
                    "center": ["50%", "50%"],
                    "data": pieArr[org],
                    # "roseType": "radius",
                    "label": {"color": "rgba(255, 255, 255, 0.3)"},
                    "labelLine": {
                        "lineStyle": {"color": "rgba(255, 255, 255, 0.3)"},
                        "smooth": 0.2,
                        "length": 10,
                        "length2": 20,
                    },
                    "itemStyle": {
                        "color": "#c23531",
                        "shadowBlur": 200,
                        "shadowColor": "rgba(0, 0, 0, 0.5)",
                    },
                    "animationType": "scale",
                    "animationEasing": "elasticOut",
                }
            ],
        }
    st_echarts(options=pie_options, key=org)


orgs = []

for i in orgArr:
    orgs.append(i)

orgs = tuple(orgs)

org = st.selectbox(
    'Organization: ',
    orgs
)

createPie(org)
